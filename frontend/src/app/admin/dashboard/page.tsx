"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import Link from "next/link";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { dashboardApi, adminAnalyticsApi } from "@/lib/api";
import {
  Users,
  School,
  BarChart3,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Activity,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

interface AdminOverview {
  total_teachers: number;
  total_students: number;
  total_events: number;
  active_interventions: number;
}

export default function AdminDashboard() {
  const [data, setData] = useState<AdminOverview | null>(null);
  const [workload, setWorkload] = useState<any>(null);
  const [heatmap, setHeatmap] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const { data: overview } = await dashboardApi.adminOverview();
      setData(overview);
      adminAnalyticsApi.teacherWorkload().then(r => setWorkload(r.data)).catch(() => {});
      adminAnalyticsApi.riskHeatmap().then(r => setHeatmap(r.data)).catch(() => {});
    } catch {
      toast.error("Failed to load admin overview");
    } finally {
      setLoading(false);
    }
  }

  const atRiskCount = heatmap?.sections?.reduce((sum: number, s: any) => sum + (s.at_risk_count || 0), 0) || 0;
  const totalTickets = workload?.teachers?.reduce((sum: number, t: any) => sum + (t.open_tickets || 0), 0) || 0;

  return (
    <AppShell requiredRole="admin">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Admin Overview</h2>
          <p className="text-sm text-gray-500 mt-1">School-wide performance and operational summary</p>
        </div>

        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          </div>
        ) : (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Teachers</p>
                      <p className="text-3xl font-bold">{data?.total_teachers ?? 0}</p>
                    </div>
                    <School className="h-8 w-8 text-primary-400" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Students</p>
                      <p className="text-3xl font-bold">{data?.total_students ?? 0}</p>
                    </div>
                    <Users className="h-8 w-8 text-accent-400" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Assessments</p>
                      <p className="text-3xl font-bold">{data?.total_events ?? 0}</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-warning-400" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Active Interventions</p>
                      <p className="text-3xl font-bold">{data?.active_interventions ?? 0}</p>
                    </div>
                    <ShieldCheck className="h-8 w-8 text-danger-400" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Alerts & Quick Stats */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* At-Risk Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <AlertTriangle className="h-5 w-5 text-amber-500" />
                    At-Risk Students
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50">
                        <span className="text-2xl font-bold text-red-600">{atRiskCount}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700">students require attention</p>
                        <p className="text-xs text-gray-500">Based on mastery levels below 40%</p>
                      </div>
                    </div>
                    {heatmap?.sections && heatmap.sections.length > 0 && (
                      <div className="space-y-2 pt-2 border-t">
                        {heatmap.sections.map((s: any) => (
                          <div key={s.section} className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">{s.section}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-gray-400">{s.total_students} students</span>
                              <Badge
                                className={
                                  s.risk_percentage >= 40
                                    ? "bg-red-100 text-red-700"
                                    : s.risk_percentage >= 25
                                    ? "bg-amber-100 text-amber-700"
                                    : "bg-green-100 text-green-700"
                                }
                              >
                                {s.risk_percentage}% risk
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Teacher Workload Quick View */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Activity className="h-5 w-5 text-blue-500" />
                    Teacher Workload
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-50">
                        <span className="text-2xl font-bold text-blue-600">{totalTickets}</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-700">open tickets total</p>
                        <p className="text-xs text-gray-500">Across all teachers</p>
                      </div>
                    </div>
                    {workload?.teachers?.slice(0, 3).map((t: any) => (
                      <div key={t.teacher_id} className="flex items-center justify-between rounded-lg border p-3">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{t.name}</p>
                          <p className="text-xs text-gray-500">{t.class_section}</p>
                        </div>
                        <div className="flex gap-2">
                          <Badge variant="outline">{t.open_tickets} tickets</Badge>
                          {t.urgent_tickets > 0 && (
                            <Badge className="bg-red-100 text-red-700">{t.urgent_tickets} urgent</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* System Status & Quick Actions */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">System Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 gap-3">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span className="text-sm">PostgreSQL</span>
                      <Badge variant="success" className="ml-auto">Online</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Neo4j Knowledge Graph</span>
                      <Badge variant="success" className="ml-auto">Online</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Gemini API</span>
                      <Badge variant="success" className="ml-auto">Connected</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">MCP Pipeline</span>
                      <Badge variant="success" className="ml-auto">Active</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Link href="/admin/analytics">
                      <Button variant="outline" className="w-full justify-between">
                        View Detailed Analytics
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                    <Link href="/admin/teachers">
                      <Button variant="outline" className="w-full justify-between mt-2">
                        Manage Teachers
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
