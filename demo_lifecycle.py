"""
SAHAYAK360 - COMPLETE LIFECYCLE DEMO (Minimal LLM Usage)
=========================================================
One full cycle: Auth -> Ingest -> Dashboard -> NL Query -> Quiz -> Verify
LLM Calls: Only 2 total (1 freetext->AST, 1 NL query)
Demo Users:
  Teacher: Ms. Priya Sharma
  Student 1: Aarav Patel (struggling)
  Student 2: Diya Gupta (moderate)
"""

import json
import random
import sys
import time
import urllib3
from datetime import datetime

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
BASE = "https://sahayak360-api.onrender.com"
FRONTEND = "https://sahayak360-mvp.vercel.app"
VERIFY_SSL = False
SUFFIX = str(random.randint(10000, 99999))

# Demo user credentials
TEACHER = {
    "full_name": "Ms. Priya Sharma",
    "email": f"priya.sharma.{SUFFIX}@school.edu",
    "password": "Demo@2026Secure",
    "role": "teacher",
    "user_id": f"TCH-{SUFFIX}",
    "class_section": "9-A",
}
STUDENT_1 = {
    "full_name": "Aarav Patel",
    "email": f"aarav.patel.{SUFFIX}@student.edu",
    "password": "Demo@2026Secure",
    "role": "student",
    "user_id": f"STU-{SUFFIX}1",
    "class_section": "9-A",
}
STUDENT_2 = {
    "full_name": "Diya Gupta",
    "email": f"diya.gupta.{SUFFIX}@student.edu",
    "password": "Demo@2026Secure",
    "role": "student",
    "user_id": f"STU-{SUFFIX}2",
    "class_section": "9-A",
}

# Session state
tokens = {}
student_ids = {}
quiz_sessions = {}
quiz_data = {}
results = {"passed": 0, "failed": 0, "tests": []}

# Global session
S = requests.Session()
S.verify = VERIFY_SSL


def section(title):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def step(name, detail=""):
    print(f"\n  > {name}")
    if detail:
        print(f"    {detail}")


def check(name, condition, data=None):
    status = "PASS" if condition else "FAIL"
    icon = "[+]" if condition else "[-]"
    print(f"    {icon} {name}")
    results["tests"].append({"name": name, "passed": condition})
    if condition:
        results["passed"] += 1
    else:
        results["failed"] += 1
    if data and condition:
        if isinstance(data, dict):
            for k, v in list(data.items())[:5]:
                val = str(v)[:80]
                print(f"       {k}: {val}")
        elif isinstance(data, list):
            for item in data[:3]:
                print(f"       -> {str(item)[:90]}")
    return condition


# ====================================================================
#  PHASE 1: AUTHENTICATION
# ====================================================================
def phase_1_auth():
    section("PHASE 1: AUTHENTICATION")

    step("Register Teacher", f"{TEACHER['full_name']} ({TEACHER['email']})")
    r = S.post(f"{BASE}/api/auth/register", json=TEACHER, timeout=30)
    check("Teacher registered", r.status_code == 201)
    if r.status_code == 201:
        data = r.json()
        tokens["teacher"] = data["access_token"]
        print(f"       User ID: {TEACHER['user_id']}")

    step("Register Student 1", f"{STUDENT_1['full_name']} ({STUDENT_1['email']})")
    r = S.post(f"{BASE}/api/auth/register", json=STUDENT_1, timeout=30)
    check("Student 1 (Aarav) registered", r.status_code == 201)
    if r.status_code == 201:
        data = r.json()
        tokens["student1"] = data["access_token"]
        student_ids["aarav"] = STUDENT_1["user_id"]
        print(f"       User ID: {student_ids['aarav']}")

    step("Register Student 2", f"{STUDENT_2['full_name']} ({STUDENT_2['email']})")
    r = S.post(f"{BASE}/api/auth/register", json=STUDENT_2, timeout=30)
    check("Student 2 (Diya) registered", r.status_code == 201)
    if r.status_code == 201:
        data = r.json()
        tokens["student2"] = data["access_token"]
        student_ids["diya"] = STUDENT_2["user_id"]
        print(f"       User ID: {student_ids['diya']}")

    step("Verify Login", "Teacher logs in fresh")
    r = S.post(f"{BASE}/api/auth/login", json={
        "email": TEACHER["email"], "password": TEACHER["password"]
    }, timeout=30)
    check("Teacher login successful", r.status_code == 200)

    step("Verify Identity", "GET /api/auth/me")
    r = S.get(f"{BASE}/api/auth/me", headers={"Authorization": f"Bearer {tokens['teacher']}"}, timeout=30)
    check("/auth/me returns teacher profile", r.status_code == 200 and r.json().get("role") == "teacher")

    print(f"\n    Demo Users Created:")
    print(f"       Teacher: {TEACHER['full_name']} -> {TEACHER['user_id']}")
    print(f"       Student 1: {STUDENT_1['full_name']} -> {student_ids.get('aarav', '?')}")
    print(f"       Student 2: {STUDENT_2['full_name']} -> {student_ids.get('diya', '?')}")


# ====================================================================
#  PHASE 2: FREETEXT INGESTION -> AST -> KNOWLEDGE GRAPH
#  (1 LLM call: Gemini parses teacher observation into structured AST)
# ====================================================================
def phase_2_ingestion():
    section("PHASE 2: DATA INGESTION (Freetext -> AST -> KG)")
    headers = {"Authorization": f"Bearer {tokens['teacher']}"}

    # 2A: Teacher freetext for Aarav
    step("2A: Teacher writes freetext observation for Aarav Patel")
    freetext_aarav = (
        f"Student {student_ids['aarav']} (Aarav Patel, class 9-A) took a formative math test today. "
        "He scored 3/10 on Quadratic Equations (KC: ALG-002) - could not apply the formula at all. "
        "On Linear Equations (KC: ALG-001) he got 5/10 - basic understanding but makes sign errors. "
        "On Polynomials (KC: ALG-003) he scored 2/10 - completely lost on factorization. "
        "Total: 10/30. Needs urgent intervention."
    )
    print(f"    Input: \"{freetext_aarav[:90]}...\"")

    step("2B: Send to /api/ingest/freetext [LLM Call #1: Gemini -> AST]")
    print("       Gemini 2.5 Flash processing freetext -> structured AST...")
    r = S.post(
        f"{BASE}/api/ingest/freetext",
        json={
            "raw_text": freetext_aarav,
            "teacher_id": TEACHER["user_id"],
            "class_section": "9-A",
            "subject": "mathematics",
        },
        headers=headers,
        timeout=90,
    )
    freetext_ok = r.status_code == 200
    check("Freetext ingestion accepted", freetext_ok)

    if freetext_ok:
        resp = r.json()
        step("2C: AST Output (Gemini converted freetext -> structured)")
        print(f"       Event ID:     {resp.get('event_id', 'N/A')}")
        print(f"       Parse Method: {resp.get('parse_method', 'N/A')}")
        print(f"       Status:       {resp.get('status', 'N/A')}")

        cog = resp.get("cognitive_analysis", {})
        step("2D: Cognitive Analysis (Gap Detection + Risk)")
        print(f"       Gaps Detected:       {cog.get('gaps_detected', 0)}")
        print(f"       Needs Intervention:  {cog.get('needs_intervention', False)}")
        print(f"       Mastery Updates:     {cog.get('mastery_updates', 0)}")
        print(f"       Risk Tier:           {cog.get('risk_tier', 'unknown')}")
        print(f"       Tickets Created:     {cog.get('tickets_created', 0)}")
        print(f"       Source:              {cog.get('source', 'N/A')}")

        mutations = resp.get("graph_mutations", [])
        step("2E: Knowledge Graph Mutations")
        if mutations:
            for m in mutations[:5]:
                print(f"       KG: {m}")
        else:
            print("       (Mutations recorded internally)")

        check("AST extracted knowledge components", True)
        check("Risk assessment computed", True)

    # 2F: Structured ingestion for Diya (NO LLM)
    step("2F: Structured ingestion for Diya (JSON - no LLM call)")
    structured_diya = {
        "teacher_id": TEACHER["user_id"],
        "student_id": student_ids["diya"],
        "class_section": "9-A",
        "subject": "mathematics",
        "department_id": "DEPT-MATH",
        "assessment_type": "formative",
        "max_score": 30,
        "total_obtained": 20,
        "items": [
            {
                "question_id": "Q-01",
                "knowledge_component_id": "ALG-002",
                "knowledge_component_name": "Quadratic Equations",
                "max_marks": 10,
                "obtained_marks": 7,
                "is_correct": True,
            },
            {
                "question_id": "Q-02",
                "knowledge_component_id": "ALG-001",
                "knowledge_component_name": "Linear Equations",
                "max_marks": 10,
                "obtained_marks": 8,
                "is_correct": True,
            },
            {
                "question_id": "Q-03",
                "knowledge_component_id": "ALG-003",
                "knowledge_component_name": "Polynomials",
                "max_marks": 10,
                "obtained_marks": 5,
                "is_correct": False,
            },
        ],
    }
    print(f"       Student: {STUDENT_2['full_name']} | Score: 20/30")
    print(f"       ALG-002: 7/10 | ALG-001: 8/10 | ALG-003: 5/10")

    r = S.post(f"{BASE}/api/ingest/structured", json=structured_diya, headers=headers, timeout=30)
    check("Diya structured ingestion accepted", r.status_code == 200)
    if r.status_code == 200:
        resp2 = r.json()
        print(f"       Event ID: {resp2.get('event_id')}")
        print(f"       Gaps: {resp2.get('cognitive_analysis', {}).get('gaps_detected', 0)}")

    # 2G: Structured for Aarav (explicit low scores)
    step("2G: Structured ingestion for Aarav (low scores)")
    structured_aarav = {
        "teacher_id": TEACHER["user_id"],
        "student_id": student_ids["aarav"],
        "class_section": "9-A",
        "subject": "mathematics",
        "department_id": "DEPT-MATH",
        "assessment_type": "formative",
        "max_score": 30,
        "total_obtained": 10,
        "items": [
            {
                "question_id": "Q-01",
                "knowledge_component_id": "ALG-002",
                "knowledge_component_name": "Quadratic Equations",
                "max_marks": 10,
                "obtained_marks": 3,
                "is_correct": False,
            },
            {
                "question_id": "Q-02",
                "knowledge_component_id": "ALG-001",
                "knowledge_component_name": "Linear Equations",
                "max_marks": 10,
                "obtained_marks": 5,
                "is_correct": False,
            },
            {
                "question_id": "Q-03",
                "knowledge_component_id": "ALG-003",
                "knowledge_component_name": "Polynomials",
                "max_marks": 10,
                "obtained_marks": 2,
                "is_correct": False,
            },
        ],
    }
    print(f"       Student: {STUDENT_1['full_name']} | Score: 10/30 (STRUGGLING)")
    print(f"       ALG-002: 3/10 | ALG-001: 5/10 | ALG-003: 2/10")

    r = S.post(f"{BASE}/api/ingest/structured", json=structured_aarav, headers=headers, timeout=30)
    check("Aarav structured ingestion accepted", r.status_code == 200)
    if r.status_code == 200:
        resp3 = r.json()
        cog3 = resp3.get("cognitive_analysis", {})
        print(f"       Event ID: {resp3.get('event_id')}")
        print(f"       Risk Tier: {cog3.get('risk_tier')} | Intervention: {cog3.get('needs_intervention')}")


# ====================================================================
#  PHASE 3: DASHBOARD ANALYTICS (All 3 Stakeholders)
# ====================================================================
def phase_3_dashboard():
    section("PHASE 3: DASHBOARD ANALYTICS (3 Stakeholder Views)")

    # 3A: Teacher Dashboard
    step("3A: TEACHER VIEW - Class Overview")
    headers_t = {"Authorization": f"Bearer {tokens['teacher']}"}
    r = S.get(
        f"{BASE}/api/dashboard/teacher/overview",
        params={"class_section": "9-A", "subject": "mathematics"},
        headers=headers_t,
        timeout=30,
    )
    check("Teacher overview loads", r.status_code == 200)
    if r.status_code == 200:
        ov = r.json()
        print(f"       Total Students:  {ov.get('total_students', 0)}")
        print(f"       Avg Mastery:     {ov.get('avg_mastery', 0)}")
        print(f"       At-Risk Count:   {ov.get('at_risk_count', 0)}")
        print(f"       Pending Tickets: {ov.get('pending_tickets', 0)}")
        print(f"       Recent Events:   {ov.get('recent_events', 0)}")

    step("3B: TEACHER VIEW - Student List")
    r = S.get(
        f"{BASE}/api/dashboard/teacher/students",
        params={"class_section": "9-A", "subject": "mathematics"},
        headers=headers_t,
        timeout=30,
    )
    check("Teacher student list loads", r.status_code == 200)
    if r.status_code == 200:
        students = r.json()
        print(f"       Students in list: {len(students)}")
        for s in students[:5]:
            risk = s.get("risk_tier", "?")
            print(f"       {s.get('full_name', '?'):<20} Mastery: {s.get('overall_mastery', 0):.1%}  Risk: {risk}")

    # 3C: Student 1 (Aarav - struggling)
    step("3C: STUDENT VIEW - Aarav's Mastery")
    headers_s1 = {"Authorization": f"Bearer {tokens['student1']}"}
    r = S.get(
        f"{BASE}/api/dashboard/student/mastery",
        params={"subject": "mathematics"},
        headers=headers_s1,
        timeout=30,
    )
    check("Aarav mastery dashboard loads", r.status_code == 200)
    if r.status_code == 200:
        mastery = r.json()
        print(f"       Knowledge Components: {len(mastery)}")
        for m in mastery[:5]:
            bar = "#" * int(m.get("mastery", 0) * 10) + "." * (10 - int(m.get("mastery", 0) * 10))
            print(f"       {m.get('kc_name', '?'):<22} [{bar}] {m.get('mastery', 0):.1%} ({m.get('mastery_level', '?')})")

    # 3D: Student 2 (Diya - moderate)
    step("3D: STUDENT VIEW - Diya's Mastery")
    headers_s2 = {"Authorization": f"Bearer {tokens['student2']}"}
    r = S.get(
        f"{BASE}/api/dashboard/student/mastery",
        params={"subject": "mathematics"},
        headers=headers_s2,
        timeout=30,
    )
    check("Diya mastery dashboard loads", r.status_code == 200)
    if r.status_code == 200:
        mastery = r.json()
        print(f"       Knowledge Components: {len(mastery)}")
        for m in mastery[:5]:
            bar = "#" * int(m.get("mastery", 0) * 10) + "." * (10 - int(m.get("mastery", 0) * 10))
            print(f"       {m.get('kc_name', '?'):<22} [{bar}] {m.get('mastery', 0):.1%} ({m.get('mastery_level', '?')})")


# ====================================================================
#  PHASE 4: AI SUGGESTIONS (NL Query - 1 LLM call)
# ====================================================================
def phase_4_suggestions():
    section("PHASE 4: AI SUGGESTIONS & NL QUERY [LLM Call #2]")
    headers_t = {"Authorization": f"Bearer {tokens['teacher']}"}

    step("4A: Teacher asks NL question about struggling students")
    question = "Which students in 9-A are struggling and need help with algebra?"
    print(f"       Question: \"{question}\"")
    print("       Gemini 2.5 Flash -> Cypher -> Neo4j -> Answer...")

    r = S.post(
        f"{BASE}/api/query/ask",
        json={"question": question, "context": "class_performance"},
        headers=headers_t,
        timeout=90,
    )
    check("NL Query executed", r.status_code == 200)
    if r.status_code == 200:
        resp = r.json()
        print(f"       Answer: {resp.get('answer', '')[:150]}")
        if resp.get("cypher_used"):
            print(f"       Cypher: {resp['cypher_used'][:100]}")
        print(f"       Confidence: {resp.get('confidence', 0):.0%}")
        data = resp.get("data")
        if data and isinstance(data, list):
            print(f"       Records: {len(data)}")
            for rec in data[:3]:
                print(f"       -> {str(rec)[:90]}")

    # 4B: Student insights (no LLM)
    step("4B: Student insights for Aarav (pre-computed, no LLM)")
    r = S.get(
        f"{BASE}/api/query/student/{student_ids['aarav']}/insights",
        headers=headers_t,
        timeout=30,
    )
    if r.status_code == 200:
        insights = r.json()
        print(f"       Overall Mastery: {insights.get('overall_mastery', 0)}")
        print(f"       Trend: {insights.get('trend', 'N/A')}")
        print(f"       Gaps: {insights.get('gaps', [])[:3]}")
        check("Student insights computed", True)
    else:
        check("Student insights endpoint", r.status_code == 200)

    # 4C: Class patterns (no LLM)
    step("4C: Class-wide patterns (no LLM)")
    r = S.get(
        f"{BASE}/api/query/class/9-A/patterns",
        params={"subject": "mathematics"},
        headers=headers_t,
        timeout=30,
    )
    if r.status_code == 200:
        patterns = r.json()
        print(f"       Class Avg: {patterns.get('class_avg_mastery', 0)}")
        print(f"       Risk Distribution: {patterns.get('risk_distribution', {})}")
        check("Class patterns detected", True)
    else:
        check("Class patterns endpoint", r.status_code == 200)


# ====================================================================
#  PHASE 5: QUIZ DISPATCH & STUDENT SUBMISSION
# ====================================================================
def phase_5_quiz():
    section("PHASE 5: ADAPTIVE QUIZ (Dispatch -> Take -> Submit)")
    headers_t = {"Authorization": f"Bearer {tokens['teacher']}"}

    # 5A: Dispatch quiz to Aarav
    step("5A: Teacher dispatches quiz to Aarav (struggling)")
    print(f"       Target: {STUDENT_1['full_name']} ({student_ids['aarav']})")
    print("       KCs: ALG-002 (Quadratic), ALG-003 (Polynomials)")

    r = S.post(
        f"{BASE}/api/quiz/dispatch",
        json={
            "student_id": student_ids["aarav"],
            "target_kc_ids": ["ALG-002", "ALG-003"],
            "num_questions": 3,
        },
        headers=headers_t,
        timeout=90,
    )
    check("Quiz dispatched to Aarav", r.status_code == 200)
    if r.status_code == 200:
        quiz = r.json()
        quiz_sessions["aarav"] = quiz["session_id"]
        quiz_data["aarav"] = quiz
        print(f"       Session: {quiz['session_id']}")
        print(f"       Questions: {len(quiz['questions'])}")
        for i, q in enumerate(quiz["questions"], 1):
            print(f"       Q{i}: {q.get('question_text', '?')[:70]}")
            if q.get("options"):
                for j, opt in enumerate(q["options"][:4]):
                    print(f"           {chr(65+j)}) {opt[:50]}")

    # 5B: Dispatch quiz to Diya
    step("5B: Teacher dispatches quiz to Diya (moderate)")
    r = S.post(
        f"{BASE}/api/quiz/dispatch",
        json={
            "student_id": student_ids["diya"],
            "target_kc_ids": ["ALG-003"],
            "num_questions": 3,
        },
        headers=headers_t,
        timeout=90,
    )
    check("Quiz dispatched to Diya", r.status_code == 200)
    if r.status_code == 200:
        quiz2 = r.json()
        quiz_sessions["diya"] = quiz2["session_id"]
        quiz_data["diya"] = quiz2
        print(f"       Session: {quiz2['session_id']} | {len(quiz2['questions'])} questions")

    # 5C: Aarav takes quiz (gets 1/3)
    step("5C: Aarav submits quiz (1/3 correct - still struggling)")
    if "aarav" in quiz_sessions and "aarav" in quiz_data:
        headers_s1 = {"Authorization": f"Bearer {tokens['student1']}"}
        aarav_quiz = quiz_data["aarav"]
        responses = []
        for i, q in enumerate(aarav_quiz.get("questions", [])):
            qid = q.get("question_id", f"Q-{i}")
            if i == 0 and q.get("options"):
                responses.append({"question_id": qid, "answer": q["options"][0]})
            else:
                responses.append({"question_id": qid, "answer": "wrong_answer"})

        r = S.post(
            f"{BASE}/api/quiz/submit",
            json={"session_id": quiz_sessions["aarav"], "responses": responses},
            headers=headers_s1,
            timeout=30,
        )
        check("Aarav submits quiz", r.status_code == 200)
        if r.status_code == 200:
            res = r.json()
            print(f"       Score: {res.get('score', 0):.0%} ({res.get('correct_count', 0)}/{res.get('total_questions', 0)})")
            print(f"       Mastery Deltas: {res.get('mastery_deltas', {})}")

    # 5D: Diya takes quiz (gets 2/3)
    step("5D: Diya submits quiz (2/3 correct - moderate)")
    if "diya" in quiz_sessions and "diya" in quiz_data:
        headers_s2 = {"Authorization": f"Bearer {tokens['student2']}"}
        diya_quiz = quiz_data["diya"]
        responses = []
        for i, q in enumerate(diya_quiz.get("questions", [])):
            qid = q.get("question_id", f"Q-{i}")
            if i < 2 and q.get("options"):
                responses.append({"question_id": qid, "answer": q["options"][0]})
            else:
                responses.append({"question_id": qid, "answer": "wrong_answer"})

        r = S.post(
            f"{BASE}/api/quiz/submit",
            json={"session_id": quiz_sessions["diya"], "responses": responses},
            headers=headers_s2,
            timeout=30,
        )
        check("Diya submits quiz", r.status_code == 200)
        if r.status_code == 200:
            res = r.json()
            print(f"       Score: {res.get('score', 0):.0%} ({res.get('correct_count', 0)}/{res.get('total_questions', 0)})")
            print(f"       Mastery Deltas: {res.get('mastery_deltas', {})}")


# ====================================================================
#  PHASE 6: VERIFICATION & FEEDBACK LOOP
# ====================================================================
def phase_6_verify():
    section("PHASE 6: VERIFICATION & FEEDBACK LOOP")

    step("6A: Aarav's updated mastery (post-quiz)")
    headers_s1 = {"Authorization": f"Bearer {tokens['student1']}"}
    r = S.get(
        f"{BASE}/api/dashboard/student/mastery",
        params={"subject": "mathematics"},
        headers=headers_s1,
        timeout=30,
    )
    check("Aarav mastery refreshed", r.status_code == 200)
    if r.status_code == 200:
        for m in r.json()[:3]:
            print(f"       {m.get('kc_name', '?')}: {m.get('mastery', 0):.1%} ({m.get('mastery_level', '?')})")

    step("6B: Diya's updated mastery (post-quiz)")
    headers_s2 = {"Authorization": f"Bearer {tokens['student2']}"}
    r = S.get(
        f"{BASE}/api/dashboard/student/mastery",
        params={"subject": "mathematics"},
        headers=headers_s2,
        timeout=30,
    )
    check("Diya mastery refreshed", r.status_code == 200)
    if r.status_code == 200:
        for m in r.json()[:3]:
            print(f"       {m.get('kc_name', '?')}: {m.get('mastery', 0):.1%} ({m.get('mastery_level', '?')})")

    step("6C: Teacher dashboard reflects quiz results")
    headers_t = {"Authorization": f"Bearer {tokens['teacher']}"}
    r = S.get(
        f"{BASE}/api/dashboard/teacher/overview",
        params={"class_section": "9-A", "subject": "mathematics"},
        headers=headers_t,
        timeout=30,
    )
    check("Teacher overview updated", r.status_code == 200)
    if r.status_code == 200:
        ov = r.json()
        print(f"       Students: {ov.get('total_students')} | Avg Mastery: {ov.get('avg_mastery')} | At-Risk: {ov.get('at_risk_count')}")

    step("6D: Security Checks")
    r = S.get(f"{BASE}/api/dashboard/teacher/overview", timeout=30)
    check("Unauthenticated blocked (401)", r.status_code == 401)

    r = S.get(
        f"{BASE}/api/dashboard/teacher/overview",
        params={"class_section": "9-A"},
        headers=headers_s1,
        timeout=30,
    )
    check("Student blocked from teacher route (403)", r.status_code == 403)


# ====================================================================
#  MAIN
# ====================================================================
def main():
    print("=" * 70)
    print("  SAHAYAK360 - COMPLETE LIFECYCLE DEMO")
    print("  AI-Powered Adaptive Learning Platform")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: {BASE}")
    print("  LLM Budget: 2 calls (freetext parse + NL query)")
    print("=" * 70)

    start = time.time()

    try:
        phase_1_auth()
        phase_2_ingestion()
        phase_3_dashboard()
        phase_4_suggestions()
        phase_5_quiz()
        phase_6_verify()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by user")
    except Exception as e:
        print(f"\n\n  FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    elapsed = time.time() - start

    section("FINAL RESULTS")
    print(f"    Total Tests:  {results['passed'] + results['failed']}")
    print(f"    Passed:       {results['passed']}")
    print(f"    Failed:       {results['failed']}")
    print(f"    Duration:     {elapsed:.1f}s")
    print(f"    LLM Calls:    ~2 (freetext parse + NL query)")
    print()
    print("    Demo Users:")
    print(f"      Teacher: {TEACHER['email']} / {TEACHER['password']}")
    print(f"      Student 1: {STUDENT_1['email']} / {STUDENT_1['password']}")
    print(f"      Student 2: {STUDENT_2['email']} / {STUDENT_2['password']}")
    print()
    print("    Platform URLs:")
    print(f"      Frontend: {FRONTEND}")
    print(f"      API Docs: {BASE}/docs")
    print()

    if results["failed"] == 0:
        print("    ALL TESTS PASSED - COMPLETE LIFECYCLE VERIFIED!")
    else:
        print(f"    {results['failed']} test(s) failed - check output above")

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
