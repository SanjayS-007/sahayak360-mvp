import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("sahayak_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("sahayak_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;

// --- Auth ---
export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    role: string;
    user_id: string;
    class_section?: string;
    department_id?: string;
  }) => api.post("/auth/register", data),
  getProfile: () => api.get("/auth/me"),
};

// --- Ingest ---
export const ingestApi = {
  structured: (data: Record<string, unknown>) =>
    api.post("/ingest/structured", data),
  freetext: (data: { teacher_id: string; raw_text: string; class_section?: string; subject?: string }) =>
    api.post("/ingest/freetext", data),
  vision: (formData: FormData) =>
    api.post("/ingest/vision", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

// --- Dashboard ---
export const dashboardApi = {
  teacherOverview: (classSection: string, subject?: string) =>
    api.get(`/dashboard/teacher/overview?class_section=${classSection}${subject ? `&subject=${subject}` : ""}`),
  studentList: (classSection: string, subject?: string) =>
    api.get(`/dashboard/teacher/students?class_section=${classSection}${subject ? `&subject=${subject}` : ""}`),
  studentDetail: (studentId: string, subject?: string) =>
    api.get(`/dashboard/teacher/student-detail/${studentId}${subject ? `?subject=${subject}` : ""}`),
  studentMastery: (subject?: string) =>
    api.get(`/dashboard/student/mastery${subject ? `?subject=${subject}` : ""}`),
  studentAnalytics: (subject?: string) =>
    api.get(`/dashboard/student/analytics${subject ? `?subject=${subject}` : ""}`),
  adminOverview: () => api.get("/dashboard/admin/overview"),
};

// --- Query ---
export const queryApi = {
  ask: (question: string) => api.post("/query/ask", { question }),
  studentInsights: (studentId: string) =>
    api.get(`/query/student/${studentId}/insights`),
  classPatterns: (classSection: string, subject?: string) =>
    api.get(`/query/class/${classSection}/patterns${subject ? `?subject=${subject}` : ""}`),
};

// --- Quiz ---
export const quizApi = {
  dispatch: (data: { student_id: string; target_kc_ids: string[]; num_questions?: number }) =>
    api.post("/quiz/dispatch", data),
  submit: (sessionId: string, responses: Array<{ question_id: string; answer: string }>) =>
    api.post("/quiz/submit", { session_id: sessionId, responses }),
  getSession: (sessionId: string) => api.get(`/quiz/${sessionId}`),
};
