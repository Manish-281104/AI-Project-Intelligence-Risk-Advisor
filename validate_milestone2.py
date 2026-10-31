import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.delete("/api/project/reset")
sample_dir = Path("sample_documents")

print("=== 1. Testing Format Uploads ===")
uploaded_doc_ids = []
for fname in ["project_charter.pdf", "meeting_minutes.docx", "sprint_tasks.csv", "architecture_risks.txt"]:
    fpath = sample_dir / fname
    mime = (
        "application/pdf"
        if fname.endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if fname.endswith(".docx")
        else "text/csv"
        if fname.endswith(".csv")
        else "text/plain"
    )
    with open(fpath, "rb") as f:
        res = client.post("/api/documents/upload", files={"file": (fname, f, mime)})
    print(f"Upload {fname}: status={res.status_code}, chunks={res.json().get('chunk_count')}")
    assert res.status_code == 201
    uploaded_doc_ids.append(res.json()["document_id"])

print("\n=== 2. Testing Edge Cases ===")
# Empty file
with open(sample_dir / "empty.txt", "rb") as f:
    r_empty = client.post("/api/documents/upload", files={"file": ("empty.txt", f, "text/plain")})
print("Empty file rejection:", r_empty.status_code, r_empty.json().get("detail"))
assert r_empty.status_code == 400

# Unsupported format
with open(sample_dir / "unsupported.png", "rb") as f:
    r_unsupported = client.post("/api/documents/upload", files={"file": ("unsupported.png", f, "image/png")})
print("Unsupported format rejection:", r_unsupported.status_code, r_unsupported.json().get("detail"))
assert r_unsupported.status_code == 400

# Corrupted PDF
with open(sample_dir / "corrupted.pdf", "rb") as f:
    r_corrupt = client.post("/api/documents/upload", files={"file": ("corrupted.pdf", f, "application/pdf")})
print("Corrupted PDF rejection:", r_corrupt.status_code, r_corrupt.json().get("detail"))
assert r_corrupt.status_code == 400

# Blank scanned PDF
with open(sample_dir / "blank_scanned.pdf", "rb") as f:
    r_blank = client.post("/api/documents/upload", files={"file": ("blank_scanned.pdf", f, "application/pdf")})
print("Blank PDF rejection:", r_blank.status_code, r_blank.json().get("detail"))
assert r_blank.status_code == 400

# Multiple files batch upload (Success)
with open(sample_dir / "architecture_risks.txt", "rb") as fa, open(sample_dir / "sprint_tasks.csv", "rb") as fb:
    r_multi = client.post(
        "/api/documents/upload",
        files=[
            ("files", ("batch_arch.txt", fa, "text/plain")),
            ("files", ("batch_sprint.csv", fb, "text/csv")),
        ],
    )
print("Multiple files upload success:", r_multi.status_code, f"total={r_multi.json().get('total_files')}, succeeded={r_multi.json().get('successful_count')}")
assert r_multi.status_code == 201
assert r_multi.json()["successful_count"] == 2

# Mixed valid and invalid batch
with open(sample_dir / "architecture_risks.txt", "rb") as fa, open(sample_dir / "unsupported.png", "rb") as fb:
    r_mixed = client.post(
        "/api/documents/upload",
        files=[
            ("files", ("valid_part.txt", fa, "text/plain")),
            ("files", ("invalid_part.png", fb, "image/png")),
        ],
    )
print("Mixed batch upload:", r_mixed.status_code, f"succeeded={r_mixed.json().get('successful_count')}, failed={r_mixed.json().get('failed_count')}")
assert r_mixed.status_code == 201
assert r_mixed.json()["successful_count"] == 1
assert r_mixed.json()["failed_count"] == 1

print("\n=== 3. Testing Agent Analysis ===")
# Scope Agent
r_scope = client.post("/api/agents/scope")
assert r_scope.status_code == 200
s_data = r_scope.json()
print("Scope Agent Results:")
print(f"  Goals ({len(s_data['project_goals'])}):", [g["title"] for g in s_data["project_goals"][:2]])
print(f"  Scope Items ({len(s_data['scope_items'])}):", [s["category"] + ": " + s["description"][:30] for s in s_data["scope_items"][:2]])
print(f"  Deliverables ({len(s_data['deliverables'])}):", [d["name"] for d in s_data["deliverables"][:3]])
print(f"  Milestones ({len(s_data['milestones'])}):", [m["milestone_id"] for m in s_data["milestones"][:3]])
print(f"  Dependencies ({len(s_data['dependencies'])}):", [dep["dependent_item"] + " -> " + dep["depends_on"] for dep in s_data["dependencies"][:2]])
print(f"  Missing Info ({len(s_data['missing_information'])}):", s_data["missing_information"][:2])

# Risk Agent
r_risk = client.post("/api/agents/risks")
assert r_risk.status_code == 200
rk_data = r_risk.json()
print("\nRisk Agent Results:")
print(f"  Overall Delivery Risk: {rk_data['overall_delivery_risk']}")
print(f"  Total Risks: {rk_data['total_risks']} (Crit: {rk_data['critical_count']}, High: {rk_data['high_count']}, Med: {rk_data['medium_count']})")
for rk in rk_data["risks"][:3]:
    print(f"  - [{rk['risk_id']}] ({rk['risk_category']}, {rk['severity']}) {rk['risk_title']}")
    print(f"    Evidence: \"{rk['supporting_evidence'][:60]}...\"")
    print(f"    Mitigation: {rk['recommended_mitigation'][:60]}...")

# Blocker Agent
r_blocker = client.post("/api/agents/blockers")
assert r_blocker.status_code == 200
b_data = r_blocker.json()
print("\nBlocker Agent Results:")
print(f"  Blockers: {b_data['blocker_count']}, Actions: {b_data['action_item_count']}, Decisions: {b_data['pending_decision_count']}, Unassigned: {b_data['unassigned_count']}, Overdue: {b_data['overdue_count']}")
for bi in b_data["items"][:3]:
    print(f"  - [{bi['item_id']}] ({bi['item_type']}) {bi['description'][:50]} (Owner: {bi['assigned_owner']}, Due: {bi['due_date']})")

# Comprehensive Analysis
r_all = client.post("/api/agents/analyze-all")
assert r_all.status_code == 200
print("\nUnified Multi-Agent API Status:", r_all.status_code)
print("Analyzed Documents:", r_all.json()["analyzed_documents"])
print("\n>>> ALL VALIDATION CHECKS PASSED SUCCESSFULLY! <<<")
