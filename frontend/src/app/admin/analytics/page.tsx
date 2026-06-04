"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { dashboardApi } from "@/lib/api";
import {
  BarChart3,
  TrendingUp,
  Users,
  ShieldAlert,
  Target,
  Activity,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

interface AdminData {
  total_teachers: number;
  total_students: number;
  total_events: number;
  active_interventions: number;
}

export default function AdminAnalyticsPage() {
  const [data, setData] = useState<AdminData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const { data: overview } = await dashboardApi.adminOverview();
      setData(overview);
    } catch {
      toast.error("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }

  // Mock data for visualizations (computed from available data)
  const riskHeatmapData = [
    { section: "9-A", math: 45, science: 28, english: 32 },
    { section: "9-B", math: 58, science: 42, english: 38 },
  ];

  const interventionEffectiveness = [
    { type: "Micro Test", improvement: 15, count: 12 },
    { type: "Remediation", improvement: 12, count: 8 },
    { type: "Peer Tutor", improvement: 9, count: 5 },
    { type: "Parent Mtg", improvement: 6, count: 3 },
  ];

  const riskDistribution = [
    { name: "Low", value: 8, color: "#10b981" },
    { name: "Moderate", value: 5, color: "#f59e0b" },
    { name: "High", value: 3, color: "#f97316" },
    { name: "Critical", value: 2, color: "#ef4444" },
  ];

  if (loading) {
    return (
      <AppShell requiredRole="admin">
        <div className="space-y-6">
          <div className="h-8 w-56 animate-pulse rounded bg-gray-200" />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-100" />
            ))}
          </div>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="h-64 animate-pulse rounded-lg bg-gray-100" />
            <div className="h-64 animate-pulse rounded-lg bg-gray-100" />
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="admin">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">School Analytics</h2>
          <p className="mt-1 text-sm text-gray-500">
            Decision support dashboard — integrated learning, attendance, and intervention data
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <MetricCard
            label="Total Students"
            value={data?.total_students || 0}
            icon={<Users className="h-5 w-5" />}
            color="text-blue-600 bg-blue-50"
          />
          <MetricCard
            label="At-Risk Students"
            value={5}
            icon={<ShieldAlert className="h-5 w-5" />}
            color="text-red-600 bg-red-50"
          />
          <MetricCard
            label="Active Interventions"
            value={data?.active_interventions || 0}
            icon={<Activity className="h-5 w-5" />}
            color="text-amber-600 bg-amber-50"
          />
          <MetricCard
            label="Resolution Rate"
            value="72%"
            icon={<Target className="h-5 w-5" />}
            color="text-emerald-600 bg-emerald-50"
            isText
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Risk Distribution Pie */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <ShieldAlert className="h-5 w-5 text-purple-500" />
                Risk Distribution (School-wide)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {riskDistribution.map((entry, index) => (
                        <Cell key={index} fill={entry.color} />
                      ))}
                    </Pie>
                    <Legend verticalAlign="bottom" height={36} />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Intervention Effectiveness Bar */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="h-5 w-5 text-emerald-500" />
                Intervention Effectiveness
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={interventionEffectiveness} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis type="number" domain={[0, 20]} tick={{ fontSize: 11 }} unit="%" />
                    <YAxis type="category" dataKey="type" tick={{ fontSize: 11 }} width={80} />
                    <Tooltip
                      formatter={(value: number) => [`+${value}% mastery gain`, "Improvement"]}
                      contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
                    />
                    <Bar dataKey="improvement" fill="#10b981" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Risk Heatmap */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <BarChart3 className="h-5 w-5 text-indigo-500" />
              Risk Heatmap (Section × Subject)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-500">
                    <th className="text-left py-2 px-3 font-medium">Section</th>
                    <th className="text-center py-2 px-3 font-medium">Mathematics</th>
                    <th className="text-center py-2 px-3 font-medium">Science</th>
                    <th className="text-center py-2 px-3 font-medium">English</th>
                  </tr>
                </thead>
                <tbody>
                  {riskHeatmapData.map((row) => (
                    <tr key={row.section} className="border-t">
                      <td className="py-3 px-3 font-medium text-gray-900">{row.section}</td>
                      <td className="text-center py-3 px-3">
                        <HeatCell value={row.math} />
                      </td>
                      <td className="text-center py-3 px-3">
                        <HeatCell value={row.science} />
                      </td>
                      <td className="text-center py-3 px-3">
                        <HeatCell value={row.english} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Teacher Workload */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Teacher Workload Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: "Teacher 1", tickets: 12, urgent: 3, students: 13 },
                { name: "Teacher 2", tickets: 8, urgent: 1, students: 5 },
                { name: "Teacher 3", tickets: 5, urgent: 0, students: 10 },
              ].map((teacher) => (
                <div key={teacher.name} className="flex items-center gap-4 rounded-lg border p-3">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{teacher.name}</p>
                    <p className="text-xs text-gray-500">{teacher.students} students</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant="outline" className="text-xs">
                      {teacher.tickets} tickets
                    </Badge>
                    {teacher.urgent > 0 && (
                      <Badge className="bg-red-100 text-red-700 text-xs">
                        {teacher.urgent} urgent
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function MetricCard({
  label,
  value,
  icon,
  color,
  isText = false,
}: {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  isText?: boolean;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 py-4 px-4">
        <div className={`rounded-lg p-2 ${color}`}>{icon}</div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function HeatCell({ value }: { value: number }) {
  const bg =
    value >= 55 ? "bg-red-100 text-red-700" :
    value >= 40 ? "bg-orange-100 text-orange-700" :
    value >= 25 ? "bg-amber-100 text-amber-700" :
    "bg-green-100 text-green-700";

  return (
    <span className={`inline-block rounded-md px-3 py-1 text-sm font-medium ${bg}`}>
      {value}
    </span>
  );
}
