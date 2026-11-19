import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.schemas.milestone3_models import (
    HealthScoreDimension,
    HealthSnapshot,
    ProjectHealthResponse,
)
from app.services.document_service import document_service
from app.services.scope_agent import scope_agent
from app.services.risk_agent import risk_agent
from app.services.blocker_agent import blocker_agent


class ProjectHealthScoringService:
    """
    Deterministic mathematical composite project health scoring engine.
    Calculates transparent, explainable 0-100 scores across Scope Clarity (35%),
    Timeline Health (35%), and Blocker Health (30%), handles missing data gracefully,
    and maintains historical score snapshots per project workspace.
    """

    DEFAULT_WEIGHTS = {
        "scope_clarity": 0.35,
        "timeline_health": 0.35,
        "blocker_health": 0.30,
    }

    def __init__(self):
        self.history_file = settings.BASE_DIR / "data" / "health_history.json"
        self._ensure_storage()

    def _ensure_storage(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self._save_history({})

    def _load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_history(self, data: Dict[str, List[Dict[str, Any]]]):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_category(self, score: Optional[float]) -> str:
        """Map numeric score to standard project health category."""
        if score is None:
            return "Insufficient Data"
        if score >= 80.0:
            return "Healthy"
        elif score >= 60.0:
            return "Needs Attention"
        elif score >= 40.0:
            return "At Risk"
        else:
            return "Critical"

    async def calculate_health(
        self,
        document_id: Optional[str] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> ProjectHealthResponse:
        """
        Execute deterministic health scoring.
        Gathers evidence from Scope, Risk, and Blocker agents to compute dimensional and composite scores.
        """
        active_weights = dict(self.DEFAULT_WEIGHTS)
        if weights:
            # Normalize user-supplied weights
            total_w = sum(weights.values())
            if total_w > 0:
                active_weights = {k: round(v / total_w, 4) for k, v in weights.items()}

        workspace = document_service.get_workspace()
        project_id = workspace.project_id
        project_name = workspace.project_name or "Project Workspace"
        documents = document_service.list_documents()

        now_iso = datetime.now(timezone.utc).isoformat()

        # Handle Empty Workspace / Missing Data
        if not documents:
            dim_insufficient = HealthScoreDimension(
                dimension_name="N/A",
                weight=0.0,
                raw_score=0.0,
                weighted_score=0.0,
                category="Insufficient Data",
                explanation="No project documents uploaded in this workspace.",
                contributing_factors=[],
                critical_issues=["Workspace contains 0 ingested documents."],
            )
            return ProjectHealthResponse(
                project_id=project_id,
                project_name=project_name,
                calculated_at=now_iso,
                overall_score=None,
                health_category="Insufficient Data",
                is_insufficient_data=True,
                weights=active_weights,
                scope_clarity=dim_insufficient.model_copy(update={"dimension_name": "Scope Clarity", "weight": active_weights["scope_clarity"]}),
                timeline_health=dim_insufficient.model_copy(update={"dimension_name": "Timeline Health", "weight": active_weights["timeline_health"]}),
                blocker_health=dim_insufficient.model_copy(update={"dimension_name": "Blocker Health", "weight": active_weights["blocker_health"]}),
                critical_issues=["Upload project charter, requirements, or meeting minutes to compute health."],
                recommended_corrective_actions=["Ingest project documentation to establish baseline health score."],
                missing_information=["Project Charter", "Milestone Schedule", "Risk Register", "Meeting Minutes"],
                historical_snapshots=[],
            )

        # 1. Fetch agent intelligence
        scope_res = await scope_agent.analyze(document_id=document_id)
        risk_res = await risk_agent.analyze(document_id=document_id)
        blocker_res = await blocker_agent.analyze(document_id=document_id)

        missing_info: List[str] = []
        critical_issues: List[str] = []
        corrective_actions: List[str] = []

        # -------------------------------------------------------------
        # DIMENSION 1: Scope Clarity (Weight: 35%)
        # -------------------------------------------------------------
        scope_score = 0.0
        scope_factors: List[str] = []
        scope_issues: List[str] = []

        if scope_res.primary_goal:
            scope_score += 20.0
            scope_factors.append("Overarching primary project goal documented (+20 pts)")
        else:
            missing_info.append("Primary project goal definition")
            scope_issues.append("Primary project goal is undocumented (-20 pts)")

        if scope_res.sub_goals or scope_res.project_goals:
            count = len(scope_res.sub_goals) or len(scope_res.project_goals)
            pts = min(15.0, count * 5.0)
            scope_score += pts
            scope_factors.append(f"{count} supporting objectives/sub-goals documented (+{pts:.0f} pts)")
        else:
            missing_info.append("Supporting sub-goals or specific objectives")
            scope_issues.append("No supporting sub-goals found (-15 pts)")

        in_scope = sum(1 for s in scope_res.scope_items if s.category == "In-Scope")
        out_scope = sum(1 for s in scope_res.scope_items if s.category == "Out-of-Scope")
        if in_scope > 0 or out_scope > 0:
            pts = 10.0 if (in_scope > 0 and out_scope > 0) else 10.0
            scope_score += pts
            scope_factors.append(f"Scope boundaries defined ({in_scope} in-scope, {out_scope} out-of-scope) (+{pts:.0f} pts)")
        else:
            missing_info.append("Explicit In-Scope vs Out-of-Scope boundaries")
            scope_issues.append("Scope boundaries are not formally delineated (-10 pts)")

        if scope_res.functional_requirements:
            count = len(scope_res.functional_requirements)
            pts = min(15.0, count * 3.0)
            scope_score += pts
            scope_factors.append(f"{count} functional requirements documented (+{pts:.0f} pts)")

        if scope_res.deliverables:
            pts = min(15.0, len(scope_res.deliverables) * 3.0)
            scope_score += pts
            scope_factors.append(f"{len(scope_res.deliverables)} project deliverables documented (+{pts:.0f} pts)")
        else:
            missing_info.append("Documented project deliverables list")
            scope_issues.append("Project deliverables list missing (-15 pts)")

        if scope_res.milestones:
            pts = min(10.0, len(scope_res.milestones) * 3.0)
            scope_score += pts
            scope_factors.append(f"{len(scope_res.milestones)} milestone schedule items tracked (+{pts:.0f} pts)")
        else:
            missing_info.append("Milestone target schedule")
            scope_issues.append("Milestone target schedule missing (-10 pts)")

        if scope_res.dependencies:
            pts = min(10.0, len(scope_res.dependencies) * 3.0)
            scope_score += pts
            scope_factors.append(f"{len(scope_res.dependencies)} task dependencies identified (+{pts:.0f} pts)")

        scope_score = min(100.0, max(0.0, round(scope_score, 1)))
        scope_weighted = round(scope_score * active_weights["scope_clarity"], 2)

        scope_dim = HealthScoreDimension(
            dimension_name="Scope Clarity",
            weight=active_weights["scope_clarity"],
            raw_score=scope_score,
            weighted_score=scope_weighted,
            category=self.get_category(scope_score),
            explanation=f"Evaluated goal hierarchy, boundaries, requirements, deliverables, and milestones: {scope_score}/100.",
            contributing_factors=scope_factors,
            critical_issues=scope_issues,
        )

        # -------------------------------------------------------------
        # DIMENSION 2: Timeline Health (Weight: 35%)
        # -------------------------------------------------------------
        timeline_score = 100.0
        timeline_factors: List[str] = []
        timeline_issues: List[str] = []

        # Penalties for schedule-specific risks
        schedule_risks = [r for r in risk_res.risks if r.risk_category == "Schedule"]
        crit_schedule_risks = [r for r in schedule_risks if r.severity in ("Critical", "High")]
        if crit_schedule_risks:
            penalty = min(40.0, len(crit_schedule_risks) * 15.0)
            timeline_score -= penalty
            timeline_issues.append(f"{len(crit_schedule_risks)} high/critical schedule risks detected (-{penalty:.0f} pts)")
            for r in crit_schedule_risks:
                critical_issues.append(f"Schedule Risk [{r.risk_id}]: {r.risk_title}")
                corrective_actions.append(f"Mitigate {r.risk_title}: {r.recommended_mitigation[:120]}")
        else:
            timeline_factors.append("No critical schedule delay risks detected")

        # Dependency bottlenecks affecting timeline
        dep_risks = [r for r in risk_res.risks if r.risk_category == "Dependency"]
        if dep_risks:
            penalty = min(20.0, len(dep_risks) * 10.0)
            timeline_score -= penalty
            timeline_issues.append(f"{len(dep_risks)} dependency bottleneck risks (-{penalty:.0f} pts)")
        else:
            timeline_factors.append("No blocking dependency risks detected")

        # Missing explicit dates on deliverables
        unspecified_dates = sum(1 for d in scope_res.deliverables if not d.target_date or d.target_date.upper() == "UNKNOWN")
        if unspecified_dates > 0:
            penalty = min(15.0, unspecified_dates * 3.0)
            timeline_score -= penalty
            timeline_issues.append(f"{unspecified_dates} deliverables lack explicit target dates (-{penalty:.0f} pts)")
            missing_info.append(f"{unspecified_dates} deliverable target dates")
        elif scope_res.deliverables:
            timeline_factors.append("All documented deliverables have explicit target dates")

        timeline_score = min(100.0, max(0.0, round(timeline_score, 1)))
        timeline_weighted = round(timeline_score * active_weights["timeline_health"], 2)

        timeline_dim = HealthScoreDimension(
            dimension_name="Timeline Health",
            weight=active_weights["timeline_health"],
            raw_score=timeline_score,
            weighted_score=timeline_weighted,
            category=self.get_category(timeline_score),
            explanation=f"Evaluated schedule risks, dependency delays, and milestone target dates: {timeline_score}/100.",
            contributing_factors=timeline_factors,
            critical_issues=timeline_issues,
        )

        # -------------------------------------------------------------
        # DIMENSION 3: Blocker Health (Weight: 30%)
        # -------------------------------------------------------------
        blocker_score = 100.0
        blocker_factors: List[str] = []
        blocker_issues: List[str] = []

        # Deduplicate blockers to avoid counting same issue twice
        active_blockers = [i for i in blocker_res.items if i.item_type == "Blocker"]
        seen_blocker_desc = set()
        unique_blockers = []
        for b in active_blockers:
            key = b.description[:40].lower()
            if key not in seen_blocker_desc:
                seen_blocker_desc.add(key)
                unique_blockers.append(b)

        if unique_blockers:
            penalty = min(45.0, len(unique_blockers) * 15.0)
            blocker_score -= penalty
            blocker_issues.append(f"{len(unique_blockers)} active blockers unresolved (-{penalty:.0f} pts)")
            for b in unique_blockers:
                critical_issues.append(f"Blocker [{b.item_id}]: {b.description[:80]}")
                corrective_actions.append(f"Unblock [{b.item_id}]: {b.recommended_next_step[:120]}")
        else:
            blocker_factors.append("Zero active blockers reported in documents")

        # Overdue action items
        if blocker_res.overdue_count > 0:
            penalty = min(20.0, blocker_res.overdue_count * 10.0)
            blocker_score -= penalty
            blocker_issues.append(f"{blocker_res.overdue_count} overdue action items past deadline (-{penalty:.0f} pts)")
        else:
            blocker_factors.append("Zero overdue action items")

        # Pending unresolved decisions
        pending_dec_count = len(blocker_res.pending_decisions)
        if pending_dec_count > 0:
            penalty = min(15.0, pending_dec_count * 5.0)
            blocker_score -= penalty
            blocker_issues.append(f"{pending_dec_count} unresolved pending decisions (-{penalty:.0f} pts)")
            for pd in blocker_res.pending_decisions:
                corrective_actions.append(f"Resolve Decision [{pd.decision_id}]: {pd.decision_title}")
        else:
            blocker_factors.append("All recorded project decisions are approved and resolved")

        # Unassigned action items
        if blocker_res.unassigned_count > 0:
            penalty = min(10.0, blocker_res.unassigned_count * 2.0)
            blocker_score -= penalty
            blocker_issues.append(f"{blocker_res.unassigned_count} action items lack designated owners (-{penalty:.0f} pts)")
            corrective_actions.append(f"Assign responsible owners to {blocker_res.unassigned_count} unassigned action items.")

        blocker_score = min(100.0, max(0.0, round(blocker_score, 1)))
        blocker_weighted = round(blocker_score * active_weights["blocker_health"], 2)

        blocker_dim = HealthScoreDimension(
            dimension_name="Blocker Health",
            weight=active_weights["blocker_health"],
            raw_score=blocker_score,
            weighted_score=blocker_weighted,
            category=self.get_category(blocker_score),
            explanation=f"Evaluated active blockers, overdue tasks, pending decisions, and unassigned actions: {blocker_score}/100.",
            contributing_factors=blocker_factors,
            critical_issues=blocker_issues,
        )

        # -------------------------------------------------------------
        # COMPOSITE HEALTH SCORE
        # Formula: (Scope * 0.35) + (Timeline * 0.35) + (Blocker * 0.30)
        # -------------------------------------------------------------
        overall = round(scope_weighted + timeline_weighted + blocker_weighted, 1)
        overall_category = self.get_category(overall)

        # Check if missing data makes score inconclusive
        is_insufficient = len(missing_info) >= 4 and len(documents) <= 1

        # -------------------------------------------------------------
        # PERSIST HISTORICAL SNAPSHOT
        # -------------------------------------------------------------
        snapshot = HealthSnapshot(
            snapshot_id=f"snap_{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            timestamp=now_iso,
            overall_score=overall if not is_insufficient else None,
            health_category=overall_category if not is_insufficient else "Insufficient Data",
            scope_score=scope_score,
            timeline_score=timeline_score,
            blocker_score=blocker_score,
        )

        history_store = self._load_history()
        proj_history = history_store.get(project_id, [])
        proj_history.append(snapshot.model_dump())
        # Keep last 15 snapshots
        if len(proj_history) > 15:
            proj_history = proj_history[-15:]
        history_store[project_id] = proj_history
        self._save_history(history_store)

        historical_snapshots = [HealthSnapshot(**s) for s in proj_history]

        return ProjectHealthResponse(
            project_id=project_id,
            project_name=project_name,
            calculated_at=now_iso,
            overall_score=overall if not is_insufficient else None,
            health_category=overall_category if not is_insufficient else "Insufficient Data",
            is_insufficient_data=is_insufficient,
            weights=active_weights,
            scope_clarity=scope_dim,
            timeline_health=timeline_dim,
            blocker_health=blocker_dim,
            critical_issues=critical_issues[:6],
            recommended_corrective_actions=corrective_actions[:6],
            missing_information=missing_info,
            historical_snapshots=historical_snapshots,
        )

    def get_history(self, project_id: Optional[str] = None) -> List[HealthSnapshot]:
        """Retrieve recorded historical health score snapshots for the project."""
        target_pid = project_id or document_service.get_workspace().project_id
        history_store = self._load_history()
        raw_list = history_store.get(target_pid, [])
        return [HealthSnapshot(**s) for s in raw_list]


health_scoring_service = ProjectHealthScoringService()
