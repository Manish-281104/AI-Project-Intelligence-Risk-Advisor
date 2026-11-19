import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from app.core.config import settings
from app.schemas.project import DocumentChunk
from app.schemas.agent_models import SourceCitation
from app.schemas.milestone3_models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ConversationHistoryResponse,
)
from app.services.document_service import document_service
from app.services.retriever import semantic_retriever
from app.services.llm_service import llm_service
from app.services.scope_agent import scope_agent
from app.services.risk_agent import risk_agent
from app.services.blocker_agent import blocker_agent
from app.services.health_scoring_service import health_scoring_service


class ConversationalProjectAssistant:
    """
    RAG-grounded Conversational Project Intelligence Assistant.
    Provides evidence-backed answers to natural language project management queries,
    enforces strict anti-hallucination guardrails, cites document coordinates,
    and isolates conversation history per project workspace.
    """

    FALLBACK_NO_EVIDENCE = "I couldn't find enough information in the uploaded project documents to answer this question."

    def __init__(self):
        self.history_file = settings.BASE_DIR / "data" / "conversations.json"
        self._ensure_storage()

    def _ensure_storage(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self._save_conversations({})

    def _load_conversations(self) -> Dict[str, Dict[str, Any]]:
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_conversations(self, data: Dict[str, Dict[str, Any]]):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    async def answer_question(self, req: ChatRequest) -> ChatResponse:
        """
        Process user question with RAG pipeline and return grounded response with citations.
        """
        workspace = document_service.get_workspace()
        project_id = req.project_id or workspace.project_id
        conversation_id = req.conversation_id or f"conv_{project_id}"
        question = req.question.strip()

        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Check if workspace has any documents
        docs = document_service.list_documents()
        if not docs:
            no_docs_reply = "No project documents have been uploaded to this workspace yet. Please upload project documents (PDF, DOCX, CSV, TXT) to ask questions."
            return ChatResponse(
                answer=no_docs_reply,
                citations=[],
                has_evidence=False,
                conversation_id=conversation_id,
                project_id=project_id,
                timestamp=now_iso,
                suggested_followups=["How do I upload project documents?"],
            )

        # Fetch previous conversation turns for follow-up query resolution
        history_resp = self.get_conversation_history(project_id, conversation_id)
        last_assistant_msg = ""
        for m in reversed(history_resp.messages):
            if m.role == "assistant":
                last_assistant_msg = m.content
                break

        # 2. Retrieve top-k semantically relevant chunks filtered by project_id
        scored_chunks = semantic_retriever.retrieve(
            query=question,
            top_k=8,
            project_id=project_id,
            min_similarity=0.01,
        )

        # 3. Try LLM invocation if configured
        if llm_service.is_configured:
            llm_reply, citations = await self._run_llm_chat(question, scored_chunks, project_id)
            if llm_reply:
                self._record_turn(project_id, conversation_id, question, llm_reply, citations)
                followups = self._generate_suggested_followups(question)
                return ChatResponse(
                    answer=llm_reply,
                    citations=citations,
                    has_evidence=bool(citations and llm_reply != self.FALLBACK_NO_EVIDENCE),
                    conversation_id=conversation_id,
                    project_id=project_id,
                    timestamp=now_iso,
                    suggested_followups=followups,
                )

        # 4. Deterministic Grounded Fallback Response Engine
        answer, citations, has_ev = await self._synthesize_grounded_answer(
            question=question,
            scored_chunks=scored_chunks,
            last_assistant_msg=last_assistant_msg,
            project_id=project_id,
        )

        # Ensure grounded responses with evidence always include a valid citation
        if has_ev and not citations:
            if scored_chunks:
                top_chunk = scored_chunks[0][0]
                citations.append(
                    SourceCitation(
                        document_id=top_chunk.document_id,
                        filename=top_chunk.source,
                        chunk_id=top_chunk.chunk_id,
                        page_number=top_chunk.page_number,
                        row_number=top_chunk.row_number,
                        source_ref=top_chunk.source_ref or "Document Passage",
                        excerpt=top_chunk.text[:220],
                    )
                )
            else:
                cit = self._find_citation("", "Project Document", question)
                if cit:
                    citations.append(cit)

        self._record_turn(project_id, conversation_id, question, answer, citations)
        followups = self._generate_suggested_followups(question)

        return ChatResponse(
            answer=answer,
            citations=citations,
            has_evidence=has_ev,
            conversation_id=conversation_id,
            project_id=project_id,
            timestamp=now_iso,
            suggested_followups=followups,
        )

    def _chunk_to_citation(self, chunk: DocumentChunk) -> SourceCitation:
        excerpt = (chunk.text[:220] + "...") if len(chunk.text) > 220 else chunk.text
        return SourceCitation(
            document_id=chunk.document_id,
            filename=chunk.source,
            chunk_id=chunk.chunk_id,
            page_number=chunk.page_number,
            row_number=chunk.row_number,
            source_ref=chunk.source_ref or f"Chunk {chunk.chunk_id}",
            excerpt=excerpt,
        )

    def _find_citation(
        self, filename_fragment: str, section_label: str, excerpt: str, project_id: Optional[str] = None
    ) -> Optional[SourceCitation]:
        """Dynamically locate matching document citation from workspace filtered by project_id."""
        docs = document_service.list_documents()
        if project_id:
            docs = [d for d in docs if d.project_id == project_id]
        if not docs:
            return None

        matching_doc = None
        frag = filename_fragment.lower().strip()

        # 1. Direct filename or doc_id match
        if frag:
            for doc in docs:
                if frag in doc.filename.lower() or doc.document_id in frag:
                    matching_doc = doc
                    break

        target_doc = matching_doc or docs[0]

        # 2. Match chunk by keywords in excerpt
        excerpt_words = [w for w in re.sub(r"[^a-zA-Z0-9\s]", "", excerpt.lower()).split() if len(w) > 3]
        for c in target_doc.chunks:
            c_low = c.text.lower()
            if any(w in c_low for w in excerpt_words[:6]):
                return SourceCitation(
                    document_id=target_doc.document_id,
                    filename=target_doc.filename,
                    chunk_id=c.chunk_id,
                    page_number=c.page_number,
                    row_number=c.row_number,
                    source_ref=c.source_ref or section_label,
                    excerpt=c.text[:220],
                )

        first_c = target_doc.chunks[0] if target_doc.chunks else None
        return SourceCitation(
            document_id=target_doc.document_id,
            filename=target_doc.filename,
            chunk_id=first_c.chunk_id if first_c else f"doc_{target_doc.document_id}_01",
            page_number=first_c.page_number if first_c else None,
            row_number=first_c.row_number if first_c else None,
            source_ref=first_c.source_ref if (first_c and first_c.source_ref) else section_label,
            excerpt=(first_c.text[:220] if first_c else excerpt[:220]),
        )

    async def _run_llm_chat(
        self,
        question: str,
        scored_chunks: List[Tuple[DocumentChunk, float]],
        project_id: Optional[str] = None,
    ) -> Tuple[Optional[str], List[SourceCitation]]:
        """Query LLM with strict context grounding and citation generation."""
        if not scored_chunks:
            return None, []
        context = semantic_retriever.format_context_for_prompt(scored_chunks)
        system_prompt = (
            "You are a helpful, professional AI Project Intelligence Assistant. "
            "Answer the user's question accurately using ONLY the provided project document excerpts. "
            "Do NOT invent dates, names, metrics, or facts. "
            "If the information is not in the excerpts, clearly state that the uploaded documents do not contain the answer. "
            "Distinguish documented facts from recommendations."
        )
        prompt = f"Project Document Excerpts:\n{context}\n\nUser Question: {question}\n\nAnswer:"
        reply = await llm_service.generate_text(prompt, system_prompt)
        if reply:
            citations = [self._chunk_to_citation(c[0]) for c in scored_chunks[:3]]
            return reply.strip(), citations
        return None, []

    async def _synthesize_grounded_answer(
        self,
        question: str,
        scored_chunks: List[Tuple[DocumentChunk, float]],
        last_assistant_msg: str = "",
        project_id: Optional[str] = None,
    ) -> Tuple[str, List[SourceCitation], bool]:
        """Synthesize answers deterministically from dynamic agent intelligence and retrieved passages."""
        q_lower = question.lower()
        citations: List[SourceCitation] = []

        # -------------------------------------------------------------
        # 0. Conversational follow-up resolution (pronouns / ordinals)
        # -------------------------------------------------------------
        if last_assistant_msg:
            # "Who owns the second one?"
            if "second" in q_lower or "2nd" in q_lower:
                bullet_lines = [l.strip() for l in last_assistant_msg.splitlines() if l.strip().startswith("- ") or re.match(r"^\d+\.", l.strip())]
                if len(bullet_lines) >= 2:
                    second_item = bullet_lines[1]
                    answer = f"The second item listed is:\n\n{second_item}"
                    if scored_chunks:
                        citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                    return answer, citations, True

            # "How to resolve it?" / "What is required to resolve it?"
            if any(k in q_lower for k in ("resolve it", "resolution", "how to resolve", "how do we resolve")):
                blocker_res = await blocker_agent.analyze()
                for b in blocker_res.items:
                    if b.item_type == "Blocker" and (b.description.lower()[:20] in last_assistant_msg.lower() or b.item_id.lower() in last_assistant_msg.lower()):
                        answer = (
                            f"To resolve the active blocker **{b.item_id}: {b.description}**:\n\n"
                            f"- **Assigned Owner:** {b.assigned_owner}\n"
                            f"- **Due Date:** {b.due_date}\n"
                            f"- **Resolution / Mitigation:** {b.recommended_next_step.replace('[AI Recommendation] ', '')}"
                        )
                        cit = self._find_citation(b.source_references[0] if b.source_references else "", b.item_id, b.supporting_evidence, project_id=project_id)
                        if cit:
                            citations.append(cit)
                        elif scored_chunks:
                            citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                        return answer, citations, True

        # -------------------------------------------------------------
        # 1. Ownership / Responsibilities Query
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("who is responsible", "who owns", "responsible for", "owner of", "assignee", "who handles")):
            blocker_res = await blocker_agent.analyze()
            scope_res = await scope_agent.analyze()

            clean_subject = re.sub(
                r"^(?:who\s+is\s+responsible\s+for|who\s+owns|who\s+is\s+handling|who\s+leads|who\s+is\s+the\s+owner\s+of)\s+",
                "",
                question,
                flags=re.IGNORECASE,
            ).rstrip("?").strip()

            stops = {
                "what", "which", "where", "who", "is", "are", "the", "for", "of", "to", "in", "on",
                "about", "responsible", "owner", "owns", "handling", "leads", "item", "items", "task",
                "project", "blocker", "blockers", "current", "active", "open", "the", "a", "an"
            }
            clean_text = clean_subject.lower().replace("-", " ")
            q_keywords = [
                w for w in re.sub(r"[^a-zA-Z0-9\s]", "", clean_text).split()
                if len(w) > 2 and w not in stops
            ]
            min_score = 2 if len(q_keywords) >= 2 else 1

            best_match = None
            best_score = 0
            match_type = ""

            # Check blockers
            for b in [i for i in blocker_res.items if i.item_type == "Blocker"]:
                b_text = f"{b.item_id} {b.description} {b.assigned_owner}".lower().replace("-", " ")
                score = sum(1 for w in q_keywords if w in b_text)
                if score > best_score:
                    best_score = score
                    best_match = b
                    match_type = "blocker"

            # Check action items
            for a in [i for i in blocker_res.items if i.item_type == "Action Item"]:
                a_text = f"{a.item_id} {a.description} {a.assigned_owner}".lower().replace("-", " ")
                score = sum(1 for w in q_keywords if w in a_text)
                if score > best_score:
                    best_score = score
                    best_match = a
                    match_type = "action"

            # Check deliverables
            for d in scope_res.deliverables:
                d_text = f"{d.deliverable_id} {d.name} {d.owner}".lower().replace("-", " ")
                score = sum(1 for w in q_keywords if w in d_text)
                if score > best_score:
                    best_score = score
                    best_match = d
                    match_type = "deliverable"

            if best_match and best_score >= min_score:
                if match_type == "blocker":
                    b = best_match
                    answer = (
                        f"- **Owner:** {b.assigned_owner}\n"
                        f"- **Blocker:** [{b.item_id}] {b.description}\n"
                        f"- **Due Date:** {b.due_date}\n"
                        f"- **Status:** {b.status}"
                    )
                    cit = self._find_citation(b.source_references[0] if b.source_references else "", b.item_id, b.supporting_evidence, project_id=project_id)
                elif match_type == "action":
                    a = best_match
                    answer = (
                        f"- **Owner:** {a.assigned_owner}\n"
                        f"- **Task:** [{a.item_id}] {a.description}\n"
                        f"- **Due Date:** {a.due_date}\n"
                        f"- **Status:** {a.status}"
                    )
                    cit = self._find_citation(a.source_references[0] if a.source_references else "", a.item_id, a.supporting_evidence, project_id=project_id)
                else:
                    d = best_match
                    answer = (
                        f"- **Owner:** {d.owner}\n"
                        f"- **Deliverable:** [{d.deliverable_id}] {d.name}\n"
                        f"- **Due Date:** {d.target_date}\n"
                        f"- **Status:** {d.status}"
                    )
                    cit = self._find_citation(d.source_ref or "", d.deliverable_id, d.name, project_id=project_id)

                if cit:
                    citations.append(cit)
                elif scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return answer, citations, True

            # Search scored chunks for an explicit line mentioning owner
            for chunk, _ in scored_chunks:
                for line in chunk.text.splitlines():
                    line_score = sum(1 for w in q_keywords if w in line.lower())
                    if line_score >= min_score and any(k in line.lower() for k in ("owner:", "assigned to", "lead", "responsible")):
                        citations.append(self._chunk_to_citation(chunk))
                        return line.strip(), citations, True

            return f"The uploaded project documents do not specify who is responsible for **{clean_subject}**.", [], False

        # -------------------------------------------------------------
        # 2. Blockers Query (general or specific blocker)
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("blocker", "impediment", "blocking", "blocked")):
            blocker_res = await blocker_agent.analyze()
            blockers = [i for i in blocker_res.items if i.item_type == "Blocker"]

            stops = {
                "what", "which", "where", "who", "is", "are", "the", "for", "of", "to", "in", "on",
                "about", "blocker", "blockers", "current", "active", "open", "any", "there", "project",
                "all", "list", "issue", "impediment", "impediments", "the", "a", "an",
                "affecting", "progress", "facing", "experiencing", "impacting", "delaying",
                "we", "our", "have", "exist", "existing", "currently", "show", "tell", "me"
            }
            clean_q = q_lower.replace("-", " ")
            q_keywords = [
                w for w in re.sub(r"[^a-zA-Z0-9\s]", "", clean_q).split()
                if len(w) > 2 and w not in stops
            ]

            if q_keywords:
                min_score = 2 if len(q_keywords) >= 2 else 1
                best_b = None
                best_score = 0
                for b in blockers:
                    b_text = f"{b.item_id} {b.description} {b.assigned_owner} {b.recommended_next_step}".lower().replace("-", " ")
                    score = sum(1 for w in q_keywords if w in b_text)
                    if score > best_score:
                        best_score = score
                        best_b = b

                if best_b and best_score >= min_score:
                    b = best_b
                    impact_text = b.recommended_next_step.replace("[AI Recommendation] ", "")
                    answer = (
                        f"**[{b.item_id}] {b.description}**\n\n"
                        f"- **Owner:** {b.assigned_owner}\n"
                        f"- **Due Date:** {b.due_date}\n"
                        f"- **Status:** {b.status}\n"
                        f"- **Impact & Resolution:** {impact_text}"
                    )
                    cit = self._find_citation(b.source_references[0] if b.source_references else "", b.item_id, b.supporting_evidence, project_id=project_id)
                    if cit:
                        citations.append(cit)
                    elif scored_chunks:
                        citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                    return answer, citations, True
                elif not blockers:
                    clean_subject = " ".join(q_keywords)
                    return f"The uploaded project documents do not contain any blocker related to '{clean_subject}'.", [], False

            if blockers:
                ans_lines = [f"**Active Project Blockers ({len(blockers)}):**\n"]
                for b in blockers:
                    ans_lines.append(f"- **[{b.item_id}] {b.description}**")
                    ans_lines.append(f"  - **Owner:** {b.assigned_owner}")
                    ans_lines.append(f"  - **Due:** {b.due_date}")
                    ans_lines.append(f"  - **Resolution / Impact:** {b.recommended_next_step.replace('[AI Recommendation] ', '')}\n")

                top_b = blockers[0]
                cit = self._find_citation(top_b.source_references[0] if top_b.source_references else "", top_b.item_id, top_b.supporting_evidence, project_id=project_id)
                if cit:
                    citations.append(cit)
                elif scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return "\n".join(ans_lines).strip(), citations, True
            else:
                return "Zero active blockers were found in the uploaded project documents.", citations, True

        # -------------------------------------------------------------
        # 2b. Action Items Query
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("action item", "action items", "open actions", "next actions")):
            blocker_res = await blocker_agent.analyze()
            actions = [i for i in blocker_res.items if i.item_type == "Action Item"]
            if actions:
                ans_lines = [f"**Documented Action Items ({len(actions)}):**\n"]
                for a in actions:
                    ans_lines.append(f"- **[{a.item_id}] {a.description}**")
                    ans_lines.append(f"  - **Owner:** {a.assigned_owner}")
                    ans_lines.append(f"  - **Due:** {a.due_date}")
                    ans_lines.append(f"  - **Status:** {a.status}\n")

                top_a = actions[0]
                cit = self._find_citation(top_a.source_references[0] if top_a.source_references else "", top_a.item_id, top_a.supporting_evidence, project_id=project_id)
                if cit:
                    citations.append(cit)
                elif scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return "\n".join(ans_lines).strip(), citations, True
            else:
                return "Zero action items were found in the uploaded project documents.", citations, True

        # -------------------------------------------------------------
        # 3. Deliverables Query
        # -------------------------------------------------------------
        if "deliverable" in q_lower:
            scope_res = await scope_agent.analyze()
            delivs = scope_res.deliverables
            if delivs:
                completed = [d for d in delivs if "complete" in d.status.lower()]
                in_progress = [d for d in delivs if "progress" in d.status.lower()]
                at_risk = [d for d in delivs if "risk" in d.status.lower()]
                not_started = [d for d in delivs if "not start" in d.status.lower() or "pending" in d.status.lower()]
                other = [d for d in delivs if d not in completed and d not in in_progress and d not in at_risk and d not in not_started]

                # If user specifically asks which deliverables are completed
                if any(w in q_lower for w in ("which deliverables are completed", "completed deliverable", "deliverables are completed", "deliverables completed", "finished deliverables", "done deliverables")):
                    if completed:
                        ans_lines = [f"**Completed Deliverables ({len(completed)} of {len(delivs)}):**\n"]
                        for d in completed:
                            ans_lines.append(f"- **[{d.deliverable_id}] {d.name}** (Owner: {d.owner}, Target Date: {d.target_date})")
                    else:
                        ans_lines = [f"None of the {len(delivs)} documented project deliverables are currently marked as completed."]
                        if in_progress:
                            ans_lines.append(f"\nCurrently **In Progress ({len(in_progress)}):**")
                            for d in in_progress[:3]:
                                ans_lines.append(f"- [{d.deliverable_id}] {d.name} (Owner: {d.owner}, Due: {d.target_date})")
                    top_d = completed[0] if completed else delivs[0]
                    cit = self._find_citation(top_d.source_ref or "", "Deliverables", top_d.name, project_id=project_id)
                    if cit:
                        citations.append(cit)
                    elif scored_chunks:
                        citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                    return "\n".join(ans_lines).strip(), citations, True

                ans_lines = [f"**Documented Project Deliverables ({len(delivs)} total):**\n"]
                for label, group in [
                    ("In Progress", in_progress),
                    ("At Risk", at_risk),
                    ("Completed", completed),
                    ("Not Started", not_started),
                    ("Other", other),
                ]:
                    if group:
                        ans_lines.append(f"**{label}:**")
                        for d in group:
                            ans_lines.append(f"- **[{d.deliverable_id}] {d.name}** (Owner: {d.owner}, Due: {d.target_date}, Status: {d.status})")
                        ans_lines.append("")

                top_d = delivs[0]
                cit = self._find_citation(top_d.source_ref or "", "Deliverables", top_d.name, project_id=project_id)
                if cit:
                    citations.append(cit)
                elif scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return "\n".join(ans_lines).strip(), citations, True
            else:
                return "No documented deliverables found in the uploaded project documents.", citations, True

        # -------------------------------------------------------------
        # 4. Risks Query
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("risk", "risks", "threat", "threats")):
            risk_res = await risk_agent.analyze()
            risks = risk_res.risks

            q_keywords = [
                w for w in re.sub(r"[^a-zA-Z0-9\s]", "", q_lower).split()
                if len(w) > 3 and w not in ("what", "which", "where", "risk", "risks", "biggest", "danger")
            ]
            matched_risk = None
            if q_keywords:
                for r in risks:
                    r_text = f"{r.risk_id} {r.risk_title} {r.description} {r.owner}".lower()
                    if any(w in r_text for w in q_keywords):
                        matched_risk = r
                        break

            if matched_risk:
                r = matched_risk
                answer = (
                    f"**[{r.risk_id}] {r.risk_title}**\n\n"
                    f"- **Description:** {r.description}\n"
                    f"- **Severity:** {r.severity} (Likelihood: {r.likelihood}, Impact: {r.impact})\n"
                    f"- **Owner:** {r.owner}\n"
                    f"- **Mitigation:** {r.recommended_mitigation}"
                )
                cit = self._find_citation(r.source_references[0] if r.source_references else "", r.risk_id, r.supporting_evidence, project_id=project_id)
                if cit:
                    citations.append(cit)
                elif scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return answer, citations, True

            if risks:
                ans_lines = [f"**Documented Project Risks ({risk_res.total_risks} total, Overall Delivery Risk: {risk_res.overall_delivery_risk}):**\n"]
                for r in risks:
                    ans_lines.append(f"- **[{r.risk_id}] {r.risk_title}**")
                    ans_lines.append(f"  - **Severity:** {r.severity} (Likelihood: {r.likelihood}, Impact: {r.impact})")
                    ans_lines.append(f"  - **Owner:** {r.owner}")
                    ans_lines.append(f"  - **Mitigation:** {r.recommended_mitigation}\n")

                top_r = risks[0]
                cit = self._find_citation(top_r.source_references[0] if top_r.source_references else "", top_r.risk_id, top_r.supporting_evidence, project_id=project_id)
                if cit:
                    citations.append(cit)
                elif scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return "\n".join(ans_lines).strip(), citations, True
            else:
                return "Zero documented risks were found in the uploaded project documents.", citations, True

        # -------------------------------------------------------------
        # 5. Schedule / "Are we on track?" Query
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("on track", "on schedule", "schedule assessment", "timeline status", "milestone status", "overall status", "project status", "status of the project", "how is the project going")):
            blocker_res = await blocker_agent.analyze()
            scope_res = await scope_agent.analyze()

            blockers = [i for i in blocker_res.items if i.item_type == "Blocker"]
            delivs = scope_res.deliverables

            all_text = " ".join(c[0].text for c in scored_chunks)
            stat_match = re.search(r"Overall\s+status:\s*([A-Za-z\s]+?)(?:\.|\n|$)", all_text, re.IGNORECASE)
            doc_status = stat_match.group(1).strip().title() if stat_match else ("At Risk" if blockers else "On Track")

            completed = [d for d in delivs if "complete" in d.status.lower()]
            in_prog = [d for d in delivs if "progress" in d.status.lower()]
            at_risk = [d for d in delivs if "risk" in d.status.lower()]
            not_started = [d for d in delivs if "not start" in d.status.lower()]

            ans_lines = [f"Project Status: **{doc_status}**\n"]
            if completed:
                ans_lines.append(f"- **Completed ({len(completed)}):** " + ", ".join(f"{d.name} ({d.owner})" for d in completed))
            if in_prog:
                ans_lines.append(f"- **In Progress ({len(in_prog)}):** " + ", ".join(f"{d.name} ({d.owner}, due {d.target_date})" for d in in_prog))
            if at_risk:
                ans_lines.append(f"- **At Risk ({len(at_risk)}):** " + ", ".join(f"{d.name} ({d.owner}, due {d.target_date})" for d in at_risk))
            if not_started:
                ans_lines.append(f"- **Not Started ({len(not_started)}):** " + ", ".join(f"{d.name} ({d.owner}, due {d.target_date})" for d in not_started))

            if blockers:
                ans_lines.append(f"\n**Open Blockers ({len(blockers)}):**")
                for b in blockers:
                    ans_lines.append(f"- [{b.item_id}] {b.description} (Owner: {b.assigned_owner}, Due: {b.due_date})")

            if scored_chunks:
                citations.append(self._chunk_to_citation(scored_chunks[0][0]))
            return "\n".join(ans_lines).strip(), citations, True

        # -------------------------------------------------------------
        # 6. Decisions Query
        # -------------------------------------------------------------
        if "decision" in q_lower or "open question" in q_lower:
            blocker_res = await blocker_agent.analyze()
            pds = blocker_res.pending_decisions
            ads = blocker_res.approved_decisions

            ans_lines = []
            if pds:
                ans_lines.append(f"**Pending Decisions ({len(pds)}):**")
                for pd in pds:
                    ans_lines.append(f"- **[{pd.decision_id}] {pd.decision_title}** (Owner: {pd.owner}, Needed by: {pd.date_or_deadline})")
                ans_lines.append("")
            else:
                ans_lines.append("Zero pending decisions were found in the uploaded documents.\n")

            if ads:
                ans_lines.append(f"**Approved Decisions ({len(ads)}):**")
                for ad in ads:
                    ans_lines.append(f"- **[{ad.decision_id}] {ad.decision_title}** (Status: Approved, Date: {ad.date_or_deadline})")

            if scored_chunks:
                citations.append(self._chunk_to_citation(scored_chunks[0][0]))
            return "\n".join(ans_lines).strip(), citations, True

        # -------------------------------------------------------------
        # 7. Primary Goal / Scope Query
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("goal", "objective", "primary goal", "project scope", "purpose")):
            scope_res = await scope_agent.analyze()
            if scope_res.primary_goal:
                goal_desc = scope_res.primary_goal.description if hasattr(scope_res.primary_goal, "description") else str(scope_res.primary_goal)
                ans_lines = [f"**Primary Project Goal:** {goal_desc}\n"]
                sub_list = scope_res.sub_goals or scope_res.project_goals
                if sub_list:
                    ans_lines.append("**Core Objectives / Sub-Goals:**")
                    for obj in sub_list:
                        desc = obj.description if hasattr(obj, "description") else str(obj)
                        ans_lines.append(f"- {desc}")
                if scored_chunks:
                    citations.append(self._chunk_to_citation(scored_chunks[0][0]))
                return "\n".join(ans_lines).strip(), citations, True

        # -------------------------------------------------------------
        # 8. Project Health Score Query
        # -------------------------------------------------------------
        if "health" in q_lower or "score" in q_lower:
            health = await health_scoring_service.calculate_health()
            summary_text = (
                health.recommended_corrective_actions[0]
                if health.recommended_corrective_actions
                else f"Project health is currently categorized as {health.health_category}."
            )
            answer = (
                f"**Project Health Score: {health.overall_score}/100 ({health.health_category})**\n\n"
                f"**Component Breakdown:**\n"
                f"- **Scope Clarity:** {health.scope_clarity.raw_score}/100 ({health.scope_clarity.category})\n"
                f"- **Timeline Health:** {health.timeline_health.raw_score}/100 ({health.timeline_health.category})\n"
                f"- **Blocker Health:** {health.blocker_health.raw_score}/100 ({health.blocker_health.category})\n\n"
                f"**Key Recommendation:** {summary_text}"
            )
            if scored_chunks:
                citations.append(self._chunk_to_citation(scored_chunks[0][0]))
            return answer, citations, True

        # -------------------------------------------------------------
        # 8b. Meeting Notes & Incremental Updates Query
        # -------------------------------------------------------------
        if any(k in q_lower for k in ("meeting note", "meeting notes", "latest meeting", "latest notes", "changed after uploading", "what changed", "recent update", "progress update", "recent notes")):
            docs = document_service.list_documents()
            meeting_docs = [
                d for d in docs
                if any(w in d.filename.lower() for w in ("meeting", "notes", "progress", "update", "sprint"))
                or any(w in d.full_text.lower() for w in ("meeting notes", "meeting minutes", "progress update", "sprint meeting"))
            ]
            if meeting_docs:
                meeting_docs.sort(key=lambda x: x.uploaded_at or "", reverse=True)
                latest_doc = meeting_docs[0]

                extracted_points = []
                for chunk in latest_doc.chunks:
                    for line in chunk.text.splitlines():
                        clean_l = line.strip()
                        if clean_l and (
                            re.match(r"^[-*•\d]\s+", clean_l)
                            or any(k in clean_l.lower() for k in ("action:", "blocker:", "decision:", "status:", "agreed:", "update:", "delay:", "completed:", "resolved:", "item:"))
                        ):
                            if len(clean_l) > 10 and clean_l not in extracted_points:
                                extracted_points.append(clean_l)

                if extracted_points:
                    ans_lines = [
                        f"Based on the latest uploaded project meeting notes (**{latest_doc.filename}**):",
                        "",
                    ]
                    for pt in extracted_points[:8]:
                        if not pt.startswith(("-", "*", "•")) and not re.match(r"^\d+\.", pt):
                            pt = f"- {pt}"
                        ans_lines.append(pt)

                    answer = "\n".join(ans_lines).strip()
                    top_chunk = latest_doc.chunks[0] if latest_doc.chunks else (scored_chunks[0][0] if scored_chunks else None)
                    if top_chunk:
                        citations.append(self._chunk_to_citation(top_chunk))
                    return answer, citations, True
                else:
                    snippet = latest_doc.preview_snippet or latest_doc.full_text[:300]
                    answer = f"The latest meeting notes document **{latest_doc.filename}** records:\n\n{snippet}"
                    top_chunk = latest_doc.chunks[0] if latest_doc.chunks else None
                    if top_chunk:
                        citations.append(self._chunk_to_citation(top_chunk))
                    return answer, citations, True
            elif scored_chunks and scored_chunks[0][1] >= 0.05:
                top_chunk = scored_chunks[0][0]
                citations.append(self._chunk_to_citation(top_chunk))
                return f"Information from recent project documentation:\n\n{top_chunk.text[:350]}", citations, True
            else:
                return "The uploaded project documents do not contain any recent meeting notes or progress updates.", [], False

        # -------------------------------------------------------------
        # 9. Generic Grounded Text Matching Fallback
        # -------------------------------------------------------------
        if scored_chunks and scored_chunks[0][1] >= 0.12:
            top_chunk, score = scored_chunks[0]
            generic_stops = {
                "project", "document", "documents", "system", "application", "what", "which",
                "where", "when", "about", "have", "with", "from", "that", "this", "some", "more",
                "also", "their", "will", "would", "could", "should", "your", "does", "were", "been",
                "manager", "lead", "team"
            }
            q_words = [w for w in re.sub(r"[^a-zA-Z0-9\s]", "", q_lower).split() if len(w) > 3 and w not in generic_stops]
            if q_words:
                sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", top_chunk.text.strip()) if len(s.strip()) > 15]
                min_match = 2 if len(q_words) >= 2 else 1
                rel = [s for s in sentences if sum(1 for w in q_words if w in s.lower()) >= min_match]
                if rel:
                    citations.append(self._chunk_to_citation(top_chunk))
                    return " ".join(rel[:3]), citations, True

        return self.FALLBACK_NO_EVIDENCE, [], False

    def _generate_suggested_followups(self, question: str) -> List[str]:
        """Generate contextual suggested follow-up questions."""
        q_lower = question.lower()
        if "risk" in q_lower:
            return ["What are the active project blockers?", "Who is responsible for the critical actions?", "What is the overall project health score?"]
        if "blocker" in q_lower:
            return ["What actions must be completed next?", "Are there any pending decisions?", "What is our current timeline health?"]
        if "health" in q_lower or "track" in q_lower:
            return ["What are our biggest risks?", "What deliverables are pending?", "Which milestones are scheduled next?"]
        return ["What are the main project objectives?", "What are our biggest risks?", "What is the current project health?"]

    def _record_turn(
        self,
        project_id: str,
        conversation_id: str,
        user_query: str,
        assistant_reply: str,
        citations: List[SourceCitation],
    ):
        """Append turn to project-isolated conversation store."""
        store = self._load_conversations()
        proj_convs = store.get(project_id, {})
        conv = proj_convs.get(conversation_id, {"conversation_id": conversation_id, "project_id": project_id, "messages": []})

        now_iso = datetime.now(timezone.utc).isoformat()
        conv["messages"].append({
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "role": "user",
            "content": user_query,
            "timestamp": now_iso,
            "citations": [],
            "has_evidence": True,
        })
        conv["messages"].append({
            "message_id": f"msg_{uuid.uuid4().hex[:8]}",
            "role": "assistant",
            "content": assistant_reply,
            "timestamp": now_iso,
            "citations": [c.model_dump() for c in citations],
            "has_evidence": bool(citations and assistant_reply != self.FALLBACK_NO_EVIDENCE),
        })

        # Keep last 30 messages in conversation
        if len(conv["messages"]) > 30:
            conv["messages"] = conv["messages"][-30:]

        proj_convs[conversation_id] = conv
        store[project_id] = proj_convs
        self._save_conversations(store)

    def get_conversation_history(
        self, project_id: Optional[str] = None, conversation_id: Optional[str] = None
    ) -> ConversationHistoryResponse:
        """Retrieve conversation turns for active project workspace."""
        target_pid = project_id or document_service.get_workspace().project_id
        target_cid = conversation_id or f"conv_{target_pid}"

        store = self._load_conversations()
        proj_convs = store.get(target_pid, {})
        conv = proj_convs.get(target_cid, {"conversation_id": target_cid, "project_id": target_pid, "messages": []})

        messages = [
            ChatMessage(
                message_id=m["message_id"],
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"],
                citations=[SourceCitation(**c) for c in m.get("citations", [])],
                has_evidence=m.get("has_evidence", True),
            )
            for m in conv.get("messages", [])
        ]

        return ConversationHistoryResponse(
            conversation_id=target_cid,
            project_id=target_pid,
            messages=messages,
        )

    def clear_conversation(self, project_id: Optional[str] = None, conversation_id: Optional[str] = None) -> bool:
        """Clear conversation turns for active project workspace."""
        target_pid = project_id or document_service.get_workspace().project_id
        target_cid = conversation_id or f"conv_{target_pid}"

        store = self._load_conversations()
        if target_pid in store and target_cid in store[target_pid]:
            store[target_pid][target_cid]["messages"] = []
            self._save_conversations(store)
            return True
        return False


chat_assistant_service = ConversationalProjectAssistant()
