"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { alertsApi, quizApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import {
  AlertTriangle,
  TrendingDown,
  Target,
  Send,
  Eye,
  ShieldAlert,
  Activity,
  Users,
} from "lucide-react";
import { InfoTooltip } from "@/components/shared/info-tooltip";

interface AlertItem {
  student_id: string;
  student_name: string;
  alert_type: string;
  risk_tier: string;
  composite_score: number;
  abc_scores: { academic: number; behavioral: number; cognitive: number };
  contributing_factors: string[];
  recommended_action: string;
  trend: string;
  gaps_count: number;
}

interface AlertsData {
  alerts: AlertItem[];
  total_critical: number;
  total_high: number;
  total_moderate: number;
  class_section: string;
}

export default function TeacherAlertsPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [data, setData] = useState<AlertsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>("all");
  const [dispatching, setDispatching] = useState<string>("");

  const loadAlerts = useCallback(async () => {
    try {
      const classSection = user?.class_section || "9-A";
      const { data: alerts } = await alertsApi.getAlerts(classSection);
      setData(alerts);
    } catch {
      toast.error("Failed to load alerts");
    } finally {
      setLoading(false);
    }
  }, [user?.class_section]);

  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  async function handleQuickDispatch(studentId: string, studentName: string) {
    setDispatching(studentId);
    try {
      await quizApi.dispatch({
        student_id: studentId,
        target_kc_ids: ["KC-001", "KC-002"],
        num_questions: 5,
      });
      toast.success(`Micro-test sent to ${studentName}!`);
    } catch {
      toast.error("Failed to dispatch quiz");
    } finally {
      setDispatching("");
    }
  }

  const filteredAlerts = data?.alerts.filter((a) => {
    if (filter === "all") return true;
    if (filter === "critical") return a.risk_tier === "critical";
    if (filter === "high") return a.risk_tier === "high";
    if (filter === "declining") return a.trend === "declining";
    return true;
  }) || [];

  if (loading) {
    return (
      <AppShell requiredRole="teacher">
        <div className="space-y-6">
          <div className="h-8 w-64 animate-pulse rounded bg-gray-200" />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-100" />
            ))}
          </div>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-36 animate-pulse rounded-lg bg-gray-100" />
            ))}
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Alerts & Early Warnings</h2>
              <p className="mt-1 text-sm text-gray-500">
                Students requiring immediate attention based on multi-dimensional risk analysis
              </p>
            </div>
            <InfoTooltip
              title="Risk Scoring & Early Warnings"
              sections={[
                { heading: "Why this feature", content: "Identifies struggling students BEFORE they fail — using the ABC risk model that combines Academic performance (mastery scores, gap count), Behavioral signals (attendance, engagement), and Cognitive indicators (learning velocity, knowledge gaps). Students are flagged early so you can intervene proactively." },
                { heading: "Understanding risk scores", content: "Each student gets a composite score (0-100): Critical (55+) needs immediate intervention, High (40-54) needs targeted support, Moderate (25-39) needs monitoring, Low (<25) is on track. The ABC breakdown shows which dimension drives the risk — academic struggles vs. behavioral vs. cognitive overload." },
                { heading: "How to use effectively", content: "Sort by Critical first. Click 'View Details' to see the full risk breakdown and MTSS plan. Use 'Send Quiz' to dispatch a diagnostic micro-test that pinpoints exact gaps. Contributing factors tell you WHY a student is at risk — address root causes, not just symptoms." },
              ]}
            />
          </div>
          <Badge variant="outline" className="text-sm px-3 py-1">
            {data?.class_section || "9-A"}
          </Badge>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <StatCard
            label="Critical"
            value={data?.total_critical || 0}
            icon={<ShieldAlert className="h-5 w-5" />}
            color="text-red-600 bg-red-50 border-red-200"
          />
          <StatCard
            label="High Risk"
            value={data?.total_high || 0}
            icon={<AlertTriangle className="h-5 w-5" />}
            color="text-orange-600 bg-orange-50 border-orange-200"
          />
          <StatCard
            label="Moderate"
            value={data?.total_moderate || 0}
            icon={<Activity className="h-5 w-5" />}
            color="text-amber-600 bg-amber-50 border-amber-200"
          />
          <StatCard
            label="Total At-Risk"
            value={data?.alerts.length || 0}
            icon={<Users className="h-5 w-5" />}
            color="text-gray-600 bg-gray-50 border-gray-200"
          />
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2">
          {[
            { key: "all", label: "All" },
            { key: "critical", label: "Critical" },
            { key: "high", label: "High Risk" },
            { key: "declining", label: "Declining Trend" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition-all ${
                filter === tab.key
                  ? "bg-gray-900 text-white shadow-sm"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Alert Cards */}
        <div className="space-y-4">
          {filteredAlerts.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Target className="h-12 w-12 text-gray-300 mb-3" />
                <p className="text-gray-500 text-sm">No alerts matching this filter</p>
              </CardContent>
            </Card>
          ) : (
            filteredAlerts.map((alert, index) => (
              <div
                key={alert.student_id}
                className="animate-in fade-in slide-in-from-bottom-2"
                style={{ animationDelay: `${index * 60}ms`, animationFillMode: "both" }}
              >
                <AlertCard
                  alert={alert}
                  onViewDetails={() => router.push(`/teacher/students/${alert.student_id}`)}
                  onDispatchQuiz={() => handleQuickDispatch(alert.student_id, alert.student_name)}
                  isDispatching={dispatching === alert.student_id}
                />
              </div>
            ))
          )}
        </div>
      </div>
    </AppShell>
  );
}

function StatCard({
  label,
  value,
  icon,
  color,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}) {
  return (
    <Card className={`border ${color.split(" ").slice(1).join(" ")}`}>
      <CardContent className="flex items-center gap-3 py-4 px-4">
        <div className={`rounded-lg p-2 ${color.split(" ").slice(1, 3).join(" ")}`}>
          <span className={color.split(" ")[0]}>{icon}</span>
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function AlertCard({
  alert,
  onViewDetails,
  onDispatchQuiz,
  isDispatching,
}: {
  alert: AlertItem;
  onViewDetails: () => void;
  onDispatchQuiz: () => void;
  isDispatching: boolean;
}) {
  const tierConfig = {
    critical: { border: "border-l-red-500", badge: "bg-red-100 text-red-700", label: "CRITICAL" },
    high: { border: "border-l-orange-500", badge: "bg-orange-100 text-orange-700", label: "HIGH" },
    moderate: { border: "border-l-amber-500", badge: "bg-amber-100 text-amber-700", label: "MODERATE" },
    low: { border: "border-l-green-500", badge: "bg-green-100 text-green-700", label: "LOW" },
  };

  const config = tierConfig[alert.risk_tier as keyof typeof tierConfig] || tierConfig.moderate;

  const factorLabels: Record<string, string> = {
    academic_performance_low: "Academic Low",
    multiple_knowledge_gaps: "Multiple Gaps",
    declining_trend: "Declining Trend",
    critical_gap_present: "Critical Gap",
    behavioral_concerns: "Behavioral",
    deep_prerequisite_gaps: "Deep Prereq Gaps",
  };

  return (
    <Card className={`border-l-4 ${config.border} hover:shadow-md transition-shadow ${
      alert.risk_tier === "critical" ? "ring-1 ring-red-100" : ""
    }`}>
      <CardContent className="py-4 px-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          {/* Left: Student info */}
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-3">
              <h3 className="font-semibold text-gray-900">{alert.student_name}</h3>
              <Badge className={`text-xs ${config.badge}`}>{config.label}</Badge>
              {alert.trend === "declining" && (
                <Badge variant="outline" className="text-xs text-red-600 border-red-200">
                  <TrendingDown className="h-3 w-3 mr-1" />
                  Declining
                </Badge>
              )}
            </div>

            {/* Composite score bar */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500 w-20">Risk Score</span>
              <div className="flex-1 max-w-48">
                <Progress value={alert.composite_score} className="h-2" />
              </div>
              <span className="text-sm font-medium text-gray-700">{alert.composite_score}/100</span>
            </div>

            {/* Contributing factors */}
            <div className="flex flex-wrap gap-1.5">
              {alert.contributing_factors.map((factor) => (
                <span
                  key={factor}
                  className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                >
                  {factorLabels[factor] || factor}
                </span>
              ))}
            </div>

            {/* Recommendation */}
            <p className="text-xs text-gray-500 italic">{alert.recommended_action}</p>
          </div>

          {/* Right: Actions */}
          <div className="flex gap-2 md:flex-col">
            <Button
              size="sm"
              variant="outline"
              onClick={onViewDetails}
              className="text-xs"
            >
              <Eye className="h-3.5 w-3.5 mr-1" />
              Details
            </Button>
            <Button
              size="sm"
              onClick={onDispatchQuiz}
              disabled={isDispatching}
              className="text-xs bg-primary-600 hover:bg-primary-700 text-white"
            >
              <Send className="h-3.5 w-3.5 mr-1" />
              {isDispatching ? "Sending..." : "Send Quiz"}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
