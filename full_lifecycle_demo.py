"""
═══════════════════════════════════════════════════════════════════════════════
 SAHAYAK 360 — COMPLETE LIFECYCLE DEMO & VERIFICATION SCRIPT
═══════════════════════════════════════════════════════════════════════════════

This script demonstrates the COMPLETE end-to-end lifecycle:
  Phase 1: User Registration (10 students, 2 teachers, 1 admin)
  Phase 2: Teacher → Freetext Ingestion → AST Parse → Knowledge Graph
  Phase 3: Structured Ingestion → Validation → Mastery Updates → Risk Scoring
  Phase 4: Dashboard Analytics (teacher view, student view)
  Phase 5: AI Natural Language Query → Neo4j Cypher
  Phase 6: Quiz Dispatch → Student Takes Quiz → Mastery Update
  Phase 7: Security Verification

Run: python full_lifecycle_demo.py [--api URL] [--local]
  --api URL : Override API base URL (default: deployed Render)
  --local   : Use http://localhost:8000
"""

import json
import random
import sys
import time
from datetime import datetime

import requests

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

API_BASE = "https://sahayak360-api.onrender.com"

if "--local" in sys.argv:
    API_BASE = "http://localhost:8000"
for arg in sys.argv:
    if arg.startswith("--api="):
        API_BASE = arg.split("=", 1)[1]

VERIFY_SSL = True
if "onrender.com" in API_BASE:
    VERIFY_SSL = False

print(f"\n{'═' * 70}")
print(f" SAHAYAK 360 — FULL LIFECYCLE DEMO")
print(f" API: {API_BASE}")
print(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'═' * 70}\n")

# Suppress SSL warnings for Render
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def api(method, path, token=None, **kwargs):
    """Make API request with error handling."""
    url = f"{API_BASE}{path}"
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers["Content-Type"] = "application/json"
    r = requests.request(method, url, headers=headers, verify=VERIFY_SSL, timeout=30, **kwargs)
    return r


# ═══════════════════════════════════════════════════════════════
# MOCK DATA DEFINITIONS
# ═══════════════════════════════════════════════════════════════

TIMESTAMP = str(int(time.time()))[-5:]

TEACHERS = [
    {"user_id": f"TCH-{TIMESTAMP}1", "email": f"priya.sharma.{TIMESTAMP}@school.edu", "full_name": "Mrs. Priya Sharma", "role": "teacher", "class_section": "9-A", "department_id": "DEPT-MATH"},
    {"user_id": f"TCH-{TIMESTAMP}2", "email": f"rajesh.kumar.{TIMESTAMP}@school.edu", "full_name": "Mr. Rajesh Kumar", "role": "teacher", "class_section": "9-B", "department_id": "DEPT-MATH"},
]

STUDENTS = [
    {"user_id": f"STU-{TIMESTAMP}01", "email": f"aarav.patel.{TIMESTAMP}@student.edu", "full_name": "Aarav Patel", "role": "student", "class_section": "9-A"},
    {"user_id": f"STU-{TIMESTAMP}02", "email": f"diya.gupta.{TIMESTAMP}@student.edu", "full_name": "Diya Gupta", "role": "student", "class_section": "9-A"},
    {"user_id": f"STU-{TIMESTAMP}03", "email": f"vivaan.singh.{TIMESTAMP}@student.edu", "full_name": "Vivaan Singh", "role": "student", "class_section": "9-A"},
    {"user_id": f"STU-{TIMESTAMP}04", "email": f"ananya.reddy.{TIMESTAMP}@student.edu", "full_name": "Ananya Reddy", "role": "student", "class_section": "9-A"},
    {"user_id": f"STU-{TIMESTAMP}05", "email": f"arjun.nair.{TIMESTAMP}@student.edu", "full_name": "Arjun Nair", "role": "student", "class_section": "9-A"},
    {"user_id": f"STU-{TIMESTAMP}06", "email": f"ishaan.joshi.{TIMESTAMP}@student.edu", "full_name": "Ishaan Joshi", "role": "student", "class_section": "9-B"},
    {"user_id": f"STU-{TIMESTAMP}07", "email": f"kavya.mehta.{TIMESTAMP}@student.edu", "full_name": "Kavya Mehta", "role": "student", "class_section": "9-B"},
    {"user_id": f"STU-{TIMESTAMP}08", "email": f"rohan.desai.{TIMESTAMP}@student.edu", "full_name": "Rohan Desai", "role": "student", "class_section": "9-B"},
    {"user_id": f"STU-{TIMESTAMP}09", "email": f"saanvi.iyer.{TIMESTAMP}@student.edu", "full_name": "Saanvi Iyer", "role": "student", "class_section": "9-B"},
    {"user_id": f"STU-{TIMESTAMP}10", "email": f"aditya.mishra.{TIMESTAMP}@student.edu", "full_name": "Aditya Mishra", "role": "student", "class_section": "9-B"},
]

ADMIN = {"user_id": f"ADM-{TIMESTAMP}1", "email": f"admin.{TIMESTAMP}@school.edu", "full_name": "School Admin", "role": "admin", "class_section": "ALL"}

PASSWORD = "Demo@2026Secure"
results = {"passed": 0, "failed": 0, "details": []}


def record(name, status_code, expected, response_text=""):
    passed = status_code in (expected if isinstance(expected, list) else [expected])
    results["passed" if passed else "failed"] += 1
    icon = "✅" if passed else "❌"
    short = response_text[:120] if response_text else ""
    results["details"].append({"name": name, "passed": passed, "status": status_code})
    print(f"  {icon} [{status_code}] {name}")
    if short and not passed:
        print(f"     └─ {short}")
    return passed


# ═══════════════════════════════════════════════════════════════
# PHASE 1: USER REGISTRATION
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 1: REGISTER ALL USERS (2 Teachers + 10 Students + 1 Admin)")
print(f"{'─' * 60}")

tokens = {}  # user_id -> token

# Register teachers
for t in TEACHERS:
    r = api("POST", "/api/auth/register", json={**t, "password": PASSWORD})
    record(f"Register {t['full_name']} ({t['user_id']})", r.status_code, [201])
    if r.status_code == 201:
        tokens[t["user_id"]] = r.json()["access_token"]

# Register students
for s in STUDENTS:
    r = api("POST", "/api/auth/register", json={**s, "password": PASSWORD})
    record(f"Register {s['full_name']} ({s['user_id']})", r.status_code, [201])
    if r.status_code == 201:
        tokens[s["user_id"]] = r.json()["access_token"]

# Register admin
r = api("POST", "/api/auth/register", json={**ADMIN, "password": PASSWORD})
record(f"Register {ADMIN['full_name']} ({ADMIN['user_id']})", r.status_code, [201])
if r.status_code == 201:
    tokens[ADMIN["user_id"]] = r.json()["access_token"]

print(f"\n  Registered: {len(tokens)} users with tokens")

# Login verification for teacher1 and student1
r = api("POST", "/api/auth/login", json={"email": TEACHERS[0]["email"], "password": PASSWORD})
record("Login Teacher 1", r.status_code, [200])
teacher1_token = r.json().get("access_token") if r.status_code == 200 else tokens.get(TEACHERS[0]["user_id"])

r = api("POST", "/api/auth/login", json={"email": STUDENTS[0]["email"], "password": PASSWORD})
record("Login Student 1 (Aarav)", r.status_code, [200])
student1_token = r.json().get("access_token") if r.status_code == 200 else tokens.get(STUDENTS[0]["user_id"])

r = api("POST", "/api/auth/login", json={"email": STUDENTS[1]["email"], "password": PASSWORD})
record("Login Student 2 (Diya)", r.status_code, [200])
student2_token = r.json().get("access_token") if r.status_code == 200 else tokens.get(STUDENTS[1]["user_id"])


# ═══════════════════════════════════════════════════════════════
# PHASE 2: FREETEXT INGESTION → AST → KNOWLEDGE GRAPH
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 2: FREETEXT INGESTION (Teacher → Gemini → AST → KG)")
print(f"{'─' * 60}")

# Teacher 1 enters natural language assessment for Student 1 (Aarav)
freetext_input_1 = f"""
Today I assessed {STUDENTS[0]['user_id']} Aarav Patel on the algebra unit test.
He scored 7 out of 10 on linear equations (Q1), 4 out of 10 on quadratic equations (Q2),
and 8 out of 10 on algebraic expressions (Q3). The test was formative, class 9-A.
Total marks: 25, he got 19. He's good at basics but struggles with quadratics.
"""

print(f"\n  📝 Teacher 1 Input (freetext):")
print(f"  ┌─{'─' * 56}─┐")
for line in freetext_input_1.strip().split("\n"):
    print(f"  │ {line.strip():<56} │")
print(f"  └─{'─' * 56}─┘")

r = api("POST", "/api/ingest/freetext", token=teacher1_token, json={
    "raw_text": freetext_input_1,
    "teacher_id": TEACHERS[0]["user_id"],
    "class_section": "9-A",
    "subject": "mathematics",
})
record("Freetext Ingest (Aarav - algebra)", r.status_code, [200])

if r.status_code == 200:
    resp = r.json()
    print(f"\n  📊 AST Parse Result:")
    print(f"     Event ID:     {resp.get('event_id', 'N/A')}")
    print(f"     Parse Method: {resp.get('parse_method', 'N/A')}")
    print(f"     Status:       {resp.get('status', 'N/A')}")
    if resp.get("validation"):
        v = resp["validation"]
        print(f"     Validation:   sum_check={'PASS' if v.get('sum_check_passed') else 'FAIL'}, discrepancy={v.get('discrepancy', 0)}")
    if resp.get("cognitive_analysis"):
        ca = resp["cognitive_analysis"]
        print(f"     Gaps Found:   {ca.get('gaps_detected', 0)}")
        print(f"     Risk Tier:    {ca.get('risk_tier', 'unknown')}")
        print(f"     Intervention: {'YES' if ca.get('needs_intervention') else 'no'}")
    if resp.get("graph_mutations"):
        print(f"     Graph Updates: {resp['graph_mutations']}")

# Teacher 1 enters freetext for Student 2 (Diya - struggling)
freetext_input_2 = f"""
Assessment for {STUDENTS[1]['user_id']} Diya Gupta, class 9-A mathematics.
Diya attempted the geometry quiz: scored 3/10 on triangle properties,
2/10 on circle theorems, and 5/10 on basic geometry. Formative test.
Total max 30, obtained 10. She needs significant help with geometry concepts.
"""

print(f"\n  📝 Teacher 1 Input (Student 2 - Diya, struggling):")
r = api("POST", "/api/ingest/freetext", token=teacher1_token, json={
    "raw_text": freetext_input_2,
    "teacher_id": TEACHERS[0]["user_id"],
    "class_section": "9-A",
    "subject": "mathematics",
})
record("Freetext Ingest (Diya - geometry, struggling)", r.status_code, [200])

if r.status_code == 200:
    resp = r.json()
    print(f"     Event ID: {resp.get('event_id')} | Method: {resp.get('parse_method')}")
    if resp.get("cognitive_analysis"):
        ca = resp["cognitive_analysis"]
        print(f"     Gaps: {ca.get('gaps_detected')} | Risk: {ca.get('risk_tier')} | Intervention: {ca.get('needs_intervention')}")


# ═══════════════════════════════════════════════════════════════
# PHASE 3: STRUCTURED INGESTION → FULL PIPELINE
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 3: STRUCTURED INGESTION (JSON → Validate → Mastery → KG)")
print(f"{'─' * 60}")

# Structured assessment for Student 1 (Aarav) - another assessment
structured_payload_1 = {
    "teacher_id": TEACHERS[0]["user_id"],
    "student_id": STUDENTS[0]["user_id"],
    "class_section": "9-A",
    "subject": "mathematics",
    "department_id": "DEPT-MATH",
    "assessment_type": "formative",
    "max_score": 40,
    "total_obtained": 32,
    "items": [
        {"question_id": "Q-01", "knowledge_component_id": "KC-MATH-ALG-LINEAR", "knowledge_component_name": "Linear Equations", "max_marks": 10, "obtained_marks": 9, "is_correct": True},
        {"question_id": "Q-02", "knowledge_component_id": "KC-MATH-ALG-POLY", "knowledge_component_name": "Polynomials", "max_marks": 10, "obtained_marks": 8, "is_correct": True},
        {"question_id": "Q-03", "knowledge_component_id": "KC-MATH-ALG-FACTOR", "knowledge_component_name": "Factorization", "max_marks": 10, "obtained_marks": 7, "is_correct": True},
        {"question_id": "Q-04", "knowledge_component_id": "KC-MATH-ALG-QUAD", "knowledge_component_name": "Quadratic Equations", "max_marks": 10, "obtained_marks": 8, "is_correct": True},
    ],
}

print(f"\n  📋 Structured Input (Aarav - Algebra, 32/40):")
print(f"     Items: {len(structured_payload_1['items'])} questions across 4 KCs")

r = api("POST", "/api/ingest/structured", token=teacher1_token, json=structured_payload_1)
record("Structured Ingest (Aarav - 32/40 algebra)", r.status_code, [200])

if r.status_code == 200:
    resp = r.json()
    print(f"\n  📊 Pipeline Result:")
    print(f"     Event ID:     {resp.get('event_id')}")
    print(f"     Lane:         {resp.get('parse_method')}")
    print(f"     Validation:   sum_check={'PASS' if resp.get('validation', {}).get('sum_check_passed') else 'FAIL'}")
    if resp.get("cognitive_analysis"):
        ca = resp["cognitive_analysis"]
        print(f"     Gaps:         {ca.get('gaps_detected', 0)}")
        print(f"     Risk Tier:    {ca.get('risk_tier', 'unknown')}")
        print(f"     Mastery Updates: {ca.get('mastery_updates', 0)}")
        print(f"     Tickets:      {ca.get('tickets_created', [])}")
    if resp.get("graph_mutations"):
        print(f"     KG Mutations: {resp['graph_mutations'][:5]}")

# Structured for Student 2 (Diya - very low scores)
structured_payload_2 = {
    "teacher_id": TEACHERS[0]["user_id"],
    "student_id": STUDENTS[1]["user_id"],
    "class_section": "9-A",
    "subject": "mathematics",
    "department_id": "DEPT-MATH",
    "assessment_type": "formative",
    "max_score": 40,
    "total_obtained": 12,
    "items": [
        {"question_id": "Q-01", "knowledge_component_id": "KC-MATH-ALG-LINEAR", "knowledge_component_name": "Linear Equations", "max_marks": 10, "obtained_marks": 4, "is_correct": False},
        {"question_id": "Q-02", "knowledge_component_id": "KC-MATH-ALG-QUAD", "knowledge_component_name": "Quadratic Equations", "max_marks": 10, "obtained_marks": 2, "is_correct": False},
        {"question_id": "Q-03", "knowledge_component_id": "KC-MATH-GEO-TRIANGLE", "knowledge_component_name": "Triangle Properties", "max_marks": 10, "obtained_marks": 3, "is_correct": False},
        {"question_id": "Q-04", "knowledge_component_id": "KC-MATH-GEO-CIRCLE", "knowledge_component_name": "Circle Theorems", "max_marks": 10, "obtained_marks": 3, "is_correct": False},
    ],
}

r = api("POST", "/api/ingest/structured", token=teacher1_token, json=structured_payload_2)
record("Structured Ingest (Diya - 12/40, at-risk)", r.status_code, [200])

if r.status_code == 200:
    resp = r.json()
    print(f"\n  ⚠️  Diya's Result (struggling student):")
    print(f"     Event ID: {resp.get('event_id')} | Risk: {resp.get('cognitive_analysis', {}).get('risk_tier')}")
    print(f"     Intervention needed: {resp.get('cognitive_analysis', {}).get('needs_intervention')}")
    print(f"     Tickets created: {resp.get('cognitive_analysis', {}).get('tickets_created', [])}")


# ═══════════════════════════════════════════════════════════════
# PHASE 4: DASHBOARD ANALYTICS
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 4: DASHBOARD ANALYTICS (Teacher + Student views)")
print(f"{'─' * 60}")

# Teacher overview
r = api("GET", "/api/dashboard/teacher/overview?class_section=9-A&subject=mathematics", token=teacher1_token)
record("Teacher Dashboard Overview (9-A)", r.status_code, [200])
if r.status_code == 200:
    d = r.json()
    print(f"     Total Students: {d.get('total_students')}")
    print(f"     Avg Mastery:    {d.get('avg_mastery')}")
    print(f"     At-Risk Count:  {d.get('at_risk_count')}")
    print(f"     Open Tickets:   {d.get('pending_tickets')}")

# Teacher student list
r = api("GET", "/api/dashboard/teacher/students?class_section=9-A", token=teacher1_token)
record("Teacher Student List (9-A)", r.status_code, [200])
if r.status_code == 200:
    students_list = r.json()
    print(f"     Students in 9-A: {len(students_list)}")
    for s in students_list[:3]:
        print(f"       • {s.get('student_id')} {s.get('full_name')}: mastery={s.get('overall_mastery'):.3f}, risk={s.get('risk_tier')}")

# Student mastery view (Aarav)
r = api("GET", "/api/dashboard/student/mastery?subject=mathematics", token=student1_token)
record("Student Mastery (Aarav)", r.status_code, [200])
if r.status_code == 200:
    masteries = r.json()
    print(f"     Aarav's KC Masteries ({len(masteries)} items):")
    for m in masteries[:5]:
        bar = "█" * int(m["mastery"] * 10) + "░" * (10 - int(m["mastery"] * 10))
        print(f"       [{bar}] {m['mastery']:.2f} {m['kc_name']} ({m['mastery_level']})")

# Student mastery view (Diya)
r = api("GET", "/api/dashboard/student/mastery?subject=mathematics", token=student2_token)
record("Student Mastery (Diya - struggling)", r.status_code, [200])
if r.status_code == 200:
    masteries = r.json()
    print(f"     Diya's KC Masteries ({len(masteries)} items):")
    for m in masteries[:5]:
        bar = "█" * int(m["mastery"] * 10) + "░" * (10 - int(m["mastery"] * 10))
        print(f"       [{bar}] {m['mastery']:.2f} {m['kc_name']} ({m['mastery_level']})")


# ═══════════════════════════════════════════════════════════════
# PHASE 5: AI NATURAL LANGUAGE QUERY
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 5: AI NATURAL LANGUAGE QUERY (NL → Cypher → Neo4j)")
print(f"{'─' * 60}")

queries = [
    "Which students are struggling the most in my class?",
    "What are the common knowledge gaps in class 9-A?",
    "Show me students who need help with quadratic equations",
]

for q in queries:
    r = api("POST", "/api/query/ask", token=teacher1_token, json={"question": q, "context": "teacher_dashboard"})
    record(f"NL Query: '{q[:40]}...'", r.status_code, [200])
    if r.status_code == 200:
        resp = r.json()
        answer = resp.get("answer", "")[:120]
        print(f"     Q: {q}")
        print(f"     A: {answer}")
        if resp.get("cypher_used"):
            print(f"     Cypher: {resp['cypher_used'][:80]}...")
        if resp.get("data"):
            print(f"     Data: {len(resp['data'])} records returned")
        print()


# ═══════════════════════════════════════════════════════════════
# PHASE 6: QUIZ DISPATCH → STUDENT TAKES → MASTERY UPDATE
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 6: QUIZ LIFECYCLE (Dispatch → Take → Score → Update)")
print(f"{'─' * 60}")

# Teacher dispatches quiz to Diya (struggling student) for her weak KCs
print(f"\n  🎯 Teacher dispatches micro-test to Diya (weak: geometry)")
r = api("POST", "/api/quiz/dispatch", token=teacher1_token, json={
    "student_id": STUDENTS[1]["user_id"],
    "target_kc_ids": ["KC-MATH-GEO-TRIANGLE", "KC-MATH-GEO-CIRCLE", "KC-MATH-GEO-BASIC"],
    "num_questions": 3,
})
record("Quiz Dispatch (Diya - geometry)", r.status_code, [200])

session_id = None
questions = []
if r.status_code == 200:
    quiz = r.json()
    session_id = quiz["session_id"]
    questions = quiz["questions"]
    print(f"     Session: {session_id}")
    print(f"     Questions: {len(questions)}")
    for i, q in enumerate(questions, 1):
        print(f"       Q{i}: {q.get('question_text', 'N/A')[:60]}... (KC: {q.get('kc_id')})")

# Student answers quiz (simulate - Diya picks options, server scores)
if session_id and questions:
    print(f"\n  📝 Diya answers the quiz (picks first option for each)")
    responses = []
    for i, q in enumerate(questions):
        options = q.get("options", ["A", "B", "C", "D"])
        # Pick first option for each (correct_answer is hidden from student)
        responses.append({"question_id": q["question_id"], "answer": options[0] if options else "A"})

    r = api("POST", "/api/quiz/submit", token=student2_token, json={
        "session_id": session_id,
        "responses": responses,
    })
    record("Quiz Submit (Diya - answers submitted)", r.status_code, [200])

    if r.status_code == 200:
        result = r.json()
        print(f"     Score: {result.get('score', 0):.0%} ({result.get('correct_count')}/{result.get('total_questions')})")
        print(f"     Note: correct_answer hidden from client (secure design)")
        if result.get("mastery_deltas"):
            print(f"     Mastery Changes:")
            for kc, delta in result["mastery_deltas"].items():
                direction = "↑" if delta > 0 else "─"
                print(f"       {direction} {kc}: {delta:.3f}")

# Quiz for Aarav (strong student - higher difficulty)
print(f"\n  🎯 Teacher dispatches quiz to Aarav (challenge: quadratics)")
r = api("POST", "/api/quiz/dispatch", token=teacher1_token, json={
    "student_id": STUDENTS[0]["user_id"],
    "target_kc_ids": ["KC-MATH-ALG-QUAD", "KC-MATH-ALG-SIMUL", "KC-MATH-ALG-FACTOR"],
    "num_questions": 3,
})
record("Quiz Dispatch (Aarav - advanced algebra)", r.status_code, [200])

if r.status_code == 200:
    quiz = r.json()
    session_id2 = quiz["session_id"]
    questions2 = quiz["questions"]
    print(f"     Session: {session_id2} | Questions: {len(questions2)}")

    # NOTE: correct_answer is intentionally NOT sent to students (security).
    # Student picks first option as best guess. Scoring happens server-side.
    print(f"  📝 Aarav answers (picks option A for all - simulated)")
    responses2 = []
    for q in questions2:
        options = q.get("options", ["A", "B", "C", "D"])
        responses2.append({"question_id": q["question_id"], "answer": options[0] if options else "A"})

    r = api("POST", "/api/quiz/submit", token=student1_token, json={
        "session_id": session_id2,
        "responses": responses2,
    })
    record("Quiz Submit (Aarav - submitted)", r.status_code, [200])
    if r.status_code == 200:
        result = r.json()
        print(f"     Score: {result.get('score', 0):.0%} ({result.get('correct_count')}/{result.get('total_questions')})")
        print(f"     Note: correct_answer hidden from client (secure design)")
        print(f"     Mastery Deltas: {result.get('mastery_deltas', {})}")


# ═══════════════════════════════════════════════════════════════
# PHASE 7: SECURITY VERIFICATION
# ═══════════════════════════════════════════════════════════════
print(f"\n{'─' * 60}")
print(" PHASE 7: SECURITY CHECKS")
print(f"{'─' * 60}")

# Unauthenticated access blocked
r = api("GET", "/api/dashboard/teacher/overview?class_section=9-A")
record("No token → 401", r.status_code, [401])

# Student can't access teacher routes
r = api("GET", "/api/dashboard/teacher/overview?class_section=9-A", token=student1_token)
record("Student → teacher route → 403", r.status_code, [403])

# Duplicate registration blocked
r = api("POST", "/api/auth/register", json={**TEACHERS[0], "password": PASSWORD})
record("Duplicate registration → 409", r.status_code, [409])


# ═══════════════════════════════════════════════════════════════
# RESULTS SUMMARY
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═' * 70}")
print(f" LIFECYCLE DEMO RESULTS")
print(f"{'═' * 70}")
print(f"\n  Total Tests: {results['passed'] + results['failed']}")
print(f"  Passed:      {results['passed']} ✅")
print(f"  Failed:      {results['failed']} ❌")

if results["failed"] > 0:
    print(f"\n  Failed Tests:")
    for d in results["details"]:
        if not d["passed"]:
            print(f"    ❌ {d['name']} [{d['status']}]")

print(f"\n{'═' * 70}")
print(f" DEMO USERS FOR MANUAL TESTING")
print(f"{'═' * 70}")
print(f"\n  🔐 Login Credentials (all use password: {PASSWORD})")
print(f"\n  TEACHERS:")
for t in TEACHERS:
    print(f"    • {t['email']} ({t['full_name']}, {t['class_section']})")
print(f"\n  STUDENTS (first 5 of 10):")
for s in STUDENTS[:5]:
    print(f"    • {s['email']} ({s['full_name']}, {s['class_section']})")
print(f"\n  ADMIN:")
print(f"    • {ADMIN['email']} ({ADMIN['full_name']})")
print(f"\n  Frontend: https://sahayak360-mvp.vercel.app")
print(f"  API Docs: {API_BASE}/docs")
print(f"\n{'═' * 70}\n")
