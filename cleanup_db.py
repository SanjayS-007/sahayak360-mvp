"""
Clean up database: remove test users, old mastery records, and assessment events.
Then reseed will produce clean realistic data.
"""
import psycopg2

# External connection string (Render external hostname)
CONN = "postgresql://sahayak360_e5rn_user:hiSNKWWuNFHvcv4obFQZ51Nn2h5iPNUn@dpg-d8g53ruk1jcs73d71nd0-a.oregon-postgres.render.com/sahayak360_e5rn"

# Valid student IDs we want to keep
VALID_STUDENTS = [
    "STU-2001", "STU-2002", "STU-2003", "STU-2004", "STU-2005",
    "STU-2006", "STU-2007", "STU-2008", "STU-2009", "STU-2010",
    "STU-2011", "STU-2012", "STU-2013", "STU-2014", "STU-2015",
    "STU-2016", "STU-2017", "STU-2018",
]

VALID_TEACHERS = ["TCH-1001", "TCH-1002", "TCH-1003"]
VALID_ADMINS = ["ADM-3001", "ADM-3002"]
ALL_VALID = VALID_STUDENTS + VALID_TEACHERS + VALID_ADMINS


def main():
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(CONN)
    cur = conn.cursor()

    # 1. Count current state
    cur.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    print(f"  Current students: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM mastery_records")
    print(f"  Current mastery records: {cur.fetchone()[0]}")
    cur.execute("SELECT COUNT(*) FROM assessment_events")
    print(f"  Current assessment events: {cur.fetchone()[0]}")

    # 2. Delete ALL mastery records (will be recreated by reseed)
    cur.execute("DELETE FROM mastery_records")
    print(f"  Deleted all mastery_records: {cur.rowcount} rows")

    # 3. Delete ALL assessment events
    cur.execute("DELETE FROM assessment_events")
    print(f"  Deleted all assessment_events: {cur.rowcount} rows")

    # 4. Delete ALL intervention tickets
    cur.execute("DELETE FROM intervention_tickets")
    print(f"  Deleted all intervention_tickets: {cur.rowcount} rows")

    # 5. Delete ALL quiz sessions
    cur.execute("DELETE FROM quiz_sessions")
    print(f"  Deleted all quiz_sessions: {cur.rowcount} rows")

    # 6. Delete test/duplicate users (keep only valid IDs)
    cur.execute("DELETE FROM users WHERE user_id NOT IN %s", (tuple(ALL_VALID),))
    print(f"  Deleted invalid users: {cur.rowcount} rows")

    # 7. Verify clean state
    cur.execute("SELECT user_id, full_name, class_section FROM users WHERE role='student' ORDER BY user_id")
    students = cur.fetchall()
    print(f"\n  Clean student list ({len(students)}):")
    for uid, name, section in students:
        print(f"    {uid} | {name:<20} | {section}")

    conn.commit()
    cur.close()
    conn.close()
    print("\n  ✓ Database cleaned!")


if __name__ == "__main__":
    main()
