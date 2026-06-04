"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { dashboardApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { getRiskBadgeColor } from "@/lib/utils";
import { Search, TrendingUp, TrendingDown, Minus, ChevronRight } from "lucide-react";

interface StudentSummary {
  student_id: string;
  full_name: string;
  overall_mastery: number;
  trend: string;
  risk_tier: string;
}

export default function TeacherStudentsPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  const loadStudents = useCallback(async () => {
    try {
      const { data } = await dashboardApi.studentList(user?.class_section || "9-A");
      setStudents(data || []);
    } catch {
      toast.error("Failed to load students");
    } finally {
      setLoading(false);
    }
  }, [user?.class_section]);

  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  const filtered = students.filter(
    (s) =>
      s.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      s.student_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Students</h2>

        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search by name or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((student) => {
              const masteryPct = Math.round(student.overall_mastery * 100);
              const borderColor =
                student.risk_tier === "low" ? "border-l-emerald-500" :
                student.risk_tier === "moderate" ? "border-l-blue-500" :
                student.risk_tier === "high" ? "border-l-amber-500" : "border-l-red-500";
              return (
                <button
                  key={student.student_id}
                  onClick={() => router.push(`/teacher/students/${student.student_id}`)}
                  className={`group relative rounded-xl border-l-4 ${borderColor} border bg-white p-4 text-left shadow-sm hover:shadow-md transition-all`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold text-gray-900">{student.full_name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{student.student_id}</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-300 group-hover:text-gray-600 transition-colors" />
                  </div>
                  <div className="mt-3 flex items-center gap-3">
                    <div className="flex-1 h-2 rounded-full bg-gray-100 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${
                          masteryPct >= 70 ? "bg-emerald-500" :
                          masteryPct >= 50 ? "bg-blue-500" :
                          masteryPct >= 30 ? "bg-amber-500" : "bg-red-500"
                        }`}
                        style={{ width: `${masteryPct}%` }}
                      />
                    </div>
                    <span className="text-sm font-bold text-gray-700 w-10 text-right">{masteryPct}%</span>
                  </div>
                  <div className="mt-2 flex items-center justify-between">
                    <Badge className={`text-xs ${getRiskBadgeColor(student.risk_tier)}`}>
                      {student.risk_tier}
                    </Badge>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      {student.trend === "improving" && <TrendingUp className="h-3 w-3 text-emerald-500" />}
                      {student.trend === "declining" && <TrendingDown className="h-3 w-3 text-red-500" />}
                      {student.trend === "stable" && <Minus className="h-3 w-3 text-gray-400" />}
                      <span className="capitalize">{student.trend || "stable"}</span>
                    </div>
                  </div>
                </button>
              );
            })}
            {filtered.length === 0 && (
              <p className="col-span-full text-center text-sm text-gray-500 py-8">No students found</p>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
