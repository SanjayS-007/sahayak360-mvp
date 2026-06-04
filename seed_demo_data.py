"""
SAHAYAK360 - SEED DEMO DATA (No LLM calls)
============================================
Creates 15 users (3 teachers, 10 students, 2 admins) with rich historical
assessment data spanning 4 weeks. All structured ingestion (fast_lane).

Emails: teacher1@school.com, student1@school.com, admin1@school.com
Password for ALL: Demo@2026Secure

Run once: python seed_demo_data.py
"""

import json
import random
import sys
import time
import urllib3
from datetime import date, timedelta

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://sahayak360-api.onrender.com"
VERIFY = False
PASSWORD = "Demo@2026Secure"

S = requests.Session()
S.verify = VERIFY

# ══════════════════════════════════════════════════════════════
# DEMO USERS
# ══════════════════════════════════════════════════════════════

TEACHERS = [
    {"user_id": "TCH-1001", "email": "teacher1@school.com", "full_name": "Ms. Priya Sharma", "role": "teacher", "class_section": "9-A", "department_id": "DEPT-MATH"},
    {"user_id": "TCH-1002", "email": "teacher2@school.com", "full_name": "Mr. Rajesh Kumar", "role": "teacher", "class_section": "9-B", "department_id": "DEPT-SCI"},
    {"user_id": "TCH-1003", "email": "teacher3@school.com", "full_name": "Ms. Anita Desai", "role": "teacher", "class_section": "9-A", "department_id": "DEPT-ENG"},
]

STUDENTS = [
    {"user_id": "STU-2001", "email": "student1@school.com", "full_name": "Aarav Patel", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2002", "email": "student2@school.com", "full_name": "Diya Gupta", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2003", "email": "student3@school.com", "full_name": "Arjun Nair", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2004", "email": "student4@school.com", "full_name": "Ananya Reddy", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2005", "email": "student5@school.com", "full_name": "Vivaan Singh", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2006", "email": "student6@school.com", "full_name": "Ishita Sharma", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2007", "email": "student7@school.com", "full_name": "Rohan Mehta", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2008", "email": "student8@school.com", "full_name": "Kavya Iyer", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2009", "email": "student9@school.com", "full_name": "Aditya Joshi", "role": "student", "class_section": "9-B"},
    {"user_id": "STU-2010", "email": "student10@school.com", "full_name": "Meera Krishnan", "role": "student", "class_section": "9-B"},
]

ADMINS = [
    {"user_id": "ADM-3001", "email": "admin1@school.com", "full_name": "Dr. Suresh Menon", "role": "admin"},
    {"user_id": "ADM-3002", "email": "admin2@school.com", "full_name": "Ms. Lakshmi Rao", "role": "admin"},
]

# ══════════════════════════════════════════════════════════════
# KNOWLEDGE COMPONENTS (Mathematics - Grade 9)
# ══════════════════════════════════════════════════════════════

KNOWLEDGE_COMPONENTS = [
    {"id": "ALG-001", "name": "Linear Equations", "subject": "mathematics"},
    {"id": "ALG-002", "name": "Quadratic Equations", "subject": "mathematics"},
    {"id": "ALG-003", "name": "Polynomials", "subject": "mathematics"},
    {"id": "ALG-004", "name": "Factorization", "subject": "mathematics"},
    {"id": "GEO-001", "name": "Triangles & Congruence", "subject": "mathematics"},
    {"id": "GEO-002", "name": "Coordinate Geometry", "subject": "mathematics"},
    {"id": "GEO-003", "name": "Circles & Theorems", "subject": "mathematics"},
    {"id": "STAT-001", "name": "Mean, Median, Mode", "subject": "mathematics"},
    {"id": "STAT-002", "name": "Probability Basics", "subject": "mathematics"},
    {"id": "TRIG-001", "name": "Trigonometric Ratios", "subject": "mathematics"},
]

# ══════════════════════════════════════════════════════════════
# STUDENT PERFORMANCE PROFILES (determines their score patterns)
# ══════════════════════════════════════════════════════════════

# Each student has a base ability per KC that improves slightly over weeks
STUDENT_PROFILES = {
    "STU-2001": {"label": "struggling", "base": 0.35, "growth": 0.04, "variance": 0.12,   # Aarav - at risk but with strengths
                 "kc_strengths": {"STAT-001": 0.60, "GEO-001": 0.50, "ALG-001": 0.40, "ALG-004": 0.15, "TRIG-001": 0.18}},
    "STU-2002": {"label": "moderate", "base": 0.55, "growth": 0.04, "variance": 0.08,     # Diya - improving
                 "kc_strengths": {"STAT-001": 0.70, "ALG-001": 0.60, "TRIG-001": 0.35}},
    "STU-2003": {"label": "struggling", "base": 0.30, "growth": 0.02, "variance": 0.12,   # Arjun - at risk
                 "kc_strengths": {"GEO-001": 0.55, "STAT-002": 0.45, "ALG-003": 0.15}},
    "STU-2004": {"label": "good", "base": 0.70, "growth": 0.03, "variance": 0.07,         # Ananya - solid
                 "kc_strengths": {"ALG-001": 0.85, "STAT-001": 0.80, "TRIG-001": 0.50}},
    "STU-2005": {"label": "excellent", "base": 0.85, "growth": 0.02, "variance": 0.05,    # Vivaan - top
                 "kc_strengths": {"ALG-002": 0.90, "GEO-003": 0.75}},
    "STU-2006": {"label": "moderate", "base": 0.50, "growth": 0.05, "variance": 0.10,     # Ishita - growing
                 "kc_strengths": {"STAT-001": 0.65, "GEO-002": 0.55, "ALG-004": 0.30}},
    "STU-2007": {"label": "good", "base": 0.65, "growth": 0.03, "variance": 0.08,         # Rohan - above avg
                 "kc_strengths": {"ALG-001": 0.80, "ALG-002": 0.70, "GEO-003": 0.45}},
    "STU-2008": {"label": "excellent", "base": 0.80, "growth": 0.02, "variance": 0.05,    # Kavya - top
                 "kc_strengths": {"TRIG-001": 0.85, "ALG-004": 0.75}},
    "STU-2009": {"label": "moderate", "base": 0.45, "growth": 0.04, "variance": 0.10,     # Aditya - 9-B
                 "kc_strengths": {"STAT-002": 0.60, "GEO-001": 0.55, "ALG-003": 0.25}},
    "STU-2010": {"label": "good", "base": 0.68, "growth": 0.03, "variance": 0.07,         # Meera - 9-B
                 "kc_strengths": {"ALG-001": 0.78, "STAT-001": 0.75, "GEO-003": 0.50}},
}

# Per-KC difficulty multiplier (some KCs are harder)
KC_DIFFICULTY = {
    "ALG-001": 1.0,   # Linear Equations - baseline
    "ALG-002": 0.85,  # Quadratic - harder
    "ALG-003": 0.80,  # Polynomials - harder
    "ALG-004": 0.75,  # Factorization - hardest algebra
    "GEO-001": 0.95,  # Triangles - moderate
    "GEO-002": 0.80,  # Coordinate - harder
    "GEO-003": 0.70,  # Circles - hardest geometry
    "STAT-001": 1.05,  # Statistics - easier
    "STAT-002": 0.90,  # Probability - moderate
    "TRIG-001": 0.75,  # Trig - hardest
}


def compute_score(student_id, kc_id, week):
    """Compute a realistic score for a student on a KC in a given week."""
    profile = STUDENT_PROFILES[student_id]
    difficulty = KC_DIFFICULTY[kc_id]
    
    # Use per-KC strength if available, otherwise fall back to base
    kc_strengths = profile.get("kc_strengths", {})
    base_ability = kc_strengths.get(kc_id, profile["base"])
    
    base = base_ability * difficulty
    growth = profile["growth"] * week
    noise = random.uniform(-profile["variance"], profile["variance"])
    
    score = base + growth + noise
    return max(0.0, min(1.0, score))  # Clamp 0-1


def section(title):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def step(msg):
    print(f"  → {msg}")


# ══════════════════════════════════════════════════════════════
# PHASE 1: REGISTER ALL USERS
# ══════════════════════════════════════════════════════════════

def phase_1_register():
    section("PHASE 1: REGISTER 15 DEMO USERS")
    tokens = {}
    
    all_users = TEACHERS + STUDENTS + ADMINS
    for user in all_users:
        payload = {
            "email": user["email"],
            "password": PASSWORD,
            "full_name": user["full_name"],
            "role": user["role"],
            "user_id": user["user_id"],
        }
        if user.get("class_section"):
            payload["class_section"] = user["class_section"]
        if user.get("department_id"):
            payload["department_id"] = user["department_id"]
        
        r = S.post(f"{BASE}/api/auth/register", json=payload, timeout=30)
        if r.status_code == 201:
            tokens[user["user_id"]] = r.json()["access_token"]
            step(f"✓ {user['role']:7} | {user['email']:<24} | {user['full_name']}")
        elif r.status_code == 409:
            # Already exists - login instead
            r2 = S.post(f"{BASE}/api/auth/login", json={"email": user["email"], "password": PASSWORD}, timeout=30)
            if r2.status_code == 200:
                tokens[user["user_id"]] = r2.json()["access_token"]
                step(f"✓ {user['role']:7} | {user['email']:<24} | {user['full_name']} (exists)")
            else:
                step(f"✗ {user['role']:7} | {user['email']:<24} | FAILED ({r2.status_code})")
        else:
            step(f"✗ {user['role']:7} | {user['email']:<24} | FAILED ({r.status_code}: {r.text[:60]})")
    
    print(f"\n  Tokens obtained: {len(tokens)}/15")
    return tokens


# ══════════════════════════════════════════════════════════════
# PHASE 2: INGEST 4 WEEKS OF ASSESSMENT DATA
# ══════════════════════════════════════════════════════════════

def phase_2_ingest(tokens):
    section("PHASE 2: INGEST 4 WEEKS OF ASSESSMENT DATA (No LLM)")
    
    teacher_token = tokens.get("TCH-1001")
    if not teacher_token:
        print("  ERROR: No teacher token available!")
        return 0
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # 4 weeks of data: Week 1 = 4 weeks ago, Week 4 = this week
    today = date.today()
    weeks = [
        today - timedelta(days=28),  # Week 1
        today - timedelta(days=21),  # Week 2
        today - timedelta(days=14),  # Week 3
        today - timedelta(days=7),   # Week 4
    ]
    
    total_ingested = 0
    failed = 0
    
    # Each week, each student gets tested on 4-6 random KCs
    for week_num, week_date in enumerate(weeks, 1):
        step(f"Week {week_num} (date: {week_date}) — ingesting assessments...")
        
        week_count = 0
        for student in STUDENTS:
            student_id = student["user_id"]
            class_section = student["class_section"]
            
            # Pick 4-6 KCs for this week's test
            num_kcs = random.randint(4, 6)
            test_kcs = random.sample(KNOWLEDGE_COMPONENTS, num_kcs)
            
            # Build items
            items = []
            total_obtained = 0
            max_score = num_kcs * 10
            
            for kc in test_kcs:
                score_pct = compute_score(student_id, kc["id"], week_num)
                obtained = round(score_pct * 10, 1)
                obtained = min(10.0, max(0.0, obtained))
                total_obtained += obtained
                items.append({
                    "question_id": f"W{week_num}-{kc['id']}-{student_id[-4:]}",
                    "knowledge_component_id": kc["id"],
                    "knowledge_component_name": kc["name"],
                    "max_marks": 10.0,
                    "obtained_marks": obtained,
                    "is_correct": obtained >= 5.0,
                })
            
            # Determine teacher based on class
            teacher_id = "TCH-1001" if class_section == "9-A" else "TCH-1002"
            
            payload = {
                "teacher_id": teacher_id,
                "student_id": student_id,
                "class_section": class_section,
                "subject": "mathematics",
                "department_id": "DEPT-MATH",
                "assessment_type": "formative",
                "assessment_date": str(week_date),
                "max_score": max_score,
                "total_obtained": round(total_obtained, 1),
                "items": items,
            }
            
            r = S.post(f"{BASE}/api/ingest/structured", json=payload, headers=headers, timeout=30)
            if r.status_code == 200:
                week_count += 1
                total_ingested += 1
            else:
                failed += 1
                if failed <= 3:
                    print(f"    WARN: {student['full_name']} W{week_num} failed: {r.status_code}")
        
        print(f"    Week {week_num}: {week_count}/10 students ingested")
    
    # Extra: Ingest a "today" snapshot with latest performance
    step("Current week snapshot (today's formative test)...")
    today_count = 0
    for student in STUDENTS:
        student_id = student["user_id"]
        class_section = student["class_section"]
        teacher_id = "TCH-1001" if class_section == "9-A" else "TCH-1002"
        
        # Full 10-KC test for today
        items = []
        total_obtained = 0
        for kc in KNOWLEDGE_COMPONENTS:
            score_pct = compute_score(student_id, kc["id"], 5)  # Week 5 = latest
            obtained = round(score_pct * 10, 1)
            obtained = min(10.0, max(0.0, obtained))
            total_obtained += obtained
            items.append({
                "question_id": f"TODAY-{kc['id']}-{student_id[-4:]}",
                "knowledge_component_id": kc["id"],
                "knowledge_component_name": kc["name"],
                "max_marks": 10.0,
                "obtained_marks": obtained,
                "is_correct": obtained >= 5.0,
            })
        
        payload = {
            "teacher_id": teacher_id,
            "student_id": student_id,
            "class_section": class_section,
            "subject": "mathematics",
            "department_id": "DEPT-MATH",
            "assessment_type": "formative",
            "assessment_date": str(today),
            "max_score": 100.0,
            "total_obtained": round(total_obtained, 1),
            "items": items,
        }
        
        r = S.post(f"{BASE}/api/ingest/structured", json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            today_count += 1
            total_ingested += 1
        else:
            failed += 1
    
    print(f"    Today's test: {today_count}/10 students")
    print(f"\n  TOTAL: {total_ingested} assessments ingested | {failed} failed")
    return total_ingested


# ══════════════════════════════════════════════════════════════
# PHASE 3: VERIFY DASHBOARDS
# ══════════════════════════════════════════════════════════════

def phase_3_verify(tokens):
    section("PHASE 3: VERIFY ALL STAKEHOLDER DASHBOARDS")
    
    passed = 0
    failed = 0
    
    def check(name, ok):
        nonlocal passed, failed
        if ok:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}")
        return ok
    
    # --- Teacher 1 Dashboard (9-A) ---
    print("\n  ── TEACHER VIEW (Ms. Priya Sharma - 9-A) ──")
    t_token = tokens.get("TCH-1001")
    if t_token:
        h = {"Authorization": f"Bearer {t_token}"}
        
        r = S.get(f"{BASE}/api/dashboard/teacher/overview",
                  params={"class_section": "9-A", "subject": "mathematics"}, headers=h, timeout=30)
        check("Teacher overview loads", r.status_code == 200)
        if r.status_code == 200:
            ov = r.json()
            print(f"       Students: {ov.get('total_students')} | Avg Mastery: {ov.get('avg_mastery'):.1%} | At-Risk: {ov.get('at_risk_count')} | Events: {ov.get('recent_events')}")
        
        r = S.get(f"{BASE}/api/dashboard/teacher/students",
                  params={"class_section": "9-A", "subject": "mathematics"}, headers=h, timeout=30)
        check("Teacher student list loads", r.status_code == 200)
        if r.status_code == 200:
            students = r.json()
            print(f"       Student list ({len(students)} students):")
            for s in sorted(students, key=lambda x: x.get("overall_mastery", 0), reverse=True)[:8]:
                m = s.get("overall_mastery", 0)
                risk = s.get("risk_tier", "?")
                bar = "█" * int(m * 10) + "░" * (10 - int(m * 10))
                print(f"       {s.get('full_name', '?'):<20} [{bar}] {m:.1%}  ({risk})")
    
    # --- Student Dashboards (sample 3) ---
    print("\n  ── STUDENT VIEWS ──")
    
    sample_students = [
        ("STU-2001", "Aarav (struggling)"),
        ("STU-2005", "Vivaan (excellent)"),
        ("STU-2006", "Ishita (growing)"),
    ]
    
    for stu_id, label in sample_students:
        token = tokens.get(stu_id)
        if not token:
            continue
        h = {"Authorization": f"Bearer {token}"}
        
        r = S.get(f"{BASE}/api/dashboard/student/mastery",
                  params={"subject": "mathematics"}, headers=h, timeout=30)
        check(f"{label} mastery loads", r.status_code == 200)
        if r.status_code == 200:
            mastery = r.json()
            for m in mastery[:5]:
                val = m.get("mastery", 0)
                bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
                print(f"       {m.get('kc_name', '?'):<22} [{bar}] {val:.1%} ({m.get('mastery_level', '?')})")
            if len(mastery) > 5:
                print(f"       ... +{len(mastery)-5} more KCs")
    
    # --- Admin view (Teacher 2 - 9-B) ---
    print("\n  ── TEACHER 2 VIEW (Mr. Rajesh - 9-B) ──")
    t2_token = tokens.get("TCH-1002")
    if t2_token:
        h = {"Authorization": f"Bearer {t2_token}"}
        r = S.get(f"{BASE}/api/dashboard/teacher/overview",
                  params={"class_section": "9-B", "subject": "mathematics"}, headers=h, timeout=30)
        check("Teacher 2 overview (9-B)", r.status_code == 200)
        if r.status_code == 200:
            ov = r.json()
            print(f"       Students: {ov.get('total_students')} | Avg Mastery: {ov.get('avg_mastery'):.1%} | At-Risk: {ov.get('at_risk_count')}")
    
    # --- Security checks ---
    print("\n  ── SECURITY ──")
    r = S.get(f"{BASE}/api/dashboard/teacher/overview", timeout=30)
    check("Unauthenticated → 401", r.status_code == 401)
    
    stu_token = tokens.get("STU-2001")
    if stu_token:
        r = S.get(f"{BASE}/api/dashboard/teacher/overview",
                  headers={"Authorization": f"Bearer {stu_token}"}, timeout=30)
        check("Student → teacher route = 403", r.status_code == 403)
    
    # --- Quiz dispatch test ---
    print("\n  ── QUIZ SYSTEM ──")
    if t_token:
        h = {"Authorization": f"Bearer {t_token}"}
        r = S.post(f"{BASE}/api/quiz/dispatch", json={
            "student_id": "STU-2001",
            "target_kc_ids": ["ALG-002", "ALG-004", "TRIG-001"],
            "num_questions": 3,
        }, headers=h, timeout=60)
        check("Quiz dispatch to struggling student", r.status_code == 200)
        if r.status_code == 200:
            quiz = r.json()
            print(f"       Session: {quiz.get('session_id')} | Questions: {len(quiz.get('questions', []))}")
            
            # Student submits
            stu_h = {"Authorization": f"Bearer {tokens.get('STU-2001', '')}"}
            responses = [{"question_id": q["question_id"], "answer": q.get("options", ["A"])[0]}
                        for q in quiz.get("questions", [])]
            r2 = S.post(f"{BASE}/api/quiz/submit", json={
                "session_id": quiz["session_id"],
                "responses": responses,
            }, headers=stu_h, timeout=30)
            check("Student submits quiz", r2.status_code == 200)
            if r2.status_code == 200:
                res = r2.json()
                print(f"       Score: {res.get('score', 0):.0%} | Deltas: {res.get('mastery_deltas', {})}")
    
    print(f"\n  RESULTS: {passed} passed | {failed} failed")
    return failed == 0


# ══════════════════════════════════════════════════════════════
# PHASE 4: SAVE demo_users.json
# ══════════════════════════════════════════════════════════════

def phase_4_save_json():
    section("PHASE 4: SAVE demo_users.json")
    
    demo_data = {
        "platform": {
            "frontend": "https://sahayak360-mvp.vercel.app",
            "api": "https://sahayak360-api.onrender.com",
            "api_docs": "https://sahayak360-api.onrender.com/docs",
        },
        "password_for_all": PASSWORD,
        "teachers": [
            {
                "email": t["email"],
                "password": PASSWORD,
                "user_id": t["user_id"],
                "full_name": t["full_name"],
                "class_section": t.get("class_section", "N/A"),
                "subject": "mathematics",
            }
            for t in TEACHERS
        ],
        "students": [
            {
                "email": s["email"],
                "password": PASSWORD,
                "user_id": s["user_id"],
                "full_name": s["full_name"],
                "class_section": s["class_section"],
                "performance_level": STUDENT_PROFILES[s["user_id"]]["label"],
            }
            for s in STUDENTS
        ],
        "admins": [
            {
                "email": a["email"],
                "password": PASSWORD,
                "user_id": a["user_id"],
                "full_name": a["full_name"],
            }
            for a in ADMINS
        ],
        "knowledge_components": KNOWLEDGE_COMPONENTS,
        "data_coverage": {
            "weeks_of_history": 4,
            "assessments_per_student_per_week": "4-6 KCs tested",
            "total_assessments": "~50 assessment events",
            "subjects": ["mathematics"],
            "classes": ["9-A", "9-B"],
        },
        "demo_scenarios": {
            "struggling_students": ["student1@school.com (Aarav)", "student3@school.com (Arjun)"],
            "top_performers": ["student5@school.com (Vivaan)", "student8@school.com (Kavya)"],
            "improving_students": ["student2@school.com (Diya)", "student6@school.com (Ishita)"],
            "teacher_9A": "teacher1@school.com (Ms. Priya Sharma)",
            "teacher_9B": "teacher2@school.com (Mr. Rajesh Kumar)",
        },
    }
    
    with open("demo_users.json", "w", encoding="utf-8") as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)
    
    step("Saved demo_users.json")
    print(f"    Teachers: {len(TEACHERS)}")
    print(f"    Students: {len(STUDENTS)}")
    print(f"    Admins:   {len(ADMINS)}")
    print(f"    Total:    15 users")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  SAHAYAK360 — SEED DEMO DATA")
    print("  15 users + 4 weeks of assessment history")
    print("  NO LLM CALLS — all structured ingestion")
    print(f"  Target: {BASE}")
    print("═" * 60)
    
    start = time.time()
    
    # Phase 1: Register users
    tokens = phase_1_register()
    if len(tokens) < 5:
        print("\n  FATAL: Not enough tokens. Aborting.")
        return 1
    
    # Phase 2: Ingest 4 weeks of data
    total = phase_2_ingest(tokens)
    if total == 0:
        print("\n  FATAL: No data ingested. Aborting.")
        return 1
    
    # Phase 3: Verify dashboards
    phase_3_verify(tokens)
    
    # Phase 4: Save credentials
    phase_4_save_json()
    
    elapsed = time.time() - start
    
    section("COMPLETE")
    print(f"  Duration: {elapsed:.1f}s")
    print(f"  Assessments: {total}")
    print(f"  Users: 15 (3 teachers + 10 students + 2 admins)")
    print()
    print("  LOGIN CREDENTIALS (all use password: Demo@2026Secure):")
    print("  ┌─────────────────────────────────────────────────────┐")
    print("  │ TEACHERS                                            │")
    print("  │   teacher1@school.com  Ms. Priya Sharma    (9-A)    │")
    print("  │   teacher2@school.com  Mr. Rajesh Kumar    (9-B)    │")
    print("  │   teacher3@school.com  Ms. Anita Desai     (9-A)    │")
    print("  │ STUDENTS                                            │")
    print("  │   student1@school.com  Aarav Patel   (9-A,struggle) │")
    print("  │   student2@school.com  Diya Gupta    (9-A,moderate) │")
    print("  │   student3@school.com  Arjun Nair    (9-A,struggle) │")
    print("  │   student4@school.com  Ananya Reddy  (9-A,good)     │")
    print("  │   student5@school.com  Vivaan Singh  (9-A,excellent)│")
    print("  │   student6@school.com  Ishita Sharma (9-A,growing)  │")
    print("  │   student7@school.com  Rohan Mehta   (9-A,good)     │")
    print("  │   student8@school.com  Kavya Iyer    (9-A,excellent)│")
    print("  │   student9@school.com  Aditya Joshi  (9-B,moderate) │")
    print("  │   student10@school.com Meera Krishnan(9-B,good)     │")
    print("  │ ADMINS                                              │")
    print("  │   admin1@school.com    Dr. Suresh Menon             │")
    print("  │   admin2@school.com    Ms. Lakshmi Rao              │")
    print("  └─────────────────────────────────────────────────────┘")
    print()
    print("  Now login at: https://sahayak360-mvp.vercel.app")
    return 0


if __name__ == "__main__":
    sys.exit(main())
