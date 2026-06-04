"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import api from "@/lib/api";
import {
  ArrowLeft,
  Users,
  BookOpen,
  BarChart3,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Mail,
} from "lucide-react";

interface TeacherProfile {
  teacher_id: string;
  full_name: string;
  email: string;
  class_section: string;
  department_id: string;
  student_count: number;
  total_assessments: number;
  avg_class_mastery: number;
  tickets: {
    total: number;
    resolved: number;
    active: number;
  };
}

export default function TeacherDetailPage() {
  const params = useParams();
  const router = useRouter();
  const teacherId = params.id as string;
  const [profile, setProfile] = useState<TeacherProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [teacherId]);

  async function loadProfile() {
    try {
      const { data } = await api.get(`/admin/analytics/teacher/${teacherId}`);
      setProfile(data);
    } catch {
      toast.error("Failed to load teacher profile");
    } finally {
      setLoading(false);
    }
  }

  const resolutionRate = profile?.tickets.total
    ? Math.round((profile.tickets.resolved / profile.tickets.total) * 100)
    : 0;

  return (
    <AppShell requiredRole="admin">
      <div className="space-y-6">
        {/* Back button */}
        <Button variant="ghost" size="sm" onClick={() => router.push("/admin/teachers")}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Teachers
        </Button>

        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          </div>
        ) : profile ? (
          <>
            {/* Profile Header */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start gap-6">
                  <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary-100 text-primary-700 font-bold text-3xl">
                    {profile.full_name.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-gray-900">{profile.full_name}</h2>
                    <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Mail className="h-4 w-4" />
                        {profile.email}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-4 w-4" />
                        Class {profile.class_section}
                      </span>
                      <span className="flex items-center gap-1">
                        <BookOpen className="h-4 w-4" />
                        {profile.department_id?.replace("DEPT-", "")}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Students</p>
                      <p className="text-3xl font-bold">{profile.student_count}</p>
                    </div>
                    <Users className="h-8 w-8 text-blue-400" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Assessments</p>
                      <p className="text-3xl font-bold">{profile.total_assessments}</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-indigo-400" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Avg Mastery</p>
                      <p className="text-3xl font-bold">{Math.round(profile.avg_class_mastery * 100)}%</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-emerald-400" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Active Tickets</p>
                      <p className="text-3xl font-bold">{profile.tickets.active}</p>
                    </div>
                    <ShieldCheck className="h-8 w-8 text-amber-400" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Intervention Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Intervention Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Resolution Rate</span>
                    <span className="text-sm font-semibold">{resolutionRate}%</span>
                  </div>
                  <Progress value={resolutionRate} className="h-3" />

                  <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-sm text-gray-500">
                        <BarChart3 className="h-4 w-4" />
                        Total
                      </div>
                      <p className="mt-1 text-xl font-bold">{profile.tickets.total}</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-sm text-gray-500">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        Resolved
                      </div>
                      <p className="mt-1 text-xl font-bold text-green-600">{profile.tickets.resolved}</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-sm text-gray-500">
                        <Clock className="h-4 w-4 text-amber-500" />
                        Active
                      </div>
                      <p className="mt-1 text-xl font-bold text-amber-600">{profile.tickets.active}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-gray-500">Teacher not found</p>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
