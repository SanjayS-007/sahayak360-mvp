"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { dashboardApi, queryApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { formatPercentage, getRiskBadgeColor } from "@/lib/utils";
import { Search, TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { StudentProfile } from "@/types";

interface StudentSummary {
  student_id: string;
  full_name: string;
  overall_mastery: number;
  trend: string;
  risk_tier: string;
}

export default function TeacherStudentsPage() {
  const { user } = useAuthStore();
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadStudents();
  }, []);

  async function loadStudents() {
    try {
      const { data } = await dashboardApi.studentList(user?.class_section || "8-A");
      setStudents(data || []);
    } catch {
      toast.error("Failed to load students");
    } finally {
      setLoading(false);
    }
  }

  async function selectStudent(studentId: string) {
    try {
      const { data } = await queryApi.studentInsights(studentId);
      setSelectedStudent(data);
    } catch {
      toast.error("Failed to load student details");
    }
  }

  const filtered = students.filter(
    (s) =>
      s.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      s.student_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Students</h2>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Student List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search students..."
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
              <div className="space-y-2">
                {filtered.map((student) => (
                  <button
                    key={student.student_id}
                    onClick={() => selectStudent(student.student_id)}
                    className={`w-full rounded-lg border bg-white p-4 text-left transition-colors hover:border-primary-300 ${
                      selectedStudent?.student_id === student.student_id
                        ? "border-primary-500 ring-1 ring-primary-500"
                        : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{student.full_name}</p>
                        <p className="text-xs text-gray-500">{student.student_id}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        {student.trend === "improving" && <TrendingUp className="h-4 w-4 text-accent-600" />}
                        {student.trend === "declining" && <TrendingDown className="h-4 w-4 text-danger-500" />}
                        {student.trend === "stable" && <Minus className="h-4 w-4 text-gray-400" />}
                        <Badge className={getRiskBadgeColor(student.risk_tier)}>
                          {formatPercentage(student.overall_mastery)}
                        </Badge>
                      </div>
                    </div>
                  </button>
                ))}
                {filtered.length === 0 && (
                  <p className="text-center text-sm text-gray-500 py-8">No students found</p>
                )}
              </div>
            )}
          </div>

          {/* Student Detail */}
          <div>
            {selectedStudent ? (
              <Card className="sticky top-24">
                <CardHeader>
                  <CardTitle>{selectedStudent.student_id}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-500">Overall Mastery</p>
                    <p className="text-2xl font-bold">{formatPercentage(selectedStudent.overall_mastery)}</p>
                    <Progress value={selectedStudent.overall_mastery * 100} className="mt-1" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Trend</p>
                    <Badge variant={
                      selectedStudent.trend === "improving" ? "success" :
                      selectedStudent.trend === "declining" ? "danger" : "outline"
                    }>
                      {selectedStudent.trend}
                    </Badge>
                  </div>
                  {selectedStudent.gaps.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Gaps</p>
                      <div className="space-y-1">
                        {selectedStudent.gaps.map((g) => (
                          <div key={g.kc_id} className="flex items-center justify-between text-xs">
                            <span className="text-gray-600">{g.kc_name}</span>
                            <span className="font-medium text-danger-600">
                              {formatPercentage(g.avg_mastery)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex h-48 items-center justify-center text-sm text-gray-400">
                  Select a student to view details
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
