"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { dashboardApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { formatPercentage } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus, Target, Award } from "lucide-react";

interface MasteryData {
  student_id: string;
  overall_mastery: number;
  trend: string;
  total_kcs: number;
  gaps: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  strengths: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  assessment_count: number;
  recent_scores: number[];
}

export default function StudentDashboard() {
  const { user } = useAuthStore();
  const [data, setData] = useState<MasteryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const { data: mastery } = await dashboardApi.studentMastery("mathematics");
      setData(mastery);
    } catch {
      toast.error("Failed to load your progress");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <AppShell requiredRole="student">
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">My Progress</h2>

        {/* Summary */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Overall Mastery</p>
                  <p className="text-3xl font-bold">{formatPercentage(data?.overall_mastery ?? 0)}</p>
                </div>
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary-100">
                  <Target className="h-6 w-6 text-primary-600" />
                </div>
              </div>
              <Progress value={(data?.overall_mastery ?? 0) * 100} className="mt-3" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Trend</p>
                  <p className="text-lg font-semibold capitalize">{data?.trend ?? "stable"}</p>
                </div>
                {data?.trend === "improving" && <TrendingUp className="h-8 w-8 text-accent-600" />}
                {data?.trend === "declining" && <TrendingDown className="h-8 w-8 text-danger-500" />}
                {data?.trend === "stable" && <Minus className="h-8 w-8 text-gray-400" />}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Assessments</p>
                  <p className="text-3xl font-bold">{data?.assessment_count ?? 0}</p>
                </div>
                <Award className="h-8 w-8 text-warning-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Gaps & Strengths */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-danger-600">Areas to Improve</CardTitle>
            </CardHeader>
            <CardContent>
              {data?.gaps && data.gaps.length > 0 ? (
                <div className="space-y-3">
                  {data.gaps.map((gap) => (
                    <div key={gap.kc_id} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{gap.kc_name}</span>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={gap.mastery * 100}
                          className="w-20"
                          indicatorClassName="bg-danger-400"
                        />
                        <span className="w-10 text-right text-xs font-medium text-danger-600">
                          {formatPercentage(gap.mastery)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No gaps detected!</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-accent-600">Your Strengths</CardTitle>
            </CardHeader>
            <CardContent>
              {data?.strengths && data.strengths.length > 0 ? (
                <div className="space-y-3">
                  {data.strengths.map((s) => (
                    <div key={s.kc_id} className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">{s.kc_name}</span>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={s.mastery * 100}
                          className="w-20"
                          indicatorClassName="bg-accent-400"
                        />
                        <span className="w-10 text-right text-xs font-medium text-accent-600">
                          {formatPercentage(s.mastery)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">Keep working to build mastery!</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
