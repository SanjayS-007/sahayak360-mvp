"use client";

import { useEffect, useState, useCallback } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { dashboardApi, queryApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { formatPercentage, getRiskBadgeColor } from "@/lib/utils";
import { Users, AlertTriangle, ClipboardList, TrendingUp, Sparkles, Brain, Target, TrendingDown, GitBranch, Layers } from "lucide-react";
import { InfoTooltip } from "@/components/shared/info-tooltip";
import type { ClassAnalytics } from "@/types";

export default function TeacherDashboard() {
  const { user } = useAuthStore();
  const [analytics, setAnalytics] = useState<ClassAnalytics | null>(null);
  const [patterns, setPatterns] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadDashboard = useCallback(async () => {
    try {
      const classSection = user?.class_section || "9-A";
      const { data } = await dashboardApi.teacherOverview(classSection);
      setAnalytics(data);
      // Load AI patterns (non-blocking) — use computed endpoint
      queryApi.classPatternsComputed(classSection).then(r => setPatterns(r.data)).catch(() => {});
    } catch {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  }, [user?.class_section]);

  useEffect(() => {
    if (user) loadDashboard();
  }, [user, loadDashboard]);

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

        {/* AI Class Patterns */}
        <Card className="border-t-4 border-t-indigo-400">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-indigo-500" />
                AI-Detected Class Patterns
              </CardTitle>
              <InfoTooltip
                title="AI-Detected Class Patterns"
                sections={[
                  { heading: "Why this feature", content: "Automatically analyzes mastery data across all students to surface hidden patterns — struggling topics, correlated weaknesses, declining performance, and achievement gaps — that would take hours to identify manually." },
                  { heading: "What you get", content: "Actionable insights with severity levels. Each pattern tells you how many students are affected and whether it needs immediate attention (high severity) or monitoring (medium). Patterns include: class-wide gaps, cross-topic correlations, declining trends, and prerequisite breakdowns." },
                  { heading: "How to use effectively", content: "Check patterns weekly after new assessments. High-severity patterns need immediate intervention (consider group remediation or targeted quizzes). Medium-severity patterns inform your lesson planning for the coming week. Use correlation patterns to address root causes rather than symptoms." },
                ]}
              />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {patterns?.summary && (
              <div className="rounded-lg bg-indigo-50/50 p-3">
                <p className="text-sm text-gray-700 leading-relaxed">{patterns.summary}</p>
              </div>
            )}
            {patterns?.patterns?.length > 0 ? (
              <div className="space-y-2">
                {patterns.patterns.slice(0, 6).map((p: any, idx: number) => {
                  const PatternIcon = p.pattern_type === "decline" ? TrendingDown :
                    p.pattern_type === "correlation" ? GitBranch :
                    p.pattern_type === "prerequisite" ? Layers :
                    p.pattern_type === "cluster" ? Users : Target;
                  return (
                    <div key={idx} className="flex items-start gap-3 rounded-lg border border-gray-100 p-3 hover:bg-gray-50 transition-colors">
                      <PatternIcon className="h-4 w-4 text-indigo-400 mt-0.5 shrink-0" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{p.insight || p.pattern || p.description}</p>
                        {p.affected_students && (
                          <p className="text-xs text-gray-500 mt-0.5">
                            Affects {p.affected_students} student{p.affected_students > 1 ? "s" : ""}
                          </p>
                        )}
                      </div>
                      {p.severity && (
                        <Badge className={
                          p.severity === "high" ? "bg-red-100 text-red-700" :
                          p.severity === "medium" ? "bg-amber-100 text-amber-700" :
                          "bg-green-100 text-green-700"
                        }>
                          {p.severity}
                        </Badge>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-sm text-gray-400">Analyzing data... Patterns will appear once enough assessments are recorded.</p>
            )}
            {patterns?.analyzed_at && (
              <p className="text-xs text-gray-400 text-right">
                Last analyzed: {new Date(patterns.analyzed_at).toLocaleString()}
              </p>
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
