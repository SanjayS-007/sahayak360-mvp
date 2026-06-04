"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { gamificationApi } from "@/lib/api";
import {
  Trophy,
  Flame,
  Zap,
  Star,
  Medal,
  Crown,
} from "lucide-react";

interface GamProfile {
  xp: number;
  level: number;
  streak_days: number;
  longest_streak: number;
  badges: Array<{ id: string; name: string; earned_at: string }>;
  total_practices: number;
  total_correct: number;
  total_questions: number;
  accuracy: number;
  next_level_xp: number;
  level_progress: number;
  all_badges: Array<{ id: string; name: string; desc: string; icon: string; earned: boolean }>;
}

interface LeaderEntry {
  rank: number;
  name: string;
  user_id: string;
  xp: number;
  level: number;
  streak: number;
  is_me: boolean;
}

export default function LeaderboardPage() {
  const [profile, setProfile] = useState<GamProfile | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderEntry[]>([]);
  const [myRank, setMyRank] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [profRes, lbRes] = await Promise.all([
        gamificationApi.profile(),
        gamificationApi.leaderboard(),
      ]);
      setProfile(profRes.data);
      setLeaderboard(lbRes.data.leaderboard);
      setMyRank(lbRes.data.my_rank);
    } catch {
      toast.error("Failed to load gamification data");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <AppShell requiredRole="student">
        <div className="space-y-4">
          <div className="h-8 w-48 animate-pulse rounded bg-gray-200" />
          <div className="h-40 animate-pulse rounded-lg bg-gray-100" />
          <div className="h-60 animate-pulse rounded-lg bg-gray-100" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6 max-w-3xl mx-auto">
        {/* Header Stats */}
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <Card className="bg-gradient-to-br from-indigo-50 to-purple-50">
            <CardContent className="pt-4 text-center">
              <Zap className="mx-auto h-6 w-6 text-indigo-500" />
              <p className="mt-1 text-2xl font-bold text-indigo-700">{profile?.xp || 0}</p>
              <p className="text-xs text-gray-500">Total XP</p>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-amber-50 to-orange-50">
            <CardContent className="pt-4 text-center">
              <Star className="mx-auto h-6 w-6 text-amber-500" />
              <p className="mt-1 text-2xl font-bold text-amber-700">Lv.{profile?.level || 1}</p>
              <p className="text-xs text-gray-500">Level</p>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-red-50 to-pink-50">
            <CardContent className="pt-4 text-center">
              <Flame className="mx-auto h-6 w-6 text-red-500" />
              <p className="mt-1 text-2xl font-bold text-red-700">{profile?.streak_days || 0}</p>
              <p className="text-xs text-gray-500">Day Streak</p>
            </CardContent>
          </Card>
          <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
            <CardContent className="pt-4 text-center">
              <Trophy className="mx-auto h-6 w-6 text-green-500" />
              <p className="mt-1 text-2xl font-bold text-green-700">{profile?.accuracy || 0}%</p>
              <p className="text-xs text-gray-500">Accuracy</p>
            </CardContent>
          </Card>
        </div>

        {/* Level Progress */}
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Level {profile?.level}</span>
              <span className="text-gray-500">{profile?.xp} / {profile?.next_level_xp} XP</span>
            </div>
            <Progress value={profile?.level_progress || 0} className="mt-2 h-3" />
          </CardContent>
        </Card>

        {/* Badges */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Medal className="h-5 w-5 text-purple-500" />
              Badges ({profile?.badges.length || 0}/{profile?.all_badges.length || 0})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-5">
              {profile?.all_badges.map((badge) => (
                <div
                  key={badge.id}
                  className={`rounded-lg border p-3 text-center transition-all ${
                    badge.earned
                      ? "border-purple-200 bg-purple-50"
                      : "border-gray-100 bg-gray-50 opacity-40"
                  }`}
                >
                  <span className="text-2xl">{badge.icon}</span>
                  <p className="mt-1 text-xs font-medium">{badge.name}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Leaderboard */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Crown className="h-5 w-5 text-amber-500" />
              Class Leaderboard
              {myRank > 0 && (
                <Badge variant="outline" className="ml-auto">Your Rank: #{myRank}</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {leaderboard.map((entry) => (
                <div
                  key={entry.user_id}
                  className={`flex items-center gap-3 rounded-lg border p-3 ${
                    entry.is_me ? "border-indigo-200 bg-indigo-50" : ""
                  }`}
                >
                  <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold ${
                    entry.rank === 1 ? "bg-amber-100 text-amber-700" :
                    entry.rank === 2 ? "bg-gray-100 text-gray-700" :
                    entry.rank === 3 ? "bg-orange-100 text-orange-700" :
                    "bg-gray-50 text-gray-500"
                  }`}>
                    {entry.rank <= 3 ? ["🥇", "🥈", "🥉"][entry.rank - 1] : `#${entry.rank}`}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">
                      {entry.name} {entry.is_me && <span className="text-indigo-500">(You)</span>}
                    </p>
                    <p className="text-xs text-gray-500">Lv.{entry.level} • {entry.streak}🔥</p>
                  </div>
                  <span className="text-sm font-bold text-indigo-600">{entry.xp} XP</span>
                </div>
              ))}
              {leaderboard.length === 0 && (
                <p className="text-center text-sm text-gray-400 py-4">
                  Practice to get on the leaderboard!
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
