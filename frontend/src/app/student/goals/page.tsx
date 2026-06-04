"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { dashboardApi, quizApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { formatPercentage } from "@/lib/utils";
import {
  Target,
  Trophy,
  Flame,
  Star,
  BookOpen,
  Lock,
  Loader2,
  Sparkles,
} from "lucide-react";

interface MasteryItem {
  kc_id: string;
  kc_name: string;
  mastery: number;
  mastery_level: string;
  attempts: number;
}

interface GoalsData {
  student_id: string;
  overall_mastery: number;
  trend: string;
  total_kcs: number;
  gaps: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  strengths: Array<{ kc_id: string; kc_name: string; mastery: number }>;
  assessment_count: number;
  recent_scores: number[];
}

export default function StudentGoalsPage() {
  const { user } = useAuthStore();
  const [data, setData] = useState<GoalsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [practicing, setPracticing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const { data: mastery } = await dashboardApi.studentMastery("mathematics");
      setData(mastery);
    } catch {
      toast.error("Failed to load goals");
    } finally {
      setLoading(false);
    }
  }

  async function startPractice(kcIds: string[]) {
    setPracticing(true);
    try {
      const response = await quizApi.dispatch({
        student_id: user?.user_id || "",
        target_kc_ids: kcIds,
        num_questions: 5,
      });
      toast.success("Practice quiz ready! Head to Quizzes tab.");
    } catch {
      toast.error("Practice mode unavailable right now");
    } finally {
      setPracticing(false);
    }
  }

  // Compute streak from recent scores
  const streak = data?.recent_scores?.length || 0;

  // Compute badges
  const badges = computeBadges(data);

  // Group KCs by mastery level
  const allKCs = [
    ...(data?.strengths || []).map((s) => ({ ...s, level: s.mastery >= 0.85 ? "advanced" : "proficient" })),
    ...(data?.gaps || []).map((g) => ({
      ...g,
      level: g.mastery >= 0.40 ? "basic" : g.mastery > 0 ? "below_basic" : "not_attempted",
    })),
  ].sort((a, b) => b.mastery - a.mastery);

  if (loading) {
    return (
      <AppShell requiredRole="student">
        <div className="space-y-6">
          <div className="h-8 w-48 animate-pulse rounded bg-gray-200" />
          <div className="h-24 animate-pulse rounded-lg bg-gray-100" />
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 animate-pulse rounded-lg bg-gray-100" />
            ))}
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">My Learning Goals</h2>
          <p className="mt-1 text-sm text-gray-500">Track your progress and earn badges</p>
        </div>

        {/* Progress Overview Card */}
        <Card className="bg-gradient-to-r from-primary-50 to-indigo-50 border-primary-200">
          <CardContent className="py-5">
            <div className="flex items-center justify-between">
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-3">
                  <Flame className="h-6 w-6 text-orange-500" />
                  <span className="text-sm font-medium text-gray-700">
                    {streak > 0 ? `${streak} assessment${streak > 1 ? "s" : ""} completed` : "Start your streak!"}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500">Overall Progress</span>
                  <div className="flex-1 max-w-64">
                    <Progress value={(data?.overall_mastery || 0) * 100} className="h-3" />
                  </div>
                  <span className="text-sm font-bold text-primary-700">
                    {formatPercentage(data?.overall_mastery || 0)}
                  </span>
                </div>
              </div>
              <div className="hidden md:flex items-center gap-2 pl-6">
                <Trophy className="h-10 w-10 text-amber-400" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{badges.length}</p>
                  <p className="text-xs text-gray-500">Badges</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Knowledge Component Cards */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Knowledge Components</h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {allKCs.map((kc, idx) => (
              <div
                key={kc.kc_id}
                className="animate-in fade-in slide-in-from-bottom-2"
                style={{ animationDelay: `${idx * 50}ms`, animationFillMode: "both" }}
              >
                <KCCard
                  kc={kc}
                  onPractice={() => startPractice([kc.kc_id])}
                  isPracticing={practicing}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Quick Practice Button */}
        {data?.gaps && data.gaps.length > 0 && (
          <Card className="border-blue-200 bg-blue-50/50">
            <CardContent className="flex items-center justify-between py-4">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Practice Your Weak Areas</p>
                  <p className="text-xs text-gray-500">
                    AI-generated quiz targeting: {data.gaps.slice(0, 2).map(g => g.kc_name).join(", ")}
                  </p>
                </div>
              </div>
              <Button
                onClick={() => startPractice(data.gaps.slice(0, 3).map(g => g.kc_id))}
                disabled={practicing}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {practicing ? <Loader2 className="h-4 w-4 animate-spin" /> : <BookOpen className="h-4 w-4 mr-1" />}
                Practice Now
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Badge Collection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Trophy className="h-5 w-5 text-amber-500" />
              Badge Collection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {ALL_BADGES.map((badge) => {
                const earned = badges.includes(badge.id);
                return (
                  <div
                    key={badge.id}
                    className={`rounded-lg border p-3 text-center transition-all ${
                      earned
                        ? "border-amber-200 bg-amber-50 shadow-sm"
                        : "border-gray-200 bg-gray-50 opacity-50"
                    }`}
                  >
                    <span className="text-2xl">{badge.emoji}</span>
                    <p className="mt-1 text-xs font-medium text-gray-900">{badge.label}</p>
                    <p className="text-[10px] text-gray-500">{badge.desc}</p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function KCCard({
  kc,
  onPractice,
  isPracticing,
}: {
  kc: { kc_id: string; kc_name: string; mastery: number; level: string };
  onPractice: () => void;
  isPracticing: boolean;
}) {
  const levelConfig: Record<string, { icon: any; color: string; bg: string; label: string }> = {
    advanced: { icon: Star, color: "text-amber-600", bg: "bg-amber-50 border-amber-200", label: "Advanced" },
    proficient: { icon: Target, color: "text-emerald-600", bg: "bg-emerald-50 border-emerald-200", label: "Proficient" },
    basic: { icon: BookOpen, color: "text-blue-600", bg: "bg-blue-50 border-blue-200", label: "Basic" },
    below_basic: { icon: Target, color: "text-orange-600", bg: "bg-orange-50 border-orange-200", label: "Developing" },
    not_attempted: { icon: Lock, color: "text-gray-400", bg: "bg-gray-50 border-gray-200", label: "Not Started" },
  };

  const config = levelConfig[kc.level] || levelConfig.basic;
  const Icon = config.icon;
  const needsPractice = kc.mastery < 0.65;

  return (
    <Card className={`${config.bg} hover:shadow-sm transition-shadow`}>
      <CardContent className="p-4 space-y-2">
        <div className="flex items-start justify-between">
          <Icon className={`h-5 w-5 ${config.color}`} />
          <Badge variant="outline" className="text-[10px]">
            {config.label}
          </Badge>
        </div>
        <p className="text-sm font-medium text-gray-900 truncate">{kc.kc_name}</p>
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-gray-500">Mastery</span>
            <span className="font-medium text-gray-700">{formatPercentage(kc.mastery)}</span>
          </div>
          <Progress value={kc.mastery * 100} className="h-2" />
        </div>
        {needsPractice && (
          <Button
            size="sm"
            variant="outline"
            className="w-full text-xs h-7 mt-1"
            onClick={onPractice}
            disabled={isPracticing}
          >
            {isPracticing ? <Loader2 className="h-3 w-3 animate-spin" /> : "Practice →"}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Badge System ────────────────────────────────────────────────────────────

const ALL_BADGES = [
  { id: "first_step", emoji: "🏅", label: "First Step", desc: "Complete first quiz" },
  { id: "streak_3", emoji: "🎖️", label: "Streak Starter", desc: "3 assessments" },
  { id: "streak_7", emoji: "🔥", label: "On Fire", desc: "7 assessments" },
  { id: "mastered_one", emoji: "⭐", label: "Knowledge Master", desc: "1 KC at Advanced" },
  { id: "gap_closer", emoji: "🎯", label: "Gap Closer", desc: "Improved a weak KC" },
  { id: "all_proficient", emoji: "💎", label: "All Proficient", desc: "All KCs ≥65%" },
  { id: "perfect_score", emoji: "🏆", label: "Perfect Score", desc: "100% on a quiz" },
  { id: "helper", emoji: "🤝", label: "Team Player", desc: "Help a classmate" },
];

function computeBadges(data: GoalsData | null): string[] {
  if (!data) return [];
  const earned: string[] = [];

  if (data.assessment_count >= 1) earned.push("first_step");
  if (data.assessment_count >= 3) earned.push("streak_3");
  if (data.assessment_count >= 7) earned.push("streak_7");
  if (data.strengths?.some((s) => s.mastery >= 0.85)) earned.push("mastered_one");
  if (data.gaps?.length === 0 && data.strengths?.length > 0) earned.push("all_proficient");
  if (data.recent_scores?.some((s) => s >= 100)) earned.push("perfect_score");

  return earned;
}
