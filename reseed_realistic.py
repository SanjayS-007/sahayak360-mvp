"""
SAHAYAK360 - RESEED WITH REALISTIC DATA
==========================================
Updates mastery records to natural-looking values where students have
distinct performance profiles. No LLM calls needed.

Run: python reseed_realistic.py
"""

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://sahayak360-api.onrender.com"
PASSWORD = "Demo@2026Secure"

S = requests.Session()
S.verify = False


# ══════════════════════════════════════════════════════════════
# REALISTIC MASTERY PROFILES
# ══════════════════════════════════════════════════════════════
# Each student has unique, natural-looking mastery per KC
# Mimics real classroom: some good at algebra, weak at geometry, etc.

REALISTIC_MASTERY = {
    "STU-2001": {  # Aarav Patel - Struggling overall, but decent at statistics
        "ALG-001": 0.32, "ALG-002": 0.18, "ALG-003": 0.22, "ALG-004": 0.15,
        "GEO-001": 0.28, "GEO-002": 0.20, "GEO-003": 0.12,
        "STAT-001": 0.48, "STAT-002": 0.38, "TRIG-001": 0.14,
    },
    "STU-2002": {  # Diya Gupta - Solid performer, strong algebra, weak geometry
        "ALG-001": 0.78, "ALG-002": 0.72, "ALG-003": 0.68, "ALG-004": 0.65,
        "GEO-001": 0.52, "GEO-002": 0.45, "GEO-003": 0.38,
        "STAT-001": 0.82, "STAT-002": 0.70, "TRIG-001": 0.55,
    },
    "STU-2003": {  # Arjun Nair - At risk, inconsistent
        "ALG-001": 0.35, "ALG-002": 0.28, "ALG-003": 0.42, "ALG-004": 0.20,
        "GEO-001": 0.30, "GEO-002": 0.18, "GEO-003": 0.25,
        "STAT-001": 0.55, "STAT-002": 0.32, "TRIG-001": 0.15,
    },
    "STU-2004": {  # Ananya Reddy - Good all-rounder
        "ALG-001": 0.82, "ALG-002": 0.75, "ALG-003": 0.70, "ALG-004": 0.72,
        "GEO-001": 0.78, "GEO-002": 0.68, "GEO-003": 0.62,
        "STAT-001": 0.88, "STAT-002": 0.80, "TRIG-001": 0.65,
    },
    "STU-2005": {  # Vivaan Singh - Top student, excellent everywhere
        "ALG-001": 0.92, "ALG-002": 0.88, "ALG-003": 0.85, "ALG-004": 0.90,
        "GEO-001": 0.94, "GEO-002": 0.82, "GEO-003": 0.78,
        "STAT-001": 0.95, "STAT-002": 0.90, "TRIG-001": 0.85,
    },
    "STU-2006": {  # Ishita Sharma - Average, improving in algebra
        "ALG-001": 0.62, "ALG-002": 0.55, "ALG-003": 0.48, "ALG-004": 0.42,
        "GEO-001": 0.58, "GEO-002": 0.50, "GEO-003": 0.35,
        "STAT-001": 0.65, "STAT-002": 0.52, "TRIG-001": 0.40,
    },
    "STU-2007": {  # Rohan Mehta - Above avg, strong geo, weak trig
        "ALG-001": 0.70, "ALG-002": 0.62, "ALG-003": 0.58, "ALG-004": 0.55,
        "GEO-001": 0.85, "GEO-002": 0.78, "GEO-003": 0.72,
        "STAT-001": 0.75, "STAT-002": 0.68, "TRIG-001": 0.38,
    },
    "STU-2008": {  # Kavya Iyer - Excellent, consistent high performer
        "ALG-001": 0.90, "ALG-002": 0.85, "ALG-003": 0.82, "ALG-004": 0.80,
        "GEO-001": 0.88, "GEO-002": 0.85, "GEO-003": 0.75,
        "STAT-001": 0.92, "STAT-002": 0.88, "TRIG-001": 0.78,
    },
    "STU-2009": {  # Aditya Joshi (9-B) - Moderate, weak in factorization
        "ALG-001": 0.58, "ALG-002": 0.45, "ALG-003": 0.52, "ALG-004": 0.28,
        "GEO-001": 0.60, "GEO-002": 0.48, "GEO-003": 0.35,
        "STAT-001": 0.62, "STAT-002": 0.55, "TRIG-001": 0.42,
    },
    "STU-2010": {  # Meera Krishnan (9-B) - Good, geometry star
        "ALG-001": 0.72, "ALG-002": 0.65, "ALG-003": 0.60, "ALG-004": 0.58,
        "GEO-001": 0.90, "GEO-002": 0.85, "GEO-003": 0.80,
        "STAT-001": 0.75, "STAT-002": 0.70, "TRIG-001": 0.62,
    },
    # Additional students for 9-A (to make class size 15 realistic)
    "STU-2011": {  # Priya Verma - Moderate, needs help with advanced topics
        "ALG-001": 0.65, "ALG-002": 0.48, "ALG-003": 0.42, "ALG-004": 0.35,
        "GEO-001": 0.62, "GEO-002": 0.55, "GEO-003": 0.30,
        "STAT-001": 0.72, "STAT-002": 0.60, "TRIG-001": 0.28,
    },
    "STU-2012": {  # Karthik Rajan - Good conceptual understanding
        "ALG-001": 0.75, "ALG-002": 0.70, "ALG-003": 0.72, "ALG-004": 0.68,
        "GEO-001": 0.65, "GEO-002": 0.60, "GEO-003": 0.55,
        "STAT-001": 0.80, "STAT-002": 0.72, "TRIG-001": 0.58,
    },
    "STU-2013": {  # Sneha Kulkarni - Struggling with abstractions
        "ALG-001": 0.40, "ALG-002": 0.30, "ALG-003": 0.25, "ALG-004": 0.22,
        "GEO-001": 0.45, "GEO-002": 0.32, "GEO-003": 0.20,
        "STAT-001": 0.52, "STAT-002": 0.40, "TRIG-001": 0.18,
    },
    "STU-2014": {  # Rahul Deshmukh - Average but steady
        "ALG-001": 0.60, "ALG-002": 0.55, "ALG-003": 0.50, "ALG-004": 0.48,
        "GEO-001": 0.58, "GEO-002": 0.52, "GEO-003": 0.45,
        "STAT-001": 0.68, "STAT-002": 0.58, "TRIG-001": 0.42,
    },
    "STU-2015": {  # Nisha Agarwal - Strong in stats, weak in geometry
        "ALG-001": 0.68, "ALG-002": 0.60, "ALG-003": 0.55, "ALG-004": 0.50,
        "GEO-001": 0.42, "GEO-002": 0.35, "GEO-003": 0.28,
        "STAT-001": 0.88, "STAT-002": 0.82, "TRIG-001": 0.45,
    },
    # Additional 9-B students
    "STU-2016": {  # Vikram Choudhury (9-B) - Bright but careless
        "ALG-001": 0.78, "ALG-002": 0.72, "ALG-003": 0.65, "ALG-004": 0.70,
        "GEO-001": 0.75, "GEO-002": 0.68, "GEO-003": 0.60,
        "STAT-001": 0.82, "STAT-002": 0.75, "TRIG-001": 0.62,
    },
    "STU-2017": {  # Lakshmi Narayan (9-B) - Needs support
        "ALG-001": 0.38, "ALG-002": 0.30, "ALG-003": 0.35, "ALG-004": 0.25,
        "GEO-001": 0.42, "GEO-002": 0.28, "GEO-003": 0.22,
        "STAT-001": 0.50, "STAT-002": 0.42, "TRIG-001": 0.20,
    },
    "STU-2018": {  # Deepa Menon (9-B) - Above average
        "ALG-001": 0.72, "ALG-002": 0.68, "ALG-003": 0.62, "ALG-004": 0.60,
        "GEO-001": 0.70, "GEO-002": 0.65, "GEO-003": 0.58,
        "STAT-001": 0.78, "STAT-002": 0.72, "TRIG-001": 0.55,
    },
}

# Additional users to register (to make 9-A have ~15 and 9-B have ~8)
EXTRA_STUDENTS = [
    {"user_id": "STU-2011", "email": "student11@school.com", "full_name": "Priya Verma", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2012", "email": "student12@school.com", "full_name": "Karthik Rajan", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2013", "email": "student13@school.com", "full_name": "Sneha Kulkarni", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2014", "email": "student14@school.com", "full_name": "Rahul Deshmukh", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2015", "email": "student15@school.com", "full_name": "Nisha Agarwal", "role": "student", "class_section": "9-A"},
    {"user_id": "STU-2016", "email": "student16@school.com", "full_name": "Vikram Choudhury", "role": "student", "class_section": "9-B"},
    {"user_id": "STU-2017", "email": "student17@school.com", "full_name": "Lakshmi Narayan", "role": "student", "class_section": "9-B"},
    {"user_id": "STU-2018", "email": "student18@school.com", "full_name": "Deepa Menon", "role": "student", "class_section": "9-B"},
]

KC_NAMES = {
    "ALG-001": "Linear Equations", "ALG-002": "Quadratic Equations",
    "ALG-003": "Polynomials", "ALG-004": "Factorization",
    "GEO-001": "Triangles & Congruence", "GEO-002": "Coordinate Geometry",
    "GEO-003": "Circles & Theorems", "STAT-001": "Mean, Median, Mode",
    "STAT-002": "Probability Basics", "TRIG-001": "Trigonometric Ratios",
}


def mastery_level(m):
    if m >= 0.85:
        return "mastered"
    elif m >= 0.65:
        return "proficient"
    elif m >= 0.40:
        return "developing"
    else:
        return "beginning"


def main():
    print("═" * 60)
    print("  SAHAYAK360 REALISTIC DATA RESEED")
    print("═" * 60)

    # Step 1: Login as teacher to get token
    print("\n[1] Logging in as teacher...")
    r = S.post(f"{BASE}/api/auth/login", json={"email": "teacher1@school.com", "password": PASSWORD}, timeout=30)
    if r.status_code != 200:
        print(f"  FAILED: {r.status_code} {r.text[:100]}")
        return
    teacher_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {teacher_token}"}
    print("  ✓ Teacher authenticated")

    # Step 2: Register extra students
    print("\n[2] Registering additional students...")
    for student in EXTRA_STUDENTS:
        payload = {
            "email": student["email"],
            "password": PASSWORD,
            "full_name": student["full_name"],
            "role": "student",
            "user_id": student["user_id"],
            "class_section": student["class_section"],
        }
        r = S.post(f"{BASE}/api/auth/register", json=payload, timeout=30)
        if r.status_code == 201:
            print(f"  ✓ Registered {student['full_name']} ({student['class_section']})")
        elif r.status_code == 409:
            print(f"  - Already exists: {student['full_name']}")
        else:
            print(f"  ✗ Failed {student['full_name']}: {r.status_code}")

    # Step 3: Ingest assessment data for ALL students with realistic scores
    print("\n[3] Ingesting realistic assessment data...")
    from datetime import date, timedelta
    today = date.today()

    success = 0
    for student_id, kc_data in REALISTIC_MASTERY.items():
        # Determine class section
        if student_id in ["STU-2009", "STU-2010", "STU-2016", "STU-2017", "STU-2018"]:
            class_section = "9-B"
            teacher_id = "TCH-1002"
        else:
            class_section = "9-A"
            teacher_id = "TCH-1001"

        # Create 3 assessment events per student (spread over 3 weeks)
        for week in range(3):
            assess_date = today - timedelta(days=(2 - week) * 7)
            items = []
            total = 0.0

            for kc_id, target_mastery in kc_data.items():
                # Add slight variance per week (improving trend)
                import random
                random.seed(hash(f"{student_id}-{kc_id}-{week}"))
                variance = random.uniform(-0.08, 0.08)
                week_bonus = week * 0.03  # slight improvement over time
                score_pct = max(0.0, min(1.0, target_mastery + variance + week_bonus - 0.05))
                obtained = round(score_pct * 10, 1)
                total += obtained
                items.append({
                    "question_id": f"R-W{week+1}-{kc_id}-{student_id[-4:]}",
                    "knowledge_component_id": kc_id,
                    "knowledge_component_name": KC_NAMES[kc_id],
                    "max_marks": 10.0,
                    "obtained_marks": obtained,
                    "is_correct": obtained >= 4.0,
                })

            payload = {
                "teacher_id": teacher_id,
                "student_id": student_id,
                "class_section": class_section,
                "subject": "mathematics",
                "department_id": "DEPT-MATH",
                "assessment_type": "formative",
                "assessment_date": str(assess_date),
                "max_score": 100.0,
                "total_obtained": round(total, 1),
                "items": items,
            }

            for attempt in range(3):
                try:
                    r = S.post(f"{BASE}/api/ingest/structured", json=payload, headers=headers, timeout=120)
                    if r.status_code == 200:
                        success += 1
                    else:
                        print(f"  ✗ {student_id} W{week+1}: {r.status_code} {r.text[:80]}")
                    break
                except Exception as e:
                    if attempt < 2:
                        import time; time.sleep(5)
                    else:
                        print(f"  ✗ {student_id} W{week+1}: {e}")

    print(f"  ✓ Ingested {success} assessment events")

    # Step 4: Verify
    print("\n[4] Verifying dashboard data...")
    r = S.get(f"{BASE}/api/dashboard/teacher/overview", params={"class_section": "9-A"}, headers=headers, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"  ✓ 9-A: {data['total_students']} students | Avg mastery: {data['avg_mastery']:.1%}")
        rd = data.get("risk_distribution", {})
        print(f"    Risk: low={rd.get('low',0)} moderate={rd.get('moderate',0)} high={rd.get('high',0)} critical={rd.get('critical',0)}")
    else:
        print(f"  ✗ Overview failed: {r.status_code}")

    r2 = S.get(f"{BASE}/api/dashboard/teacher/students", params={"class_section": "9-A"}, headers=headers, timeout=30)
    if r2.status_code == 200:
        students = r2.json()
        print(f"\n  Student Performance (9-A):")
        for s in sorted(students, key=lambda x: x["overall_mastery"], reverse=True):
            bar = "█" * int(s["overall_mastery"] * 10) + "░" * (10 - int(s["overall_mastery"] * 10))
            print(f"    {s['full_name']:<20} {bar} {s['overall_mastery']:.0%} [{s['risk_tier']}]")

    print("\n" + "═" * 60)
    print("  DONE — Realistic data seeded!")
    print("═" * 60)


if __name__ == "__main__":
    main()
