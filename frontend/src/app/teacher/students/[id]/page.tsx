"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { dashboardApi, alertsApi, queryApi, quizApi } from "@/lib/api";
import { formatPercentage, getRiskBadgeColor } from "@/lib/utils";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Minus,
  Target,
  AlertTriangle,
  Award,
  BarChart3,
  ShieldAlert,
  Sparkles,
  Send,
  BookOpen,
  Loader2,
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
} from "recharts";

interface StudentDetail {
  student_id: string;
  full_name: string;
  class_section: string;
  overall_mastery: number;
  risk_tier: string;
  trend: string;
  assessment_count: number;
  radar_data: Array<{ kc: string; mastery: number; full_mark: number }>;
  gaps: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  strengths: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  timeline: Array<{ date: string; score: number }>;
  kc_breakdown: Array<{ kc_id: string; kc_name: string; mastery: number; level: string }>;
}

export default function TeacherStudentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const studentId = params.id as string;
  const [data, setData] = useState<StudentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [riskData, setRiskData] = useState<any>(null);
  const [mtssData, setMtssData] = useState<any>(null);
  const [insightsData, setInsightsData] = useState<any>(null);
  const [dispatching, setDispatching] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const { data: detail } = await dashboardApi.studentDetail(studentId);
      setData(detail);
      // Load additional data in parallel (non-blocking)
      alertsApi.getStudentRisk(studentId).then(res => setRiskData(res.data)).catch(() => {});
      alertsApi.getStudentMTSS(studentId).then(res => setMtssData(res.data)).catch(() => {});
      queryApi.studentInsights(studentId).then(res => setInsightsData(res.data)).catch(() => {});
    } catch {
      toast.error("Failed to load student details");
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    if (studentId) loadData();
  }, [studentId, loadData]);


  async function handleDispatchQuiz(kcIds: string[]) {
    setDispatching(true);
    try {
      await quizApi.dispatch({ student_id: studentId, target_kc_ids: kcIds, num_questions: 5 });
      toast.success("Micro-test dispatched! Student will receive it in real-time.");
    } catch {
      toast.error("Failed to dispatch quiz");
    } finally {
      setDispatching(false);
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

  if (!data) {
    return (
      <AppShell requiredRole="teacher">
        <div className="text-center py-12 text-gray-500">Student not found</div>
      </AppShell>
    );
  }

  const trendIcon = data.trend === "improving" ? (
    <TrendingUp className="h-5 w-5 text-emerald-500" />
  ) : data.trend === "declining" ? (
    <TrendingDown className="h-5 w-5 text-red-500" />
  ) : (
    <Minus className="h-5 w-5 text-gray-400" />
  );

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/teacher/students")}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900">{data.full_name}</h2>
            <p className="text-sm text-gray-500">
              {data.student_id} â€¢ {data.class_section}
            </p>
          </div>
          <Badge className={`text-sm px-3 py-1 ${getRiskBadgeColor(data.risk_tier)}`}>
            {data.risk_tier.toUpperCase()}
          </Badge>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <Card className="border-l-4 border-l-blue-500">
            <CardContent className="pt-5 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase">Mastery</p>
                  <p className="text-2xl font-bold text-gray-900">{formatPercentage(data.overall_mastery)}</p>
                </div>
                <Target className="h-8 w-8 text-blue-500 opacity-80" />
              </div>
              <Progress value={data.overall_mastery * 100} className="mt-2 h-2" />
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-emerald-500">
            <CardContent className="pt-5 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase">Trend</p>
                  <p className="text-lg font-semibold capitalize text-gray-900">{data.trend}</p>
                </div>
                {trendIcon}
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-amber-500">
            <CardContent className="pt-5 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase">Assessments</p>
                  <p className="text-2xl font-bold text-gray-900">{data.assessment_count}</p>
                </div>
                <Award className="h-8 w-8 text-amber-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-l-red-500">
            <CardContent className="pt-5 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase">Gaps</p>
                  <p className="text-2xl font-bold text-gray-900">{data.gaps.length}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-500 opacity-80" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Radar Chart & Timeline */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Radar */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-purple-500" />
                Skill Radar
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={data.radar_data} cx="50%" cy="50%" outerRadius="75%">
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis
                      dataKey="kc"
                      tick={{ fontSize: 11, fill: "#64748b" }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 100]}
                      tick={{ fontSize: 10, fill: "#94a3b8" }}
                    />
                    <Radar
                      name="Mastery"
                      dataKey="mastery"
                      stroke="#7c3aed"
                      fill="#7c3aed"
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Progress Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-emerald-500" />
                Performance Over Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                {data.timeline.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.timeline}>
                      <defs>
                        <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#64748b" }} />
                      <Tooltip
                        contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
                        formatter={(value: number) => [`${value}%`, "Score"]}
                      />
                      <Area
                        type="monotone"
                        dataKey="score"
                        stroke="#10b981"
                        strokeWidth={2}
                        fill="url(#colorScore)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-gray-400">
                    No assessment history yet
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* KC Breakdown Table */}
        <Card>
          <CardHeader>
            <CardTitle>Knowledge Component Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.kc_breakdown.map((kc) => {
                const color =
                  kc.mastery >= 0.85 ? "bg-emerald-500" :
                  kc.mastery >= 0.65 ? "bg-blue-500" :
                  kc.mastery >= 0.40 ? "bg-amber-500" : "bg-red-500";
                const levelBadge =
                  kc.mastery >= 0.85 ? "text-emerald-700 bg-emerald-50" :
                  kc.mastery >= 0.65 ? "text-blue-700 bg-blue-50" :
                  kc.mastery >= 0.40 ? "text-amber-700 bg-amber-50" : "text-red-700 bg-red-50";
                return (
                  <div key={kc.kc_id} className="flex items-center gap-3">
                    <span className="w-40 text-sm text-gray-700 truncate">{kc.kc_name}</span>
                    <div className="flex-1 h-3 rounded-full bg-gray-100 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${color}`}
                        style={{ width: `${kc.mastery * 100}%` }}
                      />
                    </div>
                    <span className="w-12 text-right text-sm font-medium text-gray-900">
                      {formatPercentage(kc.mastery)}
                    </span>
                    <Badge className={`text-xs ${levelBadge}`}>
                      {kc.level || (kc.mastery >= 0.85 ? "mastered" : kc.mastery >= 0.65 ? "proficient" : kc.mastery >= 0.4 ? "developing" : "beginning")}
                    </Badge>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Gaps & Strengths */}
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <Card className="border-t-4 border-t-red-400">
            <CardHeader>
              <CardTitle className="text-red-600 text-base">Areas Needing Attention</CardTitle>
            </CardHeader>
            <CardContent>
              {data.gaps.length > 0 ? (
                <div className="space-y-2">
                  {data.gaps.map((g) => (
                    <div key={g.kc_id} className="flex items-center justify-between py-1">
                      <span className="text-sm text-gray-700">{g.kc_name}</span>
                      <span className="text-sm font-bold text-red-600">{formatPercentage(g.mastery)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">No critical gaps â€” great progress!</p>
              )}
            </CardContent>
          </Card>
          <Card className="border-t-4 border-t-emerald-400">
            <CardHeader>
              <CardTitle className="text-emerald-600 text-base">Strengths</CardTitle>
            </CardHeader>
            <CardContent>
              {data.strengths.length > 0 ? (
                <div className="space-y-2">
                  {data.strengths.map((s) => (
                    <div key={s.kc_id} className="flex items-center justify-between py-1">
                      <span className="text-sm text-gray-700">{s.kc_name}</span>
                      <span className="text-sm font-bold text-emerald-600">{formatPercentage(s.mastery)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-400">Building towards mastery</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* â”€â”€â”€ NEW: Risk Assessment + MTSS + AI Insights â”€â”€â”€ */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* ABC Risk Radar */}
          {riskData && (
            <Card className="border-t-4 border-t-purple-400">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <ShieldAlert className="h-5 w-5 text-purple-500" />
                  Risk Assessment (ABC Model)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart
                      data={[
                        { axis: "Academic", value: riskData.abc_scores?.academic || 0, fullMark: 100 },
                        { axis: "Behavioral", value: riskData.abc_scores?.behavioral || 0, fullMark: 100 },
                        { axis: "Cognitive", value: riskData.abc_scores?.cognitive || 0, fullMark: 100 },
                      ]}
                      cx="50%" cy="50%" outerRadius="70%"
                    >
                      <PolarGrid stroke="#e2e8f0" />
                      <PolarAngleAxis dataKey="axis" tick={{ fontSize: 12, fill: "#64748b" }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                      <Radar dataKey="value" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.25} strokeWidth={2} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500">Composite:</span>
                    <span className="text-lg font-bold text-gray-900">{riskData.composite_score}/100</span>
                  </div>
                  <Badge className={getRiskBadgeColor(riskData.risk_tier)}>
                    {riskData.risk_tier?.toUpperCase()}
                  </Badge>
                </div>
                {riskData.contributing_factors?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {riskData.contributing_factors.map((f: string) => (
                      <span key={f} className="rounded-md bg-purple-50 px-2 py-0.5 text-xs text-purple-700">
                        {f.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* AI Insights */}
          {insightsData && (
            <Card className="border-t-4 border-t-indigo-400">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sparkles className="h-5 w-5 text-indigo-500" />
                  AI Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="rounded-lg bg-indigo-50/50 p-3">
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {insightsData.trend === "declining"
                      ? `${data.full_name} shows a declining pattern. Focus areas: ${insightsData.gaps?.slice(0, 2).map((g: any) => g.kc_name).join(", ") || "general review"}. Immediate intervention recommended.`
                      : insightsData.trend === "improving"
                      ? `${data.full_name} is making good progress! Strengths in ${insightsData.strengths?.slice(0, 2).map((s: any) => s.kc_name).join(", ") || "multiple areas"}. Continue current approach.`
                      : `${data.full_name} is stable. ${insightsData.gaps?.length > 0 ? `Monitor gaps in ${insightsData.gaps[0]?.kc_name}.` : "On track with current progress."}`
                    }
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-lg bg-gray-50 p-2">
                    <p className="text-lg font-bold text-gray-900">{formatPercentage(insightsData.overall_mastery || 0)}</p>
                    <p className="text-[10px] text-gray-500">Overall</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-2">
                    <p className="text-lg font-bold text-gray-900">{insightsData.gaps?.length || 0}</p>
                    <p className="text-[10px] text-gray-500">Gaps</p>
                  </div>
                  <div className="rounded-lg bg-gray-50 p-2">
                    <p className="text-lg font-bold text-gray-900">{insightsData.assessment_count || 0}</p>
                    <p className="text-[10px] text-gray-500">Assessed</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* MTSS Intervention Plan */}
        {mtssData && mtssData.actions?.length > 0 && (
          <Card className="border-t-4 border-t-blue-400">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <BookOpen className="h-5 w-5 text-blue-500" />
                Recommended Interventions
                <Badge variant="outline" className="ml-2 text-xs">
                  {mtssData.assigned_tier?.replace("_", " ").toUpperCase()}
                </Badge>
              </CardTitle>
              <p className="text-xs text-gray-500 mt-1">{mtssData.tier_description}</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                {mtssData.actions.map((action: any, idx: number) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-gray-200 p-3 hover:border-blue-300 hover:shadow-sm transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <Badge variant="outline" className="text-[10px]">
                        Priority {action.priority}
                      </Badge>
                      <span className="text-[10px] text-gray-400">
                        {action.estimated_sessions} session{action.estimated_sessions > 1 ? "s" : ""}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-gray-900 mb-1">
                      {action.action_type.replace(/_/g, " ").replace(/\b\w/g, (l: string) => l.toUpperCase())}
                    </p>
                    <p className="text-xs text-gray-500 mb-2">{action.target_kc_name}</p>
                    {action.can_dispatch && (
                      <Button
                        size="sm"
                        className="w-full text-xs h-7 bg-blue-600 hover:bg-blue-700"
                        disabled={dispatching}
                        onClick={() => handleDispatchQuiz([action.target_kc_id])}
                      >
                        <Send className="h-3 w-3 mr-1" />
                        {dispatching ? "Sending..." : "Send Micro-Test"}
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              {mtssData.escalation_note && (
                <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3">
                  <p className="text-xs text-red-700 flex items-start gap-2">
                    <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                    {mtssData.escalation_note}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
