// Sahayak 360 — Neo4j Knowledge Graph Seed Data
// Run: cat seed_neo4j.cypher | cypher-shell -u neo4j -p <password>

// ─── Subject Nodes ───
MERGE (math:Subject {subject_id: 'SUBJ-MATH', name: 'Mathematics', grade: 8});
MERGE (sci:Subject {subject_id: 'SUBJ-SCI', name: 'Science', grade: 8});

// ─── Topic Nodes ───
MERGE (fractions:Topic {topic_id: 'TOPIC-FRAC', name: 'Fractions', subject_id: 'SUBJ-MATH'});
MERGE (algebra:Topic {topic_id: 'TOPIC-ALG', name: 'Algebra', subject_id: 'SUBJ-MATH'});
MERGE (geometry:Topic {topic_id: 'TOPIC-GEO', name: 'Geometry', subject_id: 'SUBJ-MATH'});

// ─── Knowledge Components (KCs) ───
MERGE (kc1:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-01', name: 'Basic Fractions', subject: 'mathematics', grade_level: 8, bloom_level: 'understand'});
MERGE (kc2:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-02', name: 'Equivalent Fractions', subject: 'mathematics', grade_level: 8, bloom_level: 'apply'});
MERGE (kc3:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-03', name: 'Fraction Addition', subject: 'mathematics', grade_level: 8, bloom_level: 'apply'});
MERGE (kc4:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-04', name: 'Fraction Multiplication', subject: 'mathematics', grade_level: 8, bloom_level: 'apply'});
MERGE (kc5:KnowledgeComponent {kc_id: 'KC-MATH-ALG-01', name: 'Linear Equations', subject: 'mathematics', grade_level: 8, bloom_level: 'apply'});
MERGE (kc6:KnowledgeComponent {kc_id: 'KC-MATH-ALG-02', name: 'Solving for X', subject: 'mathematics', grade_level: 8, bloom_level: 'analyze'});
MERGE (kc7:KnowledgeComponent {kc_id: 'KC-MATH-GEO-01', name: 'Angles', subject: 'mathematics', grade_level: 8, bloom_level: 'understand'});
MERGE (kc8:KnowledgeComponent {kc_id: 'KC-MATH-GEO-02', name: 'Triangles', subject: 'mathematics', grade_level: 8, bloom_level: 'apply'});

// ─── Prerequisite Relationships ───
MATCH (a:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-01'}), (b:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-02'})
MERGE (a)-[:PREREQUISITE_OF]->(b);

MATCH (a:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-02'}), (b:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-03'})
MERGE (a)-[:PREREQUISITE_OF]->(b);

MATCH (a:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-02'}), (b:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-04'})
MERGE (a)-[:PREREQUISITE_OF]->(b);

MATCH (a:KnowledgeComponent {kc_id: 'KC-MATH-ALG-01'}), (b:KnowledgeComponent {kc_id: 'KC-MATH-ALG-02'})
MERGE (a)-[:PREREQUISITE_OF]->(b);

MATCH (a:KnowledgeComponent {kc_id: 'KC-MATH-GEO-01'}), (b:KnowledgeComponent {kc_id: 'KC-MATH-GEO-02'})
MERGE (a)-[:PREREQUISITE_OF]->(b);

// ─── Topic → KC Relationships ───
MATCH (t:Topic {topic_id: 'TOPIC-FRAC'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-01'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-FRAC'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-02'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-FRAC'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-03'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-FRAC'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-04'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-ALG'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-ALG-01'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-ALG'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-ALG-02'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-GEO'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-GEO-01'}) MERGE (t)-[:CONTAINS]->(kc);
MATCH (t:Topic {topic_id: 'TOPIC-GEO'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-GEO-02'}) MERGE (t)-[:CONTAINS]->(kc);

// ─── Subject → Topic ───
MATCH (s:Subject {subject_id: 'SUBJ-MATH'}), (t:Topic {topic_id: 'TOPIC-FRAC'}) MERGE (s)-[:HAS_TOPIC]->(t);
MATCH (s:Subject {subject_id: 'SUBJ-MATH'}), (t:Topic {topic_id: 'TOPIC-ALG'}) MERGE (s)-[:HAS_TOPIC]->(t);
MATCH (s:Subject {subject_id: 'SUBJ-MATH'}), (t:Topic {topic_id: 'TOPIC-GEO'}) MERGE (s)-[:HAS_TOPIC]->(t);

// ─── Student Mastery Edges ───
MERGE (s1:Student {student_id: 'STU-01', name: 'Ravi Shankar', class_section: '8-A'});
MERGE (s2:Student {student_id: 'STU-02', name: 'Anita Devi', class_section: '8-A'});
MERGE (s3:Student {student_id: 'STU-03', name: 'Vijay Patel', class_section: '8-A'});
MERGE (s4:Student {student_id: 'STU-04', name: 'Meena Kumari', class_section: '8-A'});
MERGE (s5:Student {student_id: 'STU-05', name: 'Karthik Raja', class_section: '8-A'});

// STU-01 mastery
MATCH (s:Student {student_id: 'STU-01'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-01'})
MERGE (s)-[:HAS_MASTERY {mastery: 0.35, mastery_level: 'below_basic', attempts: 4, last_updated: datetime()}]->(kc);
MATCH (s:Student {student_id: 'STU-01'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-02'})
MERGE (s)-[:HAS_MASTERY {mastery: 0.25, mastery_level: 'below_basic', attempts: 3, last_updated: datetime()}]->(kc);
MATCH (s:Student {student_id: 'STU-01'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-ALG-01'})
MERGE (s)-[:HAS_MASTERY {mastery: 0.72, mastery_level: 'proficient', attempts: 5, last_updated: datetime()}]->(kc);

// STU-03 mastery (critical risk)
MATCH (s:Student {student_id: 'STU-03'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-FRAC-01'})
MERGE (s)-[:HAS_MASTERY {mastery: 0.15, mastery_level: 'below_basic', attempts: 2, last_updated: datetime()}]->(kc);
MATCH (s:Student {student_id: 'STU-03'}), (kc:KnowledgeComponent {kc_id: 'KC-MATH-ALG-01'})
MERGE (s)-[:HAS_MASTERY {mastery: 0.30, mastery_level: 'below_basic', attempts: 3, last_updated: datetime()}]->(kc);
