"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface RiskPieChartProps {
  distribution: {
    low: number;
    moderate: number;
    high: number;
    critical: number;
  };
}

const RISK_COLORS = {
  low: "#22c55e",
  moderate: "#3b82f6",
  high: "#f59e0b",
  critical: "#ef4444",
};

export function RiskPieChart({ distribution }: RiskPieChartProps) {
  const data = Object.entries(distribution)
    .filter(([, value]) => value > 0)
    .map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      key: name,
    }));

  if (data.length === 0) {
    return (
      <div className="flex h-[250px] items-center justify-center text-sm text-gray-400">
        No student data available
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          dataKey="value"
        >
          {data.map((entry) => (
            <Cell
              key={entry.key}
              fill={RISK_COLORS[entry.key as keyof typeof RISK_COLORS]}
            />
          ))}
        </Pie>
        <Tooltip formatter={(value: number) => [`${value} students`, ""]} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
