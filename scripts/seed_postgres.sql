-- Sahayak 360 — PostgreSQL Seed Data for Hackathon Demo
-- Run: psql -U sahayak -d sahayak360 -f seed_postgres.sql

-- Institution
INSERT INTO institutions (institution_id, name, type) VALUES
    ('INST-01', 'Government Higher Secondary School, Madurai', 'school')
ON CONFLICT (institution_id) DO NOTHING;

-- Department
INSERT INTO departments (department_id, institution_id, name, subject) VALUES
    ('DEPT-MATH', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'Mathematics', 'mathematics'),
    ('DEPT-SCI', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'Science', 'science'),
    ('DEPT-ENG', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'English', 'english')
ON CONFLICT (department_id) DO NOTHING;

-- Users (password: "demo1234" hashed with bcrypt)
-- $2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS
INSERT INTO users (user_id, email, hashed_password, full_name, role, institution_id, department_id, class_section) VALUES
    ('TCH-01', 'priya@school.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Dr. Priya Sharma', 'teacher', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-MATH', '8-A'),
    ('TCH-02', 'arun@school.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Mr. Arun Kumar', 'teacher', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-SCI', '8-A'),
    ('STU-01', 'ravi@student.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Ravi Shankar', 'student', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-MATH', '8-A'),
    ('STU-02', 'anita@student.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Anita Devi', 'student', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-MATH', '8-A'),
    ('STU-03', 'vijay@student.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Vijay Patel', 'student', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-MATH', '8-A'),
    ('STU-04', 'meena@student.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Meena Kumari', 'student', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-MATH', '8-A'),
    ('STU-05', 'karthik@student.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Karthik Raja', 'student', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), 'DEPT-MATH', '8-A'),
    ('ADM-01', 'admin@school.edu', '$2b$12$LJ3RQKlN5F0K4fBkNj5YhOGt.Ky3jjlBXiY8dKUmO9QqF2pxwXyuS', 'Admin User', 'admin', (SELECT id FROM institutions WHERE institution_id = 'INST-01'), NULL, NULL)
ON CONFLICT (user_id) DO NOTHING;

-- Mastery Records (simulating ongoing learning state)
INSERT INTO mastery_records (student_id, kc_id, kc_name, subject, mastery, mastery_level, attempts) VALUES
    -- STU-01 (Ravi) — struggling in fractions
    ('STU-01', 'KC-MATH-FRAC-01', 'Basic Fractions', 'mathematics', 0.35, 'developing', 4),
    ('STU-01', 'KC-MATH-FRAC-02', 'Equivalent Fractions', 'mathematics', 0.25, 'beginning', 3),
    ('STU-01', 'KC-MATH-FRAC-03', 'Fraction Addition', 'mathematics', 0.20, 'beginning', 2),
    ('STU-01', 'KC-MATH-ALG-01', 'Linear Equations', 'mathematics', 0.72, 'proficient', 5),
    ('STU-01', 'KC-MATH-GEO-01', 'Angles', 'mathematics', 0.88, 'mastered', 6),
    -- STU-02 (Anita) — strong overall
    ('STU-02', 'KC-MATH-FRAC-01', 'Basic Fractions', 'mathematics', 0.90, 'mastered', 5),
    ('STU-02', 'KC-MATH-FRAC-02', 'Equivalent Fractions', 'mathematics', 0.85, 'mastered', 4),
    ('STU-02', 'KC-MATH-ALG-01', 'Linear Equations', 'mathematics', 0.78, 'proficient', 5),
    ('STU-02', 'KC-MATH-GEO-01', 'Angles', 'mathematics', 0.92, 'mastered', 4),
    -- STU-03 (Vijay) — critical risk
    ('STU-03', 'KC-MATH-FRAC-01', 'Basic Fractions', 'mathematics', 0.15, 'beginning', 2),
    ('STU-03', 'KC-MATH-FRAC-02', 'Equivalent Fractions', 'mathematics', 0.10, 'not_attempted', 1),
    ('STU-03', 'KC-MATH-ALG-01', 'Linear Equations', 'mathematics', 0.30, 'beginning', 3),
    ('STU-03', 'KC-MATH-GEO-01', 'Angles', 'mathematics', 0.45, 'developing', 3),
    -- STU-04 (Meena) — moderate
    ('STU-04', 'KC-MATH-FRAC-01', 'Basic Fractions', 'mathematics', 0.62, 'developing', 4),
    ('STU-04', 'KC-MATH-FRAC-02', 'Equivalent Fractions', 'mathematics', 0.55, 'developing', 3),
    ('STU-04', 'KC-MATH-ALG-01', 'Linear Equations', 'mathematics', 0.68, 'proficient', 4),
    ('STU-04', 'KC-MATH-GEO-01', 'Angles', 'mathematics', 0.75, 'proficient', 5),
    -- STU-05 (Karthik) — improving
    ('STU-05', 'KC-MATH-FRAC-01', 'Basic Fractions', 'mathematics', 0.70, 'proficient', 5),
    ('STU-05', 'KC-MATH-FRAC-02', 'Equivalent Fractions', 'mathematics', 0.65, 'proficient', 4),
    ('STU-05', 'KC-MATH-ALG-01', 'Linear Equations', 'mathematics', 0.58, 'developing', 4),
    ('STU-05', 'KC-MATH-GEO-01', 'Angles', 'mathematics', 0.80, 'proficient', 5)
ON CONFLICT DO NOTHING;

-- Sample Assessment Events
INSERT INTO assessment_events (event_id, student_id, teacher_id, institution_id, department_id, class_section, subject, channel, assessment_type, max_score, total_obtained, items, cognitive_analysis) VALUES
    ('EVT-DEMO0001', 'STU-01', 'TCH-01', 'INST-01', 'DEPT-MATH', '8-A', 'mathematics', 'SWIPE_PWA', 'formative', 10, 6, '[{"question_id": "Q-01", "knowledge_component_id": "KC-MATH-FRAC-01", "knowledge_component_name": "Basic Fractions", "max_marks": 2, "obtained_marks": 1, "is_correct": false}, {"question_id": "Q-02", "knowledge_component_id": "KC-MATH-FRAC-02", "knowledge_component_name": "Equivalent Fractions", "max_marks": 2, "obtained_marks": 0, "is_correct": false}]', '{"gaps": [{"kc_id": "KC-MATH-FRAC-02", "severity": "critical", "mastery": 0.25}], "needs_intervention": true, "risk_tier": "high", "composite_risk": 0.72}'),
    ('EVT-DEMO0002', 'STU-02', 'TCH-01', 'INST-01', 'DEPT-MATH', '8-A', 'mathematics', 'SWIPE_PWA', 'formative', 10, 9, '[{"question_id": "Q-01", "knowledge_component_id": "KC-MATH-FRAC-01", "knowledge_component_name": "Basic Fractions", "max_marks": 2, "obtained_marks": 2, "is_correct": true}]', '{"gaps": [], "needs_intervention": false, "risk_tier": "low", "composite_risk": 0.15}'),
    ('EVT-DEMO0003', 'STU-03', 'TCH-01', 'INST-01', 'DEPT-MATH', '8-A', 'mathematics', 'FREETEXT', 'formative', 10, 2, '[]', '{"gaps": [{"kc_id": "KC-MATH-FRAC-01", "severity": "critical", "mastery": 0.15}], "needs_intervention": true, "risk_tier": "critical", "composite_risk": 0.88}')
ON CONFLICT (event_id) DO NOTHING;

-- Sample Intervention Tickets
INSERT INTO intervention_tickets (ticket_id, student_id, teacher_id, ticket_type, priority, status, target_kc_id, target_kc_name, description) VALUES
    ('TKT-001', 'STU-01', 'TCH-01', 'micro_test', 'P2', 'open', 'KC-MATH-FRAC-02', 'Equivalent Fractions', 'Student needs additional practice on equivalent fractions — mastery at 25%'),
    ('TKT-002', 'STU-03', 'TCH-01', 'remedial_content', 'P1', 'assigned', 'KC-MATH-FRAC-01', 'Basic Fractions', 'CRITICAL: Student at 15% mastery in basic fractions — requires immediate intervention'),
    ('TKT-003', 'STU-03', 'TCH-01', 'parent_meeting', 'P1', 'open', 'KC-MATH-FRAC-01', 'Basic Fractions', 'Parent meeting recommended — student consistently below threshold')
ON CONFLICT (ticket_id) DO NOTHING;
