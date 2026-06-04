"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { dashboardApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { formatPercentage, getRiskBadgeColor } from "@/lib/utils";
import { Users, AlertTriangle, ClipboardList, TrendingUp } from "lucide-react";
import type { ClassAnalytics } from "@/types";

export default function TeacherDashboard() {
  const { user } = useAuthStore();
  const [analytics, setAnalytics] = useState<ClassAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) loadDashboard();
  }, [user?.class_section]);

  async function loadDashboard() {
    try {
      const classSection = user?.class_section || "9-A";
      const { data } = await dashboardApi.teacherOverview(classSection);
      setAnalytics(data);
    } catch {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <AppShell requiredRole="teacher">
        <div className="flex h-64 items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard Overview</h2>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Students"
            value={analytics?.total_students ?? 0}
            icon={<Users className="h-5 w-5 text-primary-600" />}
          />
          <StatCard
            title="Class Avg Mastery"
            value={formatPercentage(analytics?.class_avg_mastery ?? 0)}
            icon={<TrendingUp className="h-5 w-5 text-accent-600" />}
          />
          <StatCard
            title="At-Risk Students"
            value={
              (analytics?.risk_distribution?.high ?? 0) +
              (analytics?.risk_distribution?.critical ?? 0)
            }
            icon={<AlertTriangle className="h-5 w-5 text-warning-500" />}
          />
          <StatCard
            title="Open Tickets"
            value={analytics?.open_tickets ?? 0}
            icon={<ClipboardList className="h-5 w-5 text-danger-500" />}
          />
        </div>

        {/* Risk Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Student Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(analytics?.risk_distribution ?? {}).map(([tier, count]) => (
                <div key={tier} className="flex items-center gap-3">
                  <Badge className={getRiskBadgeColor(tier)}>{tier}</Badge>
                  <Progress
                    value={count}
                    max={analytics?.total_students || 1}
                    className="flex-1"
                    indicatorClassName={
                      tier === "critical"
                        ? "bg-danger-500"
                        : tier === "high"
                        ? "bg-warning-500"
                        : tier === "moderate"
                        ? "bg-primary-500"
                        : "bg-accent-500"
                    }
                  />
                  <span className="w-8 text-right text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Struggling KCs */}
        <Card>
          <CardHeader>
            <CardTitle>Struggling Knowledge Components</CardTitle>
          </CardHeader>
          <CardContent>
            {analytics?.struggling_kcs && analytics.struggling_kcs.length > 0 ? (
              <div className="space-y-3">
                {analytics.struggling_kcs.map((kc) => (
                  <div key={kc.kc_id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{kc.kc_name}</p>
                      <p className="text-xs text-gray-500">{kc.student_count} students struggling</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-danger-600">
                        {formatPercentage(kc.avg_mastery)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No struggling KCs detected. Great work!</p>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function StatCard({
  title,
  value,
  icon,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
}) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        {icon}
      </div>
      <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
