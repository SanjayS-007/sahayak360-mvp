"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { dashboardApi } from "@/lib/api";
import { formatPercentage } from "@/lib/utils";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Target,
  Zap,
  BookOpen,
  Trophy,
  BarChart3,
} from "lucide-react";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  Cell,
} from "recharts";

interface AnalyticsData {
  student_id: string;
  full_name: string;
  overall_mastery: number;
  trend: string;
  assessment_count: number;
  radar_data: Array<{ kc: string; mastery: number; full_mark: number }>;
  domains: Array<{ domain: string; mastery: number; kc_count: number }>;
  gaps: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  strengths: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  timeline: Array<{ date: string; score: number }>;
}

const DOMAIN_COLORS: Record<string, string> = {
  Algebra: "#6366f1",
  Geometry: "#10b981",
  Statistics: "#f59e0b",
  Trigonometry: "#ef4444",
};

export default function StudentAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const { data: analytics } = await dashboardApi.studentAnalytics("mathematics");
      setData(analytics);
    } catch {
      toast.error("Failed to load analytics");
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

  if (!data) {
    return (
      <AppShell requiredRole="student">
        <div className="text-center py-12 text-gray-500">No data available yet</div>
      </AppShell>
    );
  }

  const masteryLevel = data.overall_mastery >= 0.85 ? "Expert" :
    data.overall_mastery >= 0.65 ? "Proficient" :
    data.overall_mastery >= 0.40 ? "Developing" : "Beginner";

  const masteryColor = data.overall_mastery >= 0.85 ? "text-emerald-600" :
    data.overall_mastery >= 0.65 ? "text-blue-600" :
    data.overall_mastery >= 0.40 ? "text-amber-600" : "text-red-600";

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6">
        {/* Hero Header */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-6 text-white shadow-xl">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMSkiLz48L3N2Zz4=')] opacity-50"></div>
          <div className="relative z-10 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">My Performance Analytics</h2>
              <p className="text-white/80 mt-1">Track your learning journey across all topics</p>
            </div>
            <div className="text-right">
              <p className="text-5xl font-black">{Math.round(data.overall_mastery * 100)}%</p>
              <p className="text-white/80 text-sm mt-1">{masteryLevel} Level</p>
            </div>
          </div>
          <div className="relative z-10 mt-4 grid grid-cols-3 gap-4">
            <div className="rounded-xl bg-white/10 backdrop-blur-sm p-3 text-center">
              <p className="text-2xl font-bold">{data.assessment_count}</p>
              <p className="text-xs text-white/70">Assessments</p>
            </div>
            <div className="rounded-xl bg-white/10 backdrop-blur-sm p-3 text-center">
              <p className="text-2xl font-bold capitalize">{data.trend}</p>
              <p className="text-xs text-white/70">Trend</p>
            </div>
            <div className="rounded-xl bg-white/10 backdrop-blur-sm p-3 text-center">
              <p className="text-2xl font-bold">{data.strengths.length}/{data.radar_data.length}</p>
              <p className="text-xs text-white/70">Mastered KCs</p>
            </div>
          </div>
        </div>

        {/* Radar + Timeline Row */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Skill Radar */}
          <Card className="shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <BarChart3 className="h-5 w-5 text-indigo-500" />
                Skill Radar
              </CardTitle>
              <p className="text-xs text-gray-500">Your mastery across all knowledge components</p>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={data.radar_data} cx="50%" cy="50%" outerRadius="70%">
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis
                      dataKey="kc"
                      tick={{ fontSize: 10, fill: "#64748b" }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 100]}
                      tick={{ fontSize: 9, fill: "#94a3b8" }}
                      axisLine={false}
                    />
                    <Radar
                      name="Your Mastery"
                      dataKey="mastery"
                      stroke="#6366f1"
                      fill="#6366f1"
                      fillOpacity={0.25}
                      strokeWidth={2}
                      dot={{ r: 3, fill: "#6366f1" }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Performance Timeline */}
          <Card className="shadow-md">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="h-5 w-5 text-emerald-500" />
                Score Timeline
              </CardTitle>
              <p className="text-xs text-gray-500">Your assessment scores over time</p>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                {data.timeline.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.timeline}>
                      <defs>
                        <linearGradient id="studentGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#64748b" }} />
                      <Tooltip
                        contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: 12 }}
                        formatter={(value: number) => [`${value}%`, "Score"]}
                      />
                      <Area
                        type="monotone"
                        dataKey="score"
                        stroke="#6366f1"
                        strokeWidth={2.5}
                        fill="url(#studentGrad)"
                        dot={{ r: 4, fill: "#6366f1", strokeWidth: 2, stroke: "#fff" }}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-gray-400">
                    Complete more assessments to see your progress
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Domain Mastery */}
        <Card className="shadow-md">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <BookOpen className="h-5 w-5 text-amber-500" />
              Domain Performance
            </CardTitle>
            <p className="text-xs text-gray-500">Your mastery broken down by mathematical domain</p>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {data.domains.map((d) => {
                const color = DOMAIN_COLORS[d.domain] || "#6366f1";
                const pct = d.mastery;
                return (
                  <div
                    key={d.domain}
                    className="relative overflow-hidden rounded-xl border p-4 hover:shadow-md transition-shadow"
                  >
                    <div
                      className="absolute bottom-0 left-0 right-0 opacity-10"
                      style={{ height: `${pct}%`, backgroundColor: color }}
                    />
                    <div className="relative">
                      <p className="text-sm font-medium text-gray-700">{d.domain}</p>
                      <p className="text-3xl font-black mt-1" style={{ color }}>
                        {Math.round(pct)}%
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{d.kc_count} topics</p>
                      <div className="mt-2 h-2 rounded-full bg-gray-100 overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{ width: `${pct}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Gaps & Strengths */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Gaps */}
          <Card className="shadow-md border-t-4 border-t-red-400">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base text-red-600">
                <Zap className="h-5 w-5" />
                Focus Areas
              </CardTitle>
              <p className="text-xs text-gray-500">Topics that need more practice</p>
            </CardHeader>
            <CardContent>
              {data.gaps.length > 0 ? (
                <div className="space-y-3">
                  {data.gaps.map((g) => (
                    <div key={g.kc_id} className="flex items-center gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{g.kc_name}</p>
                        <div className="mt-1 h-2 rounded-full bg-red-50 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-red-400 transition-all"
                            style={{ width: `${g.mastery * 100}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-bold text-red-600 w-12 text-right">
                        {formatPercentage(g.mastery)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center py-6 text-gray-400">
                  <Trophy className="h-10 w-10 mb-2 text-emerald-400" />
                  <p className="text-sm">No critical gaps — amazing work!</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Strengths */}
          <Card className="shadow-md border-t-4 border-t-emerald-400">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base text-emerald-600">
                <Trophy className="h-5 w-5" />
                Your Strengths
              </CardTitle>
              <p className="text-xs text-gray-500">Topics you&apos;ve mastered</p>
            </CardHeader>
            <CardContent>
              {data.strengths.length > 0 ? (
                <div className="space-y-3">
                  {data.strengths.map((s) => (
                    <div key={s.kc_id} className="flex items-center gap-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-800">{s.kc_name}</p>
                        <div className="mt-1 h-2 rounded-full bg-emerald-50 overflow-hidden">
                          <div
                            className="h-full rounded-full bg-emerald-400 transition-all"
                            style={{ width: `${s.mastery * 100}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-bold text-emerald-600 w-12 text-right">
                        {formatPercentage(s.mastery)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center py-6 text-gray-400">
                  <Target className="h-10 w-10 mb-2" />
                  <p className="text-sm">Keep practicing to build mastery!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
