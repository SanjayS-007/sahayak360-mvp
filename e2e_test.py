"""
Sahayak 360 — Complete End-to-End Use Case Test
Tests the full flow: register → login → ingest data → dashboard → AI query → quiz
"""

import requests
import json
import time
from datetime import datetime

BASE = "https://sahayak360-api.onrender.com"
S = requests.Session()
S.verify = False
import urllib3; urllib3.disable_warnings()

PASS = "✅"
FAIL = "❌"
SKIP = "⚠️ "

results = []

def test(name, fn, expect_fail=False):
    try:
        r = fn()
        ok = r if isinstance(r, bool) else r.status_code < 400
        if expect_fail:
            ok = not ok  # For security tests expecting 4xx
        status = PASS if ok else FAIL
        code = getattr(r, 'status_code', '—')
        body = getattr(r, 'text', str(r))[:120]
        results.append((status, name, code, body))
        print(f"{status} {name} [{code}] {body[:80]}")
        return r
    except Exception as e:
        results.append((FAIL, name, 'ERR', str(e)[:120]))
        print(f"{FAIL} {name} [ERR] {e}")
        return None

# ─── 0. HEALTH ────────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 0: HEALTH CHECKS")
print("══════════════════════════════════════════")

test("GET /health", lambda: S.get(f"{BASE}/health", timeout=30))
test("GET /       (root)", lambda: S.get(f"{BASE}/", timeout=30))
test("GET /docs   (OpenAPI)", lambda: S.get(f"{BASE}/docs", timeout=30))
test("GET /openapi.json", lambda: S.get(f"{BASE}/openapi.json", timeout=30))

# ─── 1. AUTH — REGISTER ───────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 1: AUTH — REGISTER + LOGIN")
print("══════════════════════════════════════════")

ts = int(time.time()) % 100000
TEACHER_EMAIL = f"teacher.demo{ts}@school.edu"
STUDENT_EMAIL = f"student.demo{ts}@school.edu"
TEACHER_ID = f"TCH-{ts:05d}"
STUDENT_ID = f"STU-{ts:05d}"
CLASS = f"10-A-{ts}"

reg_teacher = test("POST /api/auth/register (teacher)", lambda: S.post(
    f"{BASE}/api/auth/register",
    json={"email": TEACHER_EMAIL, "password": "SecurePass123", "full_name": "Demo Teacher",
          "role": "teacher", "user_id": TEACHER_ID, "department_id": "MATHS"},
    timeout=30
))

reg_student = test("POST /api/auth/register (student)", lambda: S.post(
    f"{BASE}/api/auth/register",
    json={"email": STUDENT_EMAIL, "password": "SecurePass123", "full_name": "Demo Student",
          "role": "student", "user_id": STUDENT_ID, "class_section": CLASS},
    timeout=30
))

# ─── 2. AUTH — LOGIN ──────────────────────────────────────────────────────────
TEACHER_TOKEN = None
STUDENT_TOKEN = None

login_r = test("POST /api/auth/login (teacher)", lambda: S.post(
    f"{BASE}/api/auth/login",
    json={"email": TEACHER_EMAIL, "password": "SecurePass123"},
    timeout=30
))
if login_r and login_r.status_code == 200:
    TEACHER_TOKEN = login_r.json().get("access_token")
    print(f"   → Token: {TEACHER_TOKEN[:40]}...")

login_s = test("POST /api/auth/login (student)", lambda: S.post(
    f"{BASE}/api/auth/login",
    json={"email": STUDENT_EMAIL, "password": "SecurePass123"},
    timeout=30
))
if login_s and login_s.status_code == 200:
    STUDENT_TOKEN = login_s.json().get("access_token")
    print(f"   → Token: {STUDENT_TOKEN[:40]}...")

# ─── Profile ──────────────────────────────────────────────────────────────────
if TEACHER_TOKEN:
    test("GET /api/auth/me (teacher)", lambda: S.get(
        f"{BASE}/api/auth/me",
        headers={"Authorization": f"Bearer {TEACHER_TOKEN}"},
        timeout=30
    ))

# ─── 3. DATA INGESTION ────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 2: DATA INGESTION")
print("══════════════════════════════════════════")

auth_teacher = {"Authorization": f"Bearer {TEACHER_TOKEN}"} if TEACHER_TOKEN else {}

ingest_payload = {
    "teacher_id": TEACHER_ID,
    "student_id": STUDENT_ID,
    "class_section": CLASS,
    "subject": "mathematics",
    "max_score": 100,
    "total_obtained": 72,
    "items": [
        {"question_id": "Q1", "knowledge_component_id": "ALG-001", "knowledge_component_name": "Linear Equations", "max_marks": 20, "obtained_marks": 18, "is_correct": True},
        {"question_id": "Q2", "knowledge_component_id": "ALG-002", "knowledge_component_name": "Quadratic Equations", "max_marks": 20, "obtained_marks": 12, "is_correct": False},
        {"question_id": "Q3", "knowledge_component_id": "GEO-001", "knowledge_component_name": "Triangles", "max_marks": 20, "obtained_marks": 16, "is_correct": True},
        {"question_id": "Q4", "knowledge_component_id": "STA-001", "knowledge_component_name": "Statistics", "max_marks": 20, "obtained_marks": 14, "is_correct": True},
        {"question_id": "Q5", "knowledge_component_id": "TRI-001", "knowledge_component_name": "Trigonometry", "max_marks": 20, "obtained_marks": 12, "is_correct": False}
    ]
}

ingest_r = test("POST /api/ingest/structured", lambda: S.post(
    f"{BASE}/api/ingest/structured",
    json=ingest_payload,
    headers=auth_teacher,
    timeout=30
))
if ingest_r and ingest_r.status_code == 200:
    print(f"   → event_id: {ingest_r.json().get('event_id')}, method: {ingest_r.json().get('parse_method')}")

# Freetext ingestion
freetext_payload = {
    "teacher_id": TEACHER_ID,
    "student_id": STUDENT_ID,
    "class_section": CLASS,
    "raw_text": f"Student {STUDENT_ID} scored 72/100 in unit test. Struggles with quadratic equations and trigonometry. Good in geometry and statistics.",
    "subject": "mathematics"
}

test("POST /api/ingest/freetext", lambda: S.post(
    f"{BASE}/api/ingest/freetext",
    json=freetext_payload,
    headers=auth_teacher,
    timeout=30
))

# ─── 4. DASHBOARD ─────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 3: DASHBOARD ANALYTICS")
print("══════════════════════════════════════════")

test("GET /api/dashboard/teacher/overview", lambda: S.get(
    f"{BASE}/api/dashboard/teacher/overview?class_section={CLASS}&subject=mathematics",
    headers=auth_teacher,
    timeout=30
))

test("GET /api/dashboard/teacher/students", lambda: S.get(
    f"{BASE}/api/dashboard/teacher/students?class_section={CLASS}",
    headers=auth_teacher,
    timeout=30
))

auth_student = {"Authorization": f"Bearer {STUDENT_TOKEN}"} if STUDENT_TOKEN else {}

test("GET /api/dashboard/student/mastery", lambda: S.get(
    f"{BASE}/api/dashboard/student/mastery",
    headers=auth_student,
    timeout=30
))

# ─── 5. AI QUERY ──────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 4: AI NATURAL LANGUAGE QUERY")
print("══════════════════════════════════════════")

nl_r = test("POST /api/query/ask (NL query)", lambda: S.post(
    f"{BASE}/api/query/ask",
    json={"question": f"Which students in class {CLASS} need help with mathematics?", "context": "teacher"},
    headers=auth_teacher,
    timeout=30
))
if nl_r and nl_r.status_code == 200:
    ans = nl_r.json().get('answer', '')[:200]
    print(f"   → Answer: {ans}")

# ─── 6. QUIZ ──────────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 5: QUIZ DISPATCH & SUBMIT")
print("══════════════════════════════════════════")

quiz_r = test("POST /api/quiz/dispatch", lambda: S.post(
    f"{BASE}/api/quiz/dispatch",
    json={"student_id": STUDENT_ID, "target_kc_ids": ["ALG-002", "TRI-001"], "num_questions": 3},
    headers=auth_teacher,
    timeout=30
))

session_id = None
if quiz_r and quiz_r.status_code == 200:
    quiz_data = quiz_r.json()
    session_id = quiz_data.get("session_id")
    questions = quiz_data.get("questions", [])
    print(f"   → session_id: {session_id}, questions: {len(questions)}")
    if questions:
        print(f"   → Q1: {str(questions[0])[:100]}")

if session_id:
    # Build submit payload — pick first option for each question
    responses = []
    for q in quiz_data.get("questions", []):
        opts = q.get("options", [])
        responses.append({"question_id": q.get("id", q.get("question_id", "q1")), "answer": opts[0] if opts else "A"})

    test("POST /api/quiz/submit", lambda: S.post(
        f"{BASE}/api/quiz/submit",
        json={"session_id": session_id, "responses": responses},
        headers=auth_student,
        timeout=30
    ))

# ─── 7. SECURITY TESTS ────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" PHASE 6: SECURITY CHECKS")
print("══════════════════════════════════════════")

test("Unauth → /api/dashboard/teacher/overview (expect 401/403)", lambda: S.get(
    f"{BASE}/api/dashboard/teacher/overview?class_section=X&subject=math",
    timeout=15
), expect_fail=True)

test("Invalid token → expect 401", lambda: S.get(
    f"{BASE}/api/auth/profile",
    headers={"Authorization": "Bearer invalid.token.here"},
    timeout=15
), expect_fail=True)

test("Duplicate register → expect 409", lambda: S.post(
    f"{BASE}/api/auth/register",
    json={"email": TEACHER_EMAIL, "password": "SecurePass123", "full_name": "Dup",
          "role": "teacher", "user_id": f"TCH-99999", "department_id": "X"},
    timeout=15
), expect_fail=True)

test("Student can't access teacher route (expect 403)", lambda: S.get(
    f"{BASE}/api/dashboard/teacher/overview?class_section={CLASS}&subject=math",
    headers=auth_student,
    timeout=15
), expect_fail=True)

# ─── SUMMARY ──────────────────────────────────────────────────────────────────
print("\n══════════════════════════════════════════")
print(" RESULTS SUMMARY")
print("══════════════════════════════════════════")

passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
skipped = sum(1 for r in results if r[0] == SKIP)
total = len(results)

print(f"\n  Total:  {total}")
print(f"  Passed: {passed} ✅")
print(f"  Failed: {failed} ❌")
print(f"\nDetailed Results:")
for status, name, code, body in results:
    print(f"  {status} [{code:>3}] {name}")
    if status == FAIL:
        print(f"         └─ {body[:100]}")
