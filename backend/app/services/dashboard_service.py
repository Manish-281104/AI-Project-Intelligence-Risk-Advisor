import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.schemas.dashboard_models import (
    ProjectDashboardSummary,
    DashboardHealth,
    HealthIndicator,
    DashboardScope,
    DashboardDeliverable,
    DashboardMilestone,
    DashboardRisks,
    DashboardRiskItem,
    DashboardBlockers,
    DashboardBlockerItem,
    DashboardActionItems,
    DashboardActionItem,
    DashboardProgress,
    DashboardDocumentSummary,
)
from app.services.document_service import document_service
from app.services.health_scoring_service import health_scoring_service
from app.services.scope_agent import scope_agent
from app.services.risk_agent import risk_agent
from app.services.blocker_agent import blocker_agent

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Service generating consolidated project intelligence for the
    Milestone 4 Project Insights and Risk Summary Dashboard.
    Integrates actual outputs from all multi-agent services, health scoring engine,
    and workspace document index with zero synthetic data.
    """

    async def get_dashboard_summary(
        self, document_id: Optional[str] = None
    ) -> ProjectDashboardSummary:
        workspace = document_service.get_workspace()
        docs = document_service.list_documents()

        if document_id:
            docs = [d for d in docs if d.document_id == document_id]

        now_iso = datetime.now(timezone.utc).isoformat()

        doc_summaries: List[DashboardDocumentSummary] = [
            DashboardDocumentSummary(
                document_id=d.document_id,
                filename=d.filename,
                file_type=d.file_type,
                file_size_kb=d.file_size_kb,
                uploaded_at=d.uploaded_at,
                chunk_count=d.chunk_count,
                char_count=d.char_count,
            )
            for d in docs
        ]

        if not docs:
            return ProjectDashboardSummary(
                project_id=workspace.project_id,
                project_name=workspace.project_name,
                client=workspace.client,
                document_count=0,
                documents=[],
                has_documents=False,
                health=None,
                scope=None,
                risks=None,
                blockers=None,
                action_items=None,
                progress=None,
                timestamp=now_iso,
            )

        # 1. Project Health
        health_res = await health_scoring_service.calculate_health(document_id=document_id)
        raw_score = health_res.overall_score
        if raw_score >= 80:
            health_status = "Healthy"
        elif raw_score >= 60:
            health_status = "Needs Attention"
        else:
            health_status = "At Risk"

        indicators = [
            HealthIndicator(
                dimension="Scope Clarity",
                raw_score=health_res.scope_clarity.raw_score,
                weight=health_res.scope_clarity.weight,
                weighted_score=health_res.scope_clarity.weighted_score,
                category=health_res.scope_clarity.category,
            ),
            HealthIndicator(
                dimension="Timeline Health",
                raw_score=health_res.timeline_health.raw_score,
                weight=health_res.timeline_health.weight,
                weighted_score=health_res.timeline_health.weighted_score,
                category=health_res.timeline_health.category,
            ),
            HealthIndicator(
                dimension="Blocker Health",
                raw_score=health_res.blocker_health.raw_score,
                weight=health_res.blocker_health.weight,
                weighted_score=health_res.blocker_health.weighted_score,
                category=health_res.blocker_health.category,
            ),
        ]

        dashboard_health = DashboardHealth(
            overall_score=health_res.overall_score,
            status=health_status,
            health_category=health_res.health_category,
            indicators=indicators,
            recommendations=health_res.recommended_corrective_actions,
            missing_data_alerts=health_res.missing_information,
        )

        # 2. Scope & Deliverables
        scope_res = await scope_agent.analyze(document_id=document_id)
        main_goal_desc = "Main project goal not explicitly identified in documents."
        if scope_res.primary_goal:
            main_goal_desc = (
                scope_res.primary_goal.description
                if hasattr(scope_res.primary_goal, "description")
                else str(scope_res.primary_goal)
            )

        objectives: List[str] = []
        sub_list = scope_res.sub_goals or scope_res.project_goals
        for obj in sub_list:
            desc = obj.description if hasattr(obj, "description") else str(obj)
            objectives.append(desc)

        deliverables: List[DashboardDeliverable] = [
            DashboardDeliverable(
                deliverable_id=d.deliverable_id or f"DEL-{idx+1:02d}",
                name=d.name,
                owner=d.owner or "UNKNOWN",
                target_date=d.target_date or "UNKNOWN",
                status=d.status or "Pending",
                source_ref=d.source_ref,
            )
            for idx, d in enumerate(scope_res.deliverables)
        ]

        milestones: List[DashboardMilestone] = [
            DashboardMilestone(
                milestone_id=m.milestone_id or f"M-{idx+1:02d}",
                name=m.name,
                target_date=m.target_date or "UNKNOWN",
                owner=m.owner or "UNKNOWN",
                status=m.status or "Planned",
            )
            for idx, m in enumerate(scope_res.milestones)
        ]

        timeline_summary = None
        if milestones or deliverables:
            timeline_summary = f"{len(milestones)} milestones planned; {len(deliverables)} key deliverables tracked."

        dashboard_scope = DashboardScope(
            main_goal=main_goal_desc,
            objectives=objectives,
            key_deliverables=deliverables,
            milestones=milestones,
            timeline_summary=timeline_summary,
        )

        # 3. Risks & Delivery Forecasting
        risk_res = await risk_agent.analyze(document_id=document_id)
        risk_items: List[DashboardRiskItem] = []
        high_cnt = 0
        med_cnt = 0
        low_cnt = 0

        for r in risk_res.risks:
            sev = (r.severity or "Medium").capitalize()
            if sev == "High":
                high_cnt += 1
            elif sev == "Low":
                low_cnt += 1
            else:
                med_cnt += 1

            source_doc = r.source_references[0] if r.source_references else None

            risk_items.append(
                DashboardRiskItem(
                    risk_id=r.risk_id,
                    title=r.risk_title,
                    description=r.description,
                    severity=sev,
                    likelihood=r.likelihood or "Medium",
                    impact=r.impact or "Medium",
                    owner=r.owner or "Unassigned",
                    evidence=r.supporting_evidence,
                    source_document=source_doc,
                    recommended_mitigation=r.recommended_mitigation,
                )
            )

        dashboard_risks = DashboardRisks(
            total_risks=risk_res.total_risks,
            overall_severity=risk_res.overall_delivery_risk,
            high_count=high_cnt,
            medium_count=med_cnt,
            low_count=low_cnt,
            items=risk_items,
        )

        # 4. Blockers & Action Items
        blocker_res = await blocker_agent.analyze(document_id=document_id)
        blocker_items: List[DashboardBlockerItem] = []
        action_items: List[DashboardActionItem] = []
        open_blockers = 0
        resolved_blockers = 0
        pending_actions = 0
        completed_actions = 0
        unassigned_actions = 0

        for item in blocker_res.items:
            source_doc = item.source_references[0] if item.source_references else None
            is_unassigned = not item.assigned_owner or item.assigned_owner.upper() in ("UNKNOWN", "UNASSIGNED", "NONE")

            if item.item_type == "Blocker":
                if "resolved" in item.status.lower() or "closed" in item.status.lower():
                    resolved_blockers += 1
                else:
                    open_blockers += 1

                res_step = item.recommended_next_step.replace("[AI Recommendation] ", "") if item.recommended_next_step else None

                blocker_items.append(
                    DashboardBlockerItem(
                        item_id=item.item_id,
                        description=item.description,
                        owner=item.assigned_owner or "UNKNOWN",
                        due_date=item.due_date or "UNKNOWN",
                        status=item.status or "Open",
                        resolution=res_step,
                        evidence=item.supporting_evidence,
                        source_document=source_doc,
                    )
                )
            else:
                # Action Item
                if "complete" in item.status.lower() or "done" in item.status.lower() or "closed" in item.status.lower():
                    completed_actions += 1
                else:
                    pending_actions += 1

                if is_unassigned:
                    unassigned_actions += 1

                action_items.append(
                    DashboardActionItem(
                        item_id=item.item_id,
                        description=item.description,
                        owner=item.assigned_owner or "UNKNOWN",
                        due_date=item.due_date or "UNKNOWN",
                        status=item.status or "Pending",
                        priority=item.priority or "Medium",
                        evidence=item.supporting_evidence,
                        source_document=source_doc,
                    )
                )

        dashboard_blockers = DashboardBlockers(
            total_blockers=len(blocker_items),
            open_count=open_blockers,
            resolved_count=resolved_blockers,
            items=blocker_items,
        )

        dashboard_actions = DashboardActionItems(
            total_actions=len(action_items),
            pending_count=pending_actions,
            completed_count=completed_actions,
            unassigned_count=unassigned_actions,
            items=action_items,
        )

        # 5. Progress Metrics
        total_delivs = len(deliverables)
        comp_delivs = sum(1 for d in deliverables if "complete" in d.status.lower())
        prog_delivs = sum(1 for d in deliverables if "progress" in d.status.lower())
        risk_delivs = sum(1 for d in deliverables if "risk" in d.status.lower())

        pct = round((comp_delivs / total_delivs) * 100, 1) if total_delivs > 0 else 0.0

        pending_acts = [
            f"[{a.item_id}] {a.description} (Owner: {a.owner}, Due: {a.due_date})"
            for a in action_items
            if "complete" not in a.status.lower()
        ]

        dashboard_progress = DashboardProgress(
            total_deliverables=total_delivs,
            completed_deliverables=comp_delivs,
            in_progress_deliverables=prog_delivs,
            at_risk_deliverables=risk_delivs,
            completion_percentage=pct,
            overall_status=health_status,
            pending_activities=pending_acts[:10],
        )

        return ProjectDashboardSummary(
            project_id=workspace.project_id,
            project_name=workspace.project_name or workspace.project_id,
            client=workspace.client,
            document_count=len(docs),
            documents=doc_summaries,
            has_documents=True,
            health=dashboard_health,
            scope=dashboard_scope,
            risks=dashboard_risks,
            blockers=dashboard_blockers,
            action_items=dashboard_actions,
            progress=dashboard_progress,
            timestamp=now_iso,
        )


dashboard_service = DashboardService()
