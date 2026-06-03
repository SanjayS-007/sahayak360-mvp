"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface MasteryBarChartProps {
  data: Array<{ kc_name: string; mastery: number }>;
}

const COLORS = {
  high: "#22c55e",
  mid: "#3b82f6",
  low: "#f59e0b",
  critical: "#ef4444",
};

function getColor(mastery: number) {
  if (mastery >= 0.85) return COLORS.high;
  if (mastery >= 0.65) return COLORS.mid;
  if (mastery >= 0.4) return COLORS.low;
  return COLORS.critical;
}

export function MasteryBarChart({ data }: MasteryBarChartProps) {
  const chartData = data.map((d) => ({
    name: d.kc_name.length > 15 ? d.kc_name.slice(0, 15) + "…" : d.kc_name,
    mastery: Math.round(d.mastery * 100),
    fullName: d.kc_name,
    rawMastery: d.mastery,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
        <XAxis
          dataKey="name"
          angle={-45}
          textAnchor="end"
          height={80}
          tick={{ fontSize: 11 }}
        />
        <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
        <Tooltip
          formatter={(value: number) => [`${value}%`, "Mastery"]}
          labelFormatter={(label: string) => {
            const item = chartData.find((d) => d.name === label);
            return item?.fullName || label;
          }}
        />
        <Bar dataKey="mastery" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, idx) => (
            <Cell key={idx} fill={getColor(entry.rawMastery)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
