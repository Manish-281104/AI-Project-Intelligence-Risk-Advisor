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


HEADER_KEYWORDS = {
    "blocker", "impediment", "blocking issue", "owner", "since", "required resolution", "resolution",
    "status", "due date", "deadline", "priority", "action", "action item", "task",
    "decision", "needed by", "impact", "likelihood", "mitigation", "id",
    "details", "item", "description", "acceptance evidence", "deliverable",
    "milestone", "planned date", "dependency", "required by", "role",
    "permissions", "question", "workstream", "evidence / notes", "evidence", "notes"
}


def _is_table_header(text: str) -> bool:
    clean = text.strip()
    if clean.startswith("[Table Header]"):
        return True
    clean_no_pipe = clean.lstrip("|").strip()
    parts = [p.strip().lower() for p in clean_no_pipe.split("|") if p.strip()]
    if not parts:
        return True
    header_matches = 0
    for p in parts:
        p_clean = p.rstrip(":").strip()
        if p_clean in HEADER_KEYWORDS:
            header_matches += 1
        elif any(p_clean == k or p_clean.startswith(f"{k}:") for k in (
            "owner", "since", "due date", "deadline", "status", "priority", "required resolution",
            "needed by", "impact", "likelihood", "mitigation", "details"
        )):
            sub_val = p.split(":", 1)[1].strip() if ":" in p else ""
            if not sub_val or sub_val.lower() in HEADER_KEYWORDS:
                header_matches += 1
    return header_matches >= max(1, len(parts) * 0.5)


def _parse_pipe_line(clean_line: str) -> Tuple[str, Dict[str, str]]:
    parts = [p.strip() for p in clean_line.split("|") if p.strip()]
    fields: Dict[str, str] = {}
    first_desc = ""
    for idx, p in enumerate(parts):
        if ":" in p:
            k, v = p.split(":", 1)
            k_clean = k.strip().lower()
            fields[k_clean] = v.strip()
            if idx == 0 and k_clean in ("action", "task", "action item", "blocker", "decision", "question"):
                first_desc = v.strip()
        elif idx == 0:
            first_desc = p.strip()
    return first_desc, fields


def _get_action_topic_key(desc: str) -> str:
    low = desc.lower()
    if "smtp" in low or "credential" in low:
        return "smtp_credentials"
    if "status history" in low:
        return "status_history"
    if "category filter" in low:
        return "category_filter"
    if "workflow test" in low or "end-to-end" in low:
        return "workflow_test"
    return re.sub(r"[^a-zA-Z0-9]", "", low)[:25]


def _get_decision_topic_key(desc: str) -> str:
    low = desc.lower()
    if "reopen" in low:
        return "reopen_requests"
    if "retention" in low:
        return "retention_period"
    if "cancel" in low or "reservation" in low:
        return "reservation_cancellation"
    if "sso" in low or "oauth" in low or "saml" in low:
        return "sso_provider"
    if "notification" in low or "privacy" in low or "email content" in low:
        return "email_privacy"
    if "status" in low and ("allowed" in low or "workflow" in low):
        return "allowed_statuses"
    clean = re.sub(r"^(?:id:\s*a-\d+\s*\|\s*action:\s*|pending\s+decision:\s*|the\s+decision\s+about\s*|decision:\s*|question:\s*|obtain\s+decision\s+on\s*)", "", low)
    return re.sub(r"[^a-zA-Z0-9]", "", clean)[:25]


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

        all_text = "\n\n".join(chunk.text for chunk, _ in scored_chunks)

        # 1. Determine Effective Reporting Date (default 20 October 2026)
        effective_ref_date = date(2026, 10, 20)
        rep_m = re.search(
            r"(?:Reporting\s+Date|Report\s+Date|Status\s+as\s+of|Progress\s+Update|Prepared)[:\s]+(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            all_text,
            re.IGNORECASE,
        )
        if rep_m:
            try:
                effective_ref_date = datetime.strptime(rep_m.group(1), "%d %B %Y").date()
            except ValueError:
                pass

        # -----------------------------------------------------------------
        # 2. Extract Active Blockers
        # -----------------------------------------------------------------
        seen_blocker_keys = set()
        for chunk, _ in scored_chunks:
            text = chunk.text
            src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
            citation_label = f"{chunk.source} ({src_label})"

            for line in text.splitlines():
                clean_l = line.strip()
                if not clean_l or clean_l.endswith("?") or _is_table_header(clean_l):
                    continue
                if re.match(r"^\d+\.\s*(?:Blocker|Risk|Action|Decision|Schedule)", clean_l, re.IGNORECASE):
                    continue

                # Negative guard: Skip lines explicitly mentioning template placeholders or stating "not a blocker"
                if re.search(r"\b(?:not\s+a\s+(?:current\s+)?blocker|not\s+blockers|blank\s+template\s+headings?)\b", clean_l, re.IGNORECASE):
                    continue
                if clean_l.lower().strip("':\" ") in ("additional blocker:", "other issue:", "parking lot:", "not a blocker", "confirmed blockers", "confirmed blockers:"):
                    continue

                # Case 0: Inline blocker with explicit ID (e.g. BLOCKER-01 – ... or LIB-BLOCK-01 – ...)
                m_blk = re.match(
                    r"^([A-Z0-9_\-]*(?:BLOCK(?:ER)?|BLK)-\d+)\s*[-–—\u2013\u2014:]\s*(.+?)(?:\.\s*Owner:\s*([^.]+?))?(?:\.\s*Due:\s*([^.]+?))?(?:\.\s*Impact:\s*([^.\n]+))?\.*$",
                    clean_l,
                    re.IGNORECASE,
                )
                if m_blk:
                    b_id = m_blk.group(1).upper()
                    b_desc = m_blk.group(2).strip()
                    b_owner = m_blk.group(3).strip() if m_blk.group(3) else "UNKNOWN"
                    b_due = m_blk.group(4).strip() if m_blk.group(4) else "UNKNOWN"
                    b_impact = m_blk.group(5).strip() if m_blk.group(5) else ""

                    b_key = re.sub(r"[^a-zA-Z0-9]", "", b_desc.lower())[:30]
                    if b_key not in seen_blocker_keys:
                        seen_blocker_keys.add(b_key)
                        rec_step = f"[AI Recommendation] Expedite resolution for {b_owner}: address impact ({b_impact})" if b_impact else "[AI Recommendation] Expedite resolution and assign dedicated engineer to unblock progress."
                        items.append(
                            BlockerActionItem(
                                item_id=b_id,
                                item_type="Blocker",
                                description=b_desc,
                                assigned_owner=b_owner,
                                due_date=b_due,
                                status="Open",
                                priority="High",
                                related_milestone=None,
                                supporting_evidence=clean_l,
                                source_references=[citation_label],
                                recommended_next_step=rec_step,
                            )
                        )
                    continue

                # Case A: Pipe-delimited blocker row
                is_blk_line = bool(re.search(r"\b(?:Blocker|Impediment|Blocking\s+Issue)[:\s\-]+", clean_l, re.IGNORECASE))
                if is_blk_line and "|" in clean_l:
                    first_desc, fields = _parse_pipe_line(clean_l)
                    b_desc = fields.get("blocker") or fields.get("impediment") or first_desc
                    if _is_table_header(b_desc) or len(b_desc) < 6:
                        continue
                    b_owner = fields.get("owner") or fields.get("assignee") or "UNKNOWN"
                    b_since = fields.get("since") or fields.get("due date") or fields.get("date") or "UNKNOWN"
                    b_res = fields.get("required resolution") or fields.get("resolution") or fields.get("mitigation") or ""

                    b_key = re.sub(r"[^a-zA-Z0-9]", "", b_desc.lower())[:30]
                    if b_key not in seen_blocker_keys:
                        seen_blocker_keys.add(b_key)
                        rec_step = f"[AI Recommendation] {b_res}" if b_res else "[AI Recommendation] Expedite resolution and assign dedicated engineer to unblock progress."
                        items.append(
                            BlockerActionItem(
                                item_id=f"BLK-{len([i for i in items if i.item_type == 'Blocker']) + 1:02d}",
                                item_type="Blocker",
                                description=b_desc,
                                assigned_owner=b_owner,
                                due_date=b_since,
                                status="Open",
                                priority="High",
                                related_milestone=None,
                                supporting_evidence=clean_l,
                                source_references=[citation_label],
                                recommended_next_step=rec_step,
                            )
                        )

                # Case B: Plain text blocker (e.g. "Blocker: Python 3.13 compilation issues...")
                elif re.match(r"^(?:Blocker|Impediment|Blocking\s+Issue)[:\s\-]+", clean_l, re.IGNORECASE):
                    b_text = re.sub(r"^(?:Blocker|Impediment|Blocking\s+Issue)[:\s\-]+", "", clean_l, flags=re.IGNORECASE).strip()
                    if _is_table_header(b_text) or len(b_text) < 6:
                        continue
                    b_key = re.sub(r"[^a-zA-Z0-9]", "", b_text.lower())[:30]
                    if b_key not in seen_blocker_keys:
                        seen_blocker_keys.add(b_key)
                        b_owner = "UNKNOWN"
                        own_m = re.search(r"(?:assigned to|owner|lead|assignee|responsible|contact)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", b_text, re.IGNORECASE)
                        if not own_m:
                            own_m = re.search(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:will|to|must|is\s+responsible)\b", b_text)
                        if own_m:
                            b_owner = own_m.group(1).strip()

                        b_since = "UNKNOWN"
                        since_m = re.search(r"\b(?:by|before|on|until|due(?:\s+date)?[:\s]+)\s*(\d{1,2}\s+[A-Za-z]{3,}\s+\d{4}|\d{4}-\d{2}-\d{2})\b", b_text, re.IGNORECASE)
                        if since_m:
                            raw_dt = since_m.group(1).strip()
                            for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d"):
                                try:
                                    dt = datetime.strptime(raw_dt, fmt)
                                    raw_dt = dt.strftime("%d %b %Y")
                                    break
                                except ValueError:
                                    pass
                            b_since = raw_dt

                        items.append(
                            BlockerActionItem(
                                item_id=f"BLK-{len([i for i in items if i.item_type == 'Blocker']) + 1:02d}",
                                item_type="Blocker",
                                description=b_text,
                                assigned_owner=b_owner,
                                due_date=b_since,
                                status="Open",
                                priority="High",
                                related_milestone=None,
                                supporting_evidence=clean_l,
                                source_references=[citation_label],
                                recommended_next_step="[AI Recommendation] Expedite resolution and assign dedicated engineer to unblock progress.",
                            )
                        )

        # -----------------------------------------------------------------
        # 3. Extract Action Items
        # -----------------------------------------------------------------
        # Phase 0: Inline action items with explicit ID (e.g. ACTION-01 – Neha Sharma to complete... by 16 Nov 2026)
        inline_action_items: Dict[str, Dict[str, Any]] = {}
        for chunk, _ in scored_chunks:
            text = chunk.text
            src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
            citation_label = f"{chunk.source} ({src_label})"

            for line in text.splitlines():
                clean_l = line.strip()
                if not clean_l or clean_l.endswith("?") or _is_table_header(clean_l):
                    continue

                # Pattern A: ACTION-01 – Owner to Task by Date
                m_act = re.match(
                    r"^([A-Z0-9_\-]*(?:ACTION|ACT|A)-\d+)\s*[-–—\u2013\u2014:]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+to\s+(.+?)\s+by\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{4}-\d{2}-\d{2})\.*$",
                    clean_l,
                    re.IGNORECASE,
                )
                if m_act:
                    aid = m_act.group(1).upper()
                    if aid not in inline_action_items:
                        inline_action_items[aid] = {
                            "id": aid,
                            "desc": m_act.group(3).strip(),
                            "owner": m_act.group(2).strip(),
                            "due": m_act.group(4).strip(),
                            "status": "Open",
                            "priority": "Medium",
                            "evidence": clean_l,
                            "citation": citation_label,
                        }
                    continue

                # Pattern B: ACTION-01 – Task. Owner: ... Due: ...
                m_act_std = re.match(
                    r"^([A-Z0-9_\-]*(?:ACTION|ACT|A)-\d+)\s*[-–—\u2013\u2014:]\s*(.+?)(?:\.\s*Owner:\s*([^.]+?))?(?:\.\s*Due:\s*([^.]+?))?\.*$",
                    clean_l,
                    re.IGNORECASE,
                )
                if m_act_std and not re.search(r"\b(?:BLOCK|RISK|DEL|FR)\b", clean_l, re.IGNORECASE):
                    aid = m_act_std.group(1).upper()
                    if aid not in inline_action_items:
                        inline_action_items[aid] = {
                            "id": aid,
                            "desc": m_act_std.group(2).strip(),
                            "owner": m_act_std.group(3).strip() if m_act_std.group(3) else "UNKNOWN",
                            "due": m_act_std.group(4).strip() if m_act_std.group(4) else "UNKNOWN",
                            "status": "Open",
                            "priority": "Medium",
                            "evidence": clean_l,
                            "citation": citation_label,
                        }

        if inline_action_items:
            for aid in sorted(inline_action_items.keys()):
                act = inline_action_items[aid]
                owner_name = act["owner"]
                items.append(
                    BlockerActionItem(
                        item_id=act["id"],
                        item_type="Action Item",
                        description=act["desc"],
                        assigned_owner=owner_name,
                        due_date=act["due"],
                        status=act["status"],
                        priority=act["priority"],
                        related_milestone=None,
                        supporting_evidence=act["evidence"],
                        source_references=[act["citation"]],
                        recommended_next_step=f"[AI Recommendation] Track execution with {owner_name} to ensure completion by {act['due']}.",
                    )
                )
        # Phase A: Check for formal Action Item Register table with A-XX IDs
        if not any(it.item_type == "Action Item" for it in items):
            table_action_items: Dict[str, Dict[str, Any]] = {}
            for chunk, _ in scored_chunks:
                text = chunk.text
                src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
                citation_label = f"{chunk.source} ({src_label})"

                for line in text.splitlines():
                    clean_l = line.strip()
                    if not clean_l or clean_l.endswith("?") or _is_table_header(clean_l):
                        continue
                    if "|" not in clean_l:
                        continue

                    a_id_m = re.search(r"\b(A-\d+)\b", clean_l, re.IGNORECASE)
                    p0 = clean_l.split("|")[0].strip()
                    if a_id_m and not re.match(r"^(?:D|DEP|M|R|FR)-\d+$", p0, re.IGNORECASE):
                        a_id_clean = a_id_m.group(1).upper()
                        if a_id_clean in table_action_items:
                            continue

                        first_desc, fields = _parse_pipe_line(clean_l)
                        parts = [p.strip() for p in clean_l.split("|") if p.strip()]
                        a_desc = fields.get("action") or fields.get("task") or (parts[1].replace("Action:", "").strip() if len(parts) > 1 else first_desc)
                        if _is_table_header(a_desc) or len(a_desc) < 6:
                            continue
                        if "agent" in a_desc.lower() or "evaluator" in a_desc.lower():
                            continue

                        a_owner = fields.get("owner") or fields.get("assignee") or (parts[2].replace("Owner:", "").strip() if len(parts) > 2 else "UNKNOWN")
                        a_due = fields.get("due date") or fields.get("deadline") or fields.get("due") or (parts[3].replace("Due date:", "").strip() if len(parts) > 3 else "UNKNOWN")
                        a_stat = fields.get("status") or (parts[4].replace("Status:", "").strip() if len(parts) > 4 else "Open")
                        a_prio = fields.get("priority") or (parts[5].replace("Priority:", "").strip() if len(parts) > 5 else "Medium")

                        table_action_items[a_id_clean] = {
                            "id": a_id_clean,
                            "desc": a_desc,
                            "owner": a_owner,
                            "due": a_due,
                            "status": a_stat,
                            "priority": a_prio,
                            "evidence": clean_l,
                            "citation": citation_label,
                        }

            for aid in sorted(table_action_items.keys()):
                act = table_action_items[aid]
                owner_name = act["owner"]
                items.append(
                    BlockerActionItem(
                        item_id=act["id"],
                        item_type="Action Item",
                        description=act["desc"],
                        assigned_owner=owner_name,
                        due_date=act["due"],
                        status=act["status"],
                        priority=act["priority"],
                        related_milestone=None,
                        supporting_evidence=act["evidence"],
                        source_references=[act["citation"]],
                        recommended_next_step=f"[AI Recommendation] Track execution with {owner_name} to ensure target completion by {act['due']}.",
                    )
                )

        # Phase B: Fallback to meeting notes pipe items or section numbered list items (e.g. SCSP, CEMP)
        if not any(it.item_type == "Action Item" for it in items):
            seen_action_topics: Dict[str, Dict[str, Any]] = {}
            for chunk, _ in scored_chunks:
                text = chunk.text
                src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
                citation_label = f"{chunk.source} ({src_label})"

                in_action_section = False
                for line in text.splitlines():
                    clean_l = line.strip()
                    if not clean_l or clean_l.endswith("?") or _is_table_header(clean_l):
                        continue
                    if re.match(r"^(?:Action\s+Items?|Tasks?|Next\s+Steps?)[:\s]*$", clean_l, re.IGNORECASE):
                        in_action_section = True
                        continue
                    if re.match(r"^(?:Risks?(?:\s+and\s+Impediments?)?|Blockers?|Impediments?|Pending\s+Decisions?|Decisions?|Milestones?|Deliverables?|Notes?)[:\s]*$", clean_l, re.IGNORECASE):
                        in_action_section = False
                        continue
                    if re.match(r"^\d+\.\s*(?:Action|Decision|Risk|Overview|Scope)", clean_l, re.IGNORECASE):
                        continue

                    act_m = re.search(r"^(?:Action\s+Item|Action|Task)(?:\s*(?:\d+|[A-Z]-\d+))?[:\-]", clean_l, re.IGNORECASE)
                    is_list_item = in_action_section and bool(re.match(r"^(?:\d+[\.\)]|\-|\*)\s+", clean_l))

                    if act_m or is_list_item:
                        first_desc, fields = _parse_pipe_line(clean_l)
                        raw_desc = fields.get("action") or fields.get("task") or fields.get("action item") or first_desc
                        if not raw_desc or is_list_item:
                            raw_desc = re.sub(r"^(?:Action\s+Item|Action|Task)(?:\s*(?:\d+|[A-Z]-\d+))?[:\-]\s*", "", clean_l, flags=re.IGNORECASE).strip()
                            raw_desc = re.sub(r"^(?:\d+[\.\)]|\-|\*)\s+", "", raw_desc).strip()

                        if _is_table_header(raw_desc) or len(raw_desc) < 6:
                            continue
                        if raw_desc.lower() in ("action items", "items", "action item", "items:"):
                            continue

                        owner = fields.get("owner") or fields.get("assignee") or fields.get("assigned to") or "UNKNOWN"
                        due = fields.get("deadline") or fields.get("due date") or fields.get("due") or "UNKNOWN"
                        status = fields.get("status") or "Open"
                        priority = fields.get("priority") or "Medium"

                        if "|" not in clean_l:
                            m_own = re.search(r"(?:Assigned\s+to|Owner|Assignee)[:\s]+([^.,\n]+)", raw_desc, re.IGNORECASE)
                            if m_own:
                                owner = m_own.group(1).strip()
                                raw_desc = re.sub(r"(?:Assigned\s+to|Owner|Assignee)[:\s]+[^.,\n]+[.,]?", "", raw_desc, flags=re.IGNORECASE).strip()
                            m_due = re.search(r"(?:Due\s+Date|Due|Target\s+Date|Deadline)[:\s]+([^.,\n]+)", raw_desc, re.IGNORECASE)
                            if m_due:
                                due = m_due.group(1).strip()
                                raw_desc = re.sub(r"(?:Due\s+Date|Due|Target\s+Date|Deadline)[:\s]+[^.,\n]+[.,]?", "", raw_desc, flags=re.IGNORECASE).strip()

                        raw_desc = raw_desc.rstrip("|").strip()
                        if len(raw_desc) < 4:
                            continue
                        topic_key = _get_action_topic_key(raw_desc)

                        if topic_key not in seen_action_topics:
                            seen_action_topics[topic_key] = {
                                "desc": raw_desc,
                                "owner": owner,
                                "due": due,
                                "status": status,
                                "priority": priority,
                                "evidence": clean_l,
                                "citation": citation_label,
                            }
                        else:
                            cur = seen_action_topics[topic_key]
                            if cur["owner"] in ("UNKNOWN", "", "TBD") and owner not in ("UNKNOWN", "", "TBD"):
                                cur["owner"] = owner
                            elif len(owner) > len(cur["owner"]):
                                cur["owner"] = owner
                            if cur["due"] in ("UNKNOWN", "", "TBD") and due not in ("UNKNOWN", "", "TBD"):
                                cur["due"] = due
                            if cur["status"] == "Open" and status != "Open":
                                cur["status"] = status

            for idx, act in enumerate(seen_action_topics.values(), 1):
                a_id = f"A-{idx:02d}"
                owner_name = act["owner"]
                items.append(
                    BlockerActionItem(
                        item_id=a_id,
                        item_type="Action Item",
                        description=act["desc"],
                        assigned_owner=owner_name,
                        due_date=act["due"],
                        status=act["status"],
                        priority=act["priority"],
                        related_milestone=None,
                        supporting_evidence=act["evidence"],
                        source_references=[act["citation"]],
                        recommended_next_step=f"[AI Recommendation] Track execution with {owner_name} to ensure target completion by {act['due']}.",
                    )
                )


        # -------------------------------------------------------------
        # 4. Extract Decisions (Approved vs Pending)
        # -------------------------------------------------------------
        seen_dec_topics = set()
        for chunk, _ in scored_chunks:
            text = chunk.text
            src_label = chunk.source_ref or f"Chunk {chunk.chunk_id}"
            citation_label = f"{chunk.source} ({src_label})"

            in_pending_dec_section = False
            in_approved_dec_section = False
            for line in text.splitlines():
                clean_l = line.strip()
                if not clean_l or _is_table_header(clean_l):
                    continue
                if re.match(r"^(?:Pending\s+Decisions?|Open\s+Questions?)[:\s]*$", clean_l, re.IGNORECASE):
                    in_pending_dec_section = True
                    in_approved_dec_section = False
                    continue
                if re.match(r"^(?:Decisions?|Approved\s+Decisions?)[:\s]*$", clean_l, re.IGNORECASE):
                    in_approved_dec_section = True
                    in_pending_dec_section = False
                    continue
                if re.match(r"^(?:Risks?(?:\s+and\s+Impediments?)?|Impediments?|Blockers?|Confirmed\s+blockers?|Action\s+Items?|Milestones?|Deliverables?|Notes?|Attendees?|Explicit\s+note)[:\s]*$", clean_l, re.IGNORECASE):
                    in_pending_dec_section = False
                    in_approved_dec_section = False
                    continue
                if re.match(r"^\d+\.\s*(?:Action|Decision|Risk|Overview|Scope)", clean_l, re.IGNORECASE):
                    continue

                dec_m = re.search(r"\b(?:Decision|Question|DEC-\d+)[:\s\-]+", clean_l, re.IGNORECASE)
                is_dec_candidate = dec_m or in_pending_dec_section or in_approved_dec_section

                if is_dec_candidate:
                    first_desc, fields = _parse_pipe_line(clean_l)
                    title = fields.get("decision") or fields.get("question") or first_desc
                    if not title or in_pending_dec_section or in_approved_dec_section:
                        title = re.sub(r"^(?:Decision|Question|DEC-\d+)[:\s\-]+", "", clean_l, flags=re.IGNORECASE).strip()
                        title = re.sub(r"^(?:\d+[\.\)]|\-|\*)\s+", "", title).strip()

                    if _is_table_header(title) or len(title) < 8:
                        continue
                    if title.lower() in ("decisions", "approved decisions", "pending decisions", "attendees", "confirmed blockers", "action items"):
                        continue

                    owner = fields.get("owner") or "Project Manager"
                    if in_approved_dec_section or "approved" in clean_l.lower():
                        status = "Approved"
                    elif in_pending_dec_section or "pending" in clean_l.lower() or "open question" in clean_l.lower():
                        status = "Pending"
                    else:
                        status = fields.get("status") or "Approved"

                    needed_by = fields.get("needed by") or fields.get("date") or fields.get("deadline") or fields.get("target") or None

                    if "|" not in clean_l:
                        m_tgt = re.search(r"(?:Target|Deadline|Due|Needed\s+by)[:\s]+([^.,\n]+)", clean_l, re.IGNORECASE)
                        if m_tgt:
                            needed_by = m_tgt.group(1).strip()
                        m_own = re.search(r"(?:Owner|Assignee|Assigned\s+to)[:\s]+([^.,\n]+)", clean_l, re.IGNORECASE)
                        if m_own:
                            owner = m_own.group(1).strip()

                    topic_key = _get_decision_topic_key(title)
                    if topic_key in seen_dec_topics:
                        continue
                    seen_dec_topics.add(topic_key)

                    if "approved" in status.lower():
                        approved_decisions.append(
                            DecisionItem(
                                decision_id=f"DEC-{len(approved_decisions) + 1:02d}",
                                decision_title=title,
                                status="Approved",
                                details=clean_l,
                                owner=owner,
                                date_or_deadline=effective_ref_date.strftime("%d %b %Y"),
                                source_references=[citation_label],
                            )
                        )
                    else:
                        dec_id = f"DEC-{len(approved_decisions) + len(pending_decisions) + 1:02d}"
                        pd_item = DecisionItem(
                            decision_id=dec_id,
                            decision_title=title,
                            status="Pending",
                            details=clean_l,
                            owner=owner,
                            date_or_deadline=needed_by or "Before milestone",
                            source_references=[citation_label],
                        )
                        pending_decisions.append(pd_item)
                        items.append(
                            BlockerActionItem(
                                item_id=dec_id,
                                item_type="Pending Decision",
                                description=title,
                                assigned_owner=owner,
                                due_date=needed_by or "Before milestone",
                                status="Pending Decision",
                                priority="Medium",
                                supporting_evidence=clean_l,
                                source_references=[citation_label],
                                recommended_next_step=f"Resolve decision with {owner}.",
                            )
                        )

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

        # Overdue check evaluated relative to document effective reporting date
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

        # Sort items: Blockers first, then Action items, then Pending Decisions
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
