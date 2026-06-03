import { create } from "zustand";
import type { ClassAnalytics, StudentProfile } from "@/types";

interface DashboardState {
  classAnalytics: ClassAnalytics | null;
  selectedStudent: StudentProfile | null;
  isLoading: boolean;
  error: string | null;
  setClassAnalytics: (data: ClassAnalytics) => void;
  setSelectedStudent: (data: StudentProfile | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  classAnalytics: null,
  selectedStudent: null,
  isLoading: false,
  error: null,
  setClassAnalytics: (data) => set({ classAnalytics: data, error: null }),
  setSelectedStudent: (data) => set({ selectedStudent: data }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
