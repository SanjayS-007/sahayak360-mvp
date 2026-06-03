"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { dashboardApi } from "@/lib/api";
import { Users, School, BarChart3, ShieldCheck } from "lucide-react";

interface AdminOverview {
  total_teachers: number;
  total_students: number;
  total_events: number;
  active_interventions: number;
}

export default function AdminDashboard() {
  const [data, setData] = useState<AdminOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const { data: overview } = await dashboardApi.adminOverview();
      setData(overview);
    } catch {
      toast.error("Failed to load admin overview");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell requiredRole="admin">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Admin Overview</h2>

        {loading ? (
          <div className="flex h-32 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          </div>
        ) : (
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
        )}

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full bg-accent-500" />
                <span className="text-sm">PostgreSQL</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full bg-accent-500" />
                <span className="text-sm">Neo4j</span>
                <Badge variant="success">Online</Badge>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full bg-accent-500" />
                <span className="text-sm">Gemini API</span>
                <Badge variant="success">Connected</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
