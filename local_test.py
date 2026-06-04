"""
SAHAYAK360 - LOCAL QUICK TEST (Run anytime to verify deployment)
================================================================
Quick verification script - tests all critical paths in ~30 seconds.
No new user registration - uses fixed test credentials.
Run: python local_test.py
"""

import sys
import time
import urllib3

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://sahayak360-api.onrender.com"
VERIFY = False

# Fixed demo credentials (permanent accounts with rich data)
# Run seed_demo_data.py to recreate if needed
TEACHER_EMAIL = "teacher1@school.com"
TEACHER_PASS = "Demo@2026Secure"
STUDENT_EMAIL = "student1@school.com"
STUDENT_PASS = "Demo@2026Secure"

passed = 0
failed = 0


def test(name, condition):
    global passed, failed
    icon = "[+]" if condition else "[-]"
    print(f"  {icon} {name}")
    if condition:
        passed += 1
    else:
        failed += 1
    return condition


def main():
    global passed, failed
    print(f"\n  SAHAYAK360 Quick Test | {BASE}")
    print(f"  {'=' * 50}")

    S = requests.Session()
    S.verify = VERIFY
    start = time.time()

    # 1. Health
    r = S.get(f"{BASE}/health", timeout=30)
    test("Health check", r.status_code == 200)

    # 2. Login teacher
    r = S.post(f"{BASE}/api/auth/login", json={
        "email": TEACHER_EMAIL, "password": TEACHER_PASS
    }, timeout=30)
    teacher_ok = test("Teacher login", r.status_code == 200)
    teacher_token = r.json().get("access_token", "") if teacher_ok else ""

    # 3. Login student
    r = S.post(f"{BASE}/api/auth/login", json={
        "email": STUDENT_EMAIL, "password": STUDENT_PASS
    }, timeout=30)
    student_ok = test("Student login", r.status_code == 200)
    student_token = r.json().get("access_token", "") if student_ok else ""

    # 4. Teacher dashboard
    if teacher_token:
        h = {"Authorization": f"Bearer {teacher_token}"}
        r = S.get(f"{BASE}/api/dashboard/teacher/overview",
                  params={"class_section": "9-A"}, headers=h, timeout=30)
        test("Teacher dashboard", r.status_code == 200)

        # 5. Structured ingest
        r = S.post(f"{BASE}/api/ingest/structured", json={
            "teacher_id": "TCH-1001",
            "student_id": "STU-2001",
            "class_section": "9-A",
            "subject": "mathematics",
            "department_id": "DEPT-MATH",
            "assessment_type": "formative",
            "max_score": 10,
            "total_obtained": 6,
            "items": [{
                "question_id": "Q-QUICK",
                "knowledge_component_id": "ALG-001",
                "knowledge_component_name": "Linear Equations",
                "max_marks": 10,
                "obtained_marks": 6,
                "is_correct": True,
            }],
        }, headers=h, timeout=30)
        test("Structured ingest", r.status_code == 200)

        # 6. NL Query (1 LLM call)
        r = S.post(f"{BASE}/api/query/ask", json={
            "question": "How many students are at risk in 9-A?",
            "context": "general",
        }, headers=h, timeout=90)
        test("NL Query (Gemini)", r.status_code == 200)
        if r.status_code == 200:
            print(f"       Answer: {r.json().get('answer', '')[:80]}")

    # 7. Student dashboard
    if student_token:
        h = {"Authorization": f"Bearer {student_token}"}
        r = S.get(f"{BASE}/api/dashboard/student/mastery",
                  params={"subject": "mathematics"}, headers=h, timeout=30)
        test("Student mastery", r.status_code == 200)

    # 8. Security
    r = S.get(f"{BASE}/api/dashboard/teacher/overview", timeout=30)
    test("Auth guard (401)", r.status_code == 401)

    if student_token:
        r = S.get(f"{BASE}/api/dashboard/teacher/overview",
                  params={"class_section": "9-A"},
                  headers={"Authorization": f"Bearer {student_token}"}, timeout=30)
        test("Role guard (403)", r.status_code == 403)

    elapsed = time.time() - start
    print(f"\n  {'=' * 50}")
    print(f"  Results: {passed}/{passed+failed} passed | {elapsed:.1f}s")
    if failed == 0:
        print("  ALL PASSED!")
    else:
        print(f"  {failed} FAILED")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
