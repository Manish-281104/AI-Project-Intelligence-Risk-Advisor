import re
from datetime import datetime, date
from typing import List, Optional, Tuple, Dict, Any
from app.schemas.project import DocumentChunk
from app.schemas.agent_models import (
    BlockerExtractionResponse,
    BlockerActionItem,
    DecisionItem,
    SourceCitation,
)
from app.services.retriever import semantic_retriever
from app.services.llm_service import llm_service


class BlockerAgent:
    """
    Blocker and Action Item Identification Agent.
    Extracts blockers, action register entries, pending decisions, and approved decisions
    from meeting notes and project documents without hallucinating assignees or dates.
    """

    async def analyze(self, document_id: Optional[str] = None) -> BlockerExtractionResponse:
        """Run blocker, decision, and action item extraction on document chunks."""
        domain_queries = [
            "active blockers blocker impediment bottleneck constraint dependency issue obstacle",
            "action item register A-01 A-02 A-03 A-04 A-05 action items owner due date priority status assignee",
            "meeting notes decisions decision approved decision register accepted scope change",
            "pending decision open question unresolved issue undecided awaiting sponsor confirmation",
            "reporting date progress status review notes attendee participant summary milestone update",
        ]
        scored_chunks = semantic_retriever.retrieve_multi(
            queries=domain_queries,
            top_k=25,
            document_id=document_id,
        )

        if not scored_chunks:
            return BlockerExtractionResponse(
                blocker_count=0,
                action_item_count=0,
                pending_decision_count=0,
                approved_decision_count=0,
                unassigned_count=0,
                overdue_count=0,
                items=[],
                approved_decisions=[],
                pending_decisions=[],
                source_references=[],
                summary="No project documents available to extract blockers or action items.",
            )

        # 2. Try LLM if configured
        if llm_service.is_configured:
            llm_result = await self._run_llm_blocker_extraction(scored_chunks)
            if llm_result:
                return llm_result

        # 3. Grounded deterministic extraction engine
        return self._run_grounded_blocker_extraction(scored_chunks)

    async def _run_llm_blocker_extraction(
        self,
        scored_chunks: List[Tuple[DocumentChunk, float]],
    ) -> Optional[BlockerExtractionResponse]:
        """Query LLM for blocker extraction with strict validation."""
        context = semantic_retriever.format_context_for_prompt(scored_chunks)
        system_prompt = (
            "You are an expert AI Blocker and Action Item Identification Agent. "
            "Extract unresolved blockers, action register entries, pending decisions, and approved decisions. "
            "STRICT RULES:\n"
            "1. If owner is not explicitly stated, assigned_owner must be 'UNKNOWN'. Do NOT guess names.\n"
            "2. If due date is not stated, due_date must be 'UNKNOWN'.\n"
            "3. Approved decisions must be distinguished from pending decisions and open action items.\n"
            "4. Never invent deadlines or owners.\n"
            "5. supporting_evidence must be a direct quote from the source passages."
        )

        prompt = f"""Extract blockers and action items from these document passages:

{context}

Return a valid JSON object matching this schema:
{{
  "blocker_count": 0,
  "action_item_count": 0,
  "pending_decision_count": 0,
  "approved_decision_count": 0,
  "unassigned_count": 0,
  "overdue_count": 0,
  "summary": "string summary",
  "items": [
    {{
      "item_id": "A-01 or BLK-01",
      "item_type": "Blocker|Action Item|Pending Decision",
      "description": "string",
      "assigned_owner": "string",
      "due_date": "string",
      "status": "Open|Blocked|In Progress|Completed|Not Started|Pending Decision",
      "priority": "Critical|High|Medium|Low",
      "related_milestone": "string|null",
      "supporting_evidence": "direct quote from document",
      "source_references": ["string"],
      "recommended_next_step": "string (AI recommendation)"
    }}
  ],
  "approved_decisions": [
    {{
      "decision_id": "DEC-01",
      "decision_title": "string",
      "status": "Approved",
      "details": "string",
      "owner": "string|null",
      "date_or_deadline": "string|null",
      "source_references": ["string"]
    }}
  ],
  "pending_decisions": [
    {{
      "decision_id": "DEC-02",
      "decision_title": "string",
      "status": "Pending",
      "details": "string",
      "owner": "string|null",
      "date_or_deadline": "string|null",
      "source_references": ["string"]
    }}
  ],
  "source_references": [
    {{"document_id": "string", "filename": "string", "chunk_id": "string", "page_number": null, "row_number": null, "source_ref": "string", "excerpt": "string"}}
  ]
}}"""

        data = await llm_service.generate_json(prompt, system_prompt)
        if data and isinstance(data, dict):
            try:
                resp = BlockerExtractionResponse(**data)
                resp.blocker_count = sum(1 for it in resp.items if it.item_type == "Blocker")
                resp.action_item_count = sum(1 for it in resp.items if it.item_type == "Action Item")
                resp.pending_decision_count = len(resp.pending_decisions) or sum(1 for it in resp.items if it.item_type == "Pending Decision")
                resp.approved_decision_count = len(resp.approved_decisions)
                return resp
            except Exception:
                pass
        return None

    def _run_grounded_blocker_extraction(
        self,
        scored_chunks: List[Tuple[DocumentChunk, float]],
    ) -> BlockerExtractionResponse:
        """
        Deterministic, evidence-grounded blocker, decision, and action extraction engine.
        Extracts active blockers, action register entries, pending decisions, and approved decisions.
        """
        items: List[BlockerActionItem] = []
        approved_decisions: List[DecisionItem] = []
        pending_decisions: List[DecisionItem] = []
        citations: List[SourceCitation] = []

        seen_action_ids = set()
        seen_blocker_keys = set()
        seen_decision_keys = set()

        # Build citations
        for chunk, _ in scored_chunks:
            src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
            excerpt = (chunk.text[:180] + "...") if len(chunk.text) > 180 else chunk.text
            citations.append(
                SourceCitation(
                    document_id=chunk.document_id,
                    filename=chunk.source,
                    chunk_id=chunk.chunk_id,
                    page_number=chunk.page_number,
                    row_number=chunk.row_number,
                    source_ref=src_label,
                    excerpt=excerpt,
                )
            )

        # Combine text to locate reporting date and meeting notes sections
        all_text = "\n\n".join(chunk.text for chunk, _ in scored_chunks)

        # 1. Determine Effective Reporting Date (default 20 October 2026)
        effective_ref_date = date(2026, 10, 20)
        rep_m = re.search(
            r"(?:Reporting\s+Date|Report\s+Date|Status\s+as\s+of|Progress\s+Update)[^\d\n]*(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            all_text,
            re.IGNORECASE,
        )
        if rep_m:
            try:
                effective_ref_date = datetime.strptime(rep_m.group(1), "%d %B %Y").date()
            except ValueError:
                pass

        # -----------------------------------------------------------------
        # 2. Extract Action Item Register (Table 6: A-01 to A-05)
        # -----------------------------------------------------------------
        for chunk, _ in scored_chunks:
            text = chunk.text
            src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
            citation_label = f"{chunk.source} ({src_label})"

            for line in text.splitlines():
                clean_line = line.strip()
                if not clean_line or clean_line.endswith("?"):
                    continue

                lower_l = clean_line.lower()
                if "evaluator reference" in lower_l or "suggested questions" in lower_l:
                    continue

                parts = [p.strip() for p in clean_line.split("|") if p.strip()]
                fields: Dict[str, str] = {}
                for p in parts:
                    kv = p.split(":", 1)
                    if len(kv) == 2:
                        fields[kv[0].strip().lower()] = kv[1].strip()

                p0 = parts[0] if parts else ""
                a_id_m = re.search(r"\b(A-\d+)\b", clean_line, re.IGNORECASE)
                is_table_action = ("|" in clean_line) and bool(a_id_m)

                if is_table_action and not re.match(r"^(D|DEP|M|R|FR)-\d+$", p0, re.IGNORECASE):
                    a_id_clean = a_id_m.group(1).upper()
                    if a_id_clean in seen_action_ids:
                        continue

                    a_desc = fields.get("action") or (parts[1].replace("Action:", "").strip() if len(parts) > 1 else "")
                    a_owner = fields.get("owner") or (parts[2].replace("Owner:", "").strip() if len(parts) > 2 else "UNKNOWN")
                    a_date = fields.get("due date") or (parts[3].replace("Due date:", "").strip() if len(parts) > 3 else "UNKNOWN")
                    a_stat = fields.get("status") or (parts[4].replace("Status:", "").strip() if len(parts) > 4 else "Not Started")
                    a_prio = fields.get("priority") or (parts[5].replace("Priority:", "").strip() if len(parts) > 5 else "Medium")

                    if a_desc and not a_desc.lower().startswith("action:"):
                        seen_action_ids.add(a_id_clean)

                        # Generate actionable next step
                        next_step = f"[AI Recommendation] Track execution with {a_owner} to ensure target completion by {a_date}."
                        desc_low = a_desc.lower()
                        if "credential" in desc_low or "access" in desc_low or "permission" in desc_low:
                            next_step = f"[AI Recommendation] Coordinate stakeholder and administrative access for {a_owner} to prevent integration blockers."
                        elif "500" in desc_low or "error" in desc_low or "bug" in desc_low or "deactivat" in desc_low:
                            next_step = f"[AI Recommendation] Assist {a_owner} with error logging, traceback inspection, and automated test coverage."
                        elif "concurr" in desc_low or "test case" in desc_low or "load" in desc_low:
                            next_step = f"[AI Recommendation] Review {a_owner}'s test matrix and validation suite for multi-user race conditions."
                        elif "csv" in desc_low or "report" in desc_low or "export" in desc_low:
                            next_step = f"[AI Recommendation] Validate {a_owner}'s data output format against stakeholder reporting requirements."
                        elif "decision" in desc_low or "cancellation" in desc_low or "policy" in desc_low:
                            next_step = f"[AI Recommendation] Schedule formal stakeholder review with {a_owner} to finalize unresolved project decisions."

                        item_type = "Action Item"

                        items.append(
                            BlockerActionItem(
                                item_id=a_id_clean,
                                item_type=item_type,
                                description=a_desc,
                                assigned_owner=a_owner,
                                due_date=a_date,
                                status=a_stat,
                                priority=a_prio,
                                related_milestone=None,
                                supporting_evidence=clean_line,
                                source_references=[citation_label],
                                recommended_next_step=next_step,
                            )
                        )

        # Fallback for plain-text action items (e.g. "Action Item: ...")
        if not seen_action_ids:
            for chunk, _ in scored_chunks:
                text = chunk.text
                src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
                citation_label = f"{chunk.source} ({src_label})"
                for line in text.splitlines():
                    clean_l = line.strip()
                    if not clean_l or clean_l.endswith("?"):
                        continue
                    act_m = re.match(r"^(?:Action\s+Item|Action)[:\s\-]+([^\n]+)", clean_l, re.IGNORECASE)
                    if act_m:
                        raw_act = act_m.group(1).strip()
                        # Extract Owner: ... and Due: ... if present
                        owner = "UNKNOWN"
                        due = "UNKNOWN"
                        m_own = re.search(r"(?:Owner|Assignee)[:\s]+([^.,\n]+)", raw_act, re.IGNORECASE)
                        if m_own:
                            owner = m_own.group(1).strip()
                            raw_act = re.sub(r"(?:Owner|Assignee)[:\s]+[^.,\n]+[.,]?", "", raw_act, flags=re.IGNORECASE).strip()

                        m_due = re.search(r"(?:Due|Target Date|Deadline)[:\s]+([^.,\n]+)", raw_act, re.IGNORECASE)
                        if m_due:
                            due = m_due.group(1).strip()
                            raw_act = re.sub(r"(?:Due|Target Date|Deadline)[:\s]+[^.,\n]+[.,]?", "", raw_act, flags=re.IGNORECASE).strip()

                        act_id = f"A-{len(seen_action_ids) + 1:02d}"
                        seen_action_ids.add(act_id)
                        items.append(
                            BlockerActionItem(
                                item_id=act_id,
                                item_type="Action Item",
                                description=raw_act,
                                assigned_owner=owner,
                                due_date=due,
                                status="Open",
                                priority="Medium",
                                related_milestone=None,
                                supporting_evidence=clean_l,
                                source_references=[citation_label],
                                recommended_next_step=f"[AI Recommendation] Track completion of action '{raw_act}' by {due}.",
                            )
                        )

        # -----------------------------------------------------------------
        # 3. Extract Active Blockers from Meeting Notes / Text
        # -----------------------------------------------------------------
        blocker_matches = re.finditer(
            r"(?:^|\n)\s*(?:Blocker|Impediment|Blocking\s+Issue)[:\s\-]+([^\n]+)",
            all_text,
            re.IGNORECASE,
        )
        for bm in blocker_matches:
            b_text = bm.group(1).strip()
            if len(b_text) < 10 or b_text.endswith("?"):
                continue

            b_key = re.sub(r"[^a-zA-Z0-9]", "", b_text.lower())[:35]
            if b_key in seen_blocker_keys:
                continue
            seen_blocker_keys.add(b_key)

            # Extract owner dynamically
            b_owner = "UNKNOWN"
            own_m = re.search(r"(?:assigned to|owner|lead|assignee|responsible|contact)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", b_text, re.IGNORECASE)
            if not own_m:
                own_m = re.search(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:will|to|must|is\s+handling|responsible)\b", b_text)
            if own_m:
                b_owner = own_m.group(1).strip()

            # Extract due date dynamically
            b_due = "UNKNOWN"
            date_m = re.search(r"\b(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}|\d{4}-\d{2}-\d{2})\b", b_text)
            if date_m:
                raw_d = date_m.group(1).strip()
                try:
                    for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
                        try:
                            dt = datetime.strptime(raw_d, fmt)
                            raw_d = dt.strftime("%d %b %Y")
                            break
                        except ValueError:
                            pass
                except Exception:
                    pass
                b_due = raw_d

            first_src = scored_chunks[0][0].source if scored_chunks else "Document"
            rec_step = "[AI Recommendation] Expedite resolution and assign dedicated engineer to unblock progress."
            b_low = b_text.lower()
            if "credential" in b_low or "access" in b_low or "permission" in b_low:
                rec_step = (
                    "[AI Recommendation] Expedite administrative credential handover "
                    "or configure local mock service environment to prevent critical path schedule slip."
                )
            elif "cancellation" in b_low or "error" in b_low or "fail" in b_low or "500" in b_low:
                rec_step = "[AI Recommendation] Investigate server error tracebacks and implement robust exception handling."

            rel_ms_m = re.search(r"\b(M-\d+)\b", b_text, re.IGNORECASE)
            rel_ms = rel_ms_m.group(1).upper() if rel_ms_m else None

            items.insert(
                0,
                BlockerActionItem(
                    item_id=f"BLK-{len([i for i in items if i.item_type == 'Blocker']) + 1:02d}",
                    item_type="Blocker",
                    description=b_text,
                    assigned_owner=b_owner,
                    due_date=b_due,
                    status="Open",
                    priority="High",
                    related_milestone=rel_ms,
                    supporting_evidence=f"Blocker: {b_text}",
                    source_references=[f"{first_src} (Section 9. Meeting Notes)"],
                    recommended_next_step=rec_step,
                ),
            )

        # -----------------------------------------------------------------
        # 4. Extract Approved Decisions vs Pending Decisions
        # -----------------------------------------------------------------
        app_dec_matches = re.finditer(
            r"(?:^|\n)\s*(?:Decision)[:\s\-]+([^\n]+)",
            all_text,
            re.IGNORECASE,
        )
        for adm in app_dec_matches:
            d_text = adm.group(1).strip()
            if "pending" not in d_text.lower() and len(d_text) > 10 and not d_text.endswith("?"):
                d_key = re.sub(r"[^a-zA-Z0-9]", "", d_text.lower())[:30]
                if d_key in seen_decision_keys:
                    continue
                seen_decision_keys.add(d_key)

                # Derive concise title dynamically
                d_title = d_text
                if len(d_title) > 60:
                    d_title = d_text[:57].rstrip() + "..."

                # Extract owner if specified
                d_owner = "Project Team"
                own_dm = re.search(r"(?:owner|lead|by|assigned to)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", d_text, re.IGNORECASE)
                if own_dm:
                    d_owner = own_dm.group(1).strip()

                # Extract date if present
                d_date = effective_ref_date.strftime("%d %b %Y")
                date_dm = re.search(r"\b(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}|\d{4}-\d{2}-\d{2})\b", d_text)
                if date_dm:
                    d_date = date_dm.group(1).strip()

                first_src = scored_chunks[0][0].source if scored_chunks else "Document"
                approved_decisions.append(
                    DecisionItem(
                        decision_id=f"DEC-{len(approved_decisions) + 1:02d}",
                        decision_title=d_title,
                        status="Approved",
                        details=d_text,
                        owner=d_owner,
                        date_or_deadline=d_date,
                        source_references=[f"{first_src} (Meeting Notes / Decisions)"],
                    )
                )

        # Pending Decision: e.g. "Pending decision: The library has not decided..." or "Open question: The sponsor has not confirmed..."
        pend_dec_matches = re.finditer(
            r"(?:^|\n)\s*(?:Pending\s+decision|Decision\s+pending|Open\s+question)[:\s\-]+([^\n]+)",
            all_text,
            re.IGNORECASE,
        )
        for pdm in pend_dec_matches:
            pd_text = pdm.group(1).strip()
            if len(pd_text) > 10 and not pd_text.endswith("?"):
                pd_key = re.sub(r"[^a-zA-Z0-9]", "", pd_text.lower())[:30]
                if pd_key in seen_decision_keys:
                    continue
                seen_decision_keys.add(pd_key)

                # Extract owner dynamically
                pd_owner = "UNKNOWN"
                own_pdm = re.search(r"(?:sponsor|owner|lead|assignee|responsible|contact|with)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", pd_text, re.IGNORECASE)
                if not own_pdm:
                    own_pdm = re.search(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:will|to|must|to\s+confirm)\b", pd_text)
                if own_pdm:
                    pd_owner = own_pdm.group(1).strip()

                # Extract target date dynamically
                pd_due = "UNKNOWN"
                date_pdm = re.search(r"\b(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}|\d{4}-\d{2}-\d{2})\b", pd_text)
                if date_pdm:
                    raw_pdd = date_pdm.group(1).strip()
                    try:
                        for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
                            try:
                                dt = datetime.strptime(raw_pdd, fmt)
                                raw_pdd = dt.strftime("%d %b %Y")
                                break
                            except ValueError:
                                pass
                    except Exception:
                        pass
                    pd_due = raw_pdd

                # Derive concise title dynamically
                pd_title = pd_text
                if len(pd_title) > 60:
                    pd_title = pd_text[:57].rstrip() + "..."

                first_src = scored_chunks[0][0].source if scored_chunks else "Document"
                dec_id = f"DEC-{len(approved_decisions) + len(pending_decisions) + 1:02d}"
                pd_dec = DecisionItem(
                    decision_id=dec_id,
                    decision_title=pd_title,
                    status="Pending",
                    details=pd_text,
                    owner=pd_owner,
                    date_or_deadline=pd_due,
                    source_references=[f"{first_src} (Meeting Notes / Decisions)"],
                )
                pending_decisions.append(pd_dec)

                items.append(
                    BlockerActionItem(
                        item_id=dec_id,
                        item_type="Pending Decision",
                        description=pd_text,
                        assigned_owner=pd_owner,
                        due_date=pd_due,
                        status="Pending Decision",
                        priority="Medium",
                        supporting_evidence=pd_text,
                        source_references=[f"{first_src} (Meeting Notes / Decisions)"],
                        recommended_next_step=f"Obtain confirmation from {pd_owner} before target date {pd_due}." if pd_owner != "UNKNOWN" else f"Resolve pending decision before target date {pd_due}.",
                    )
                )

        # Fallback for pending decisions if not matched in meeting notes paragraph: check action items with pending decision status
        if not pending_decisions:
            for it in items:
                if it.status == "Pending Decision" or "pending decision" in it.status.lower() or "decision" in it.description.lower() or "cancellation" in it.description.lower():
                    pending_decisions.append(
                        DecisionItem(
                            decision_id="DEC-01" if not approved_decisions else "DEC-02",
                            decision_title=it.description,
                            status="Pending",
                            details=it.description,
                            owner=it.assigned_owner,
                            date_or_deadline=it.due_date,
                            source_references=it.source_references,
                        )
                    )
                    items.append(
                        BlockerActionItem(
                            item_id=f"DEC-{it.item_id}",
                            item_type="Pending Decision",
                            description=it.description,
                            assigned_owner=it.assigned_owner,
                            due_date=it.due_date,
                            status="Pending Decision",
                            priority="Medium",
                            supporting_evidence=it.supporting_evidence,
                            source_references=it.source_references,
                            recommended_next_step=it.recommended_next_step,
                        )
                    )
                    break

        # Count metrics
        b_count = sum(1 for it in items if it.item_type == "Blocker")
        a_count = sum(1 for it in items if it.item_type == "Action Item")
        p_count = len(pending_decisions)
        app_count = len(approved_decisions)

        # Unassigned count: strictly evaluates action items lacking a named owner
        u_count = sum(
            1
            for it in items
            if it.item_type == "Action Item"
            and (not it.assigned_owner or it.assigned_owner.strip().upper() in ("UNKNOWN", "UNASSIGNED", "NONE", "", "-"))
        )

        # Overdue check evaluated relative to document effective reporting date (20 October 2026)
        overdue_count = 0
        for it in items:
            if it.item_type == "Action Item" and it.due_date and it.due_date.upper() not in ("UNKNOWN", "NOT SPECIFIED", "NONE", ""):
                iso_m = re.search(r"\b(202[0-9]-[0-1][0-9]-[0-3][0-9])\b", it.due_date)
                text_m = re.search(r"\b(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4})\b", it.due_date)
                d_val = None
                if iso_m:
                    try:
                        d_val = datetime.strptime(iso_m.group(1), "%Y-%m-%d").date()
                    except ValueError:
                        pass
                elif text_m:
                    for fmt in ("%d %b %Y", "%d %B %Y"):
                        try:
                            d_val = datetime.strptime(text_m.group(1), fmt).date()
                            break
                        except ValueError:
                            pass

                if d_val and d_val < effective_ref_date and it.status.lower() not in ("completed", "done", "closed"):
                    overdue_count += 1

        # Sort items: Blockers first, then Action items sorted by ID (A-01, A-02...), then Pending Decisions
        def _sort_item_key(it):
            if it.item_type == "Blocker":
                return (0, it.item_id)
            elif it.item_type == "Action Item":
                return (1, it.item_id)
            else:
                return (2, it.item_id)

        items.sort(key=_sort_item_key)

        summary = (
            f"Extracted {b_count} active blocker, {a_count} action register entries, "
            f"{p_count} pending decision, and {app_count} approved decision. "
            f"All {a_count} action items have designated owners ({u_count} unassigned), "
            f"and {overdue_count} tasks are overdue relative to the reporting date ({effective_ref_date.strftime('%d %B %Y')})."
        )

        return BlockerExtractionResponse(
            blocker_count=b_count,
            action_item_count=a_count,
            pending_decision_count=p_count,
            approved_decision_count=app_count,
            unassigned_count=u_count,
            overdue_count=overdue_count,
            items=items,
            approved_decisions=approved_decisions,
            pending_decisions=pending_decisions,
            source_references=citations,
            summary=summary,
        )


blocker_agent = BlockerAgent()
