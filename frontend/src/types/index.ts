// --- User ---
export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: "teacher" | "student" | "admin" | "parent";
  class_section?: string;
  department_id?: string;
}

// --- Auth ---
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  role: "teacher" | "student" | "admin" | "parent";
  full_name: string;
}

// --- Score Item ---
export interface ScoreItem {
  question_id: string;
  knowledge_component_id: string;
  knowledge_component_name: string;
  max_marks: number;
  obtained_marks: number;
  is_correct: boolean;
}

// --- Ingest ---
export interface IngestResponse {
  status: string;
  event_id: string | null;
  parse_method: string;
  validation: ValidationResult;
  cognitive_analysis?: Record<string, unknown>;
  graph_mutations: string[];
}

export interface ValidationResult {
  sum_check_passed: boolean;
  computed_sum: number;
  declared_total: number;
  discrepancy: number;
  anomaly_flags: string[];
}

// --- Dashboard ---
export interface ClassAnalytics {
  total_students: number;
  class_avg_mastery: number;
  risk_distribution: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
  struggling_kcs: KCInfo[];
  recent_events: number;
  open_tickets: number;
}

export interface KCInfo {
  kc_id: string;
  kc_name: string;
  avg_mastery: number;
  student_count?: number;
}

export interface StudentProfile {
  student_id: string;
  overall_mastery: number;
  trend: "improving" | "stable" | "declining";
  gaps: KCInfo[];
  strengths: KCInfo[];
  assessment_count: number;
}

// --- Quiz ---
export interface QuizQuestion {
  question_id: string;
  kc_id: string;
  question_text: string;
  options: string[];
  bloom_level: string;
}

export interface QuizSession {
  session_id: string;
  questions: QuizQuestion[];
  time_limit_seconds: number;
}

export interface QuizResult {
  session_id: string;
  score: number;
  correct_count: number;
  total_questions: number;
  mastery_deltas: Record<string, number>;
}

// --- Query ---
export interface QueryResponse {
  answer: string;
  data?: unknown;
  cypher_used?: string;
  confidence: number;
}

// --- Risk Tier ---
export type RiskTier = "low" | "moderate" | "high" | "critical";
