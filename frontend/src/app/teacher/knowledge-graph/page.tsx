"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";

interface GraphNode {
  id: string;
  label: string;
  type: "student" | "kc";
  group: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface GraphEdge {
  source: string;
  target: string;
  mastery: number;
  level: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const GROUP_COLORS: Record<string, string> = {
  student: "#6366f1",
  alg: "#f59e0b",
  geo: "#10b981",
  stat: "#3b82f6",
  trig: "#ef4444",
};

function getMasteryColor(mastery: number): string {
  if (mastery >= 0.85) return "#22c55e";
  if (mastery >= 0.65) return "#84cc16";
  if (mastery >= 0.40) return "#f59e0b";
  return "#ef4444";
}

export default function KnowledgeGraphPage() {
  const { user } = useAuthStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [stats, setStats] = useState({ students: 0, kcs: 0, edges: 0 });
  const animRef = useRef<number>(0);
  const nodesRef = useRef<GraphNode[]>([]);

  useEffect(() => {
    loadGraph();
  }, [user?.class_section]);

  async function loadGraph() {
    try {
      const { data: graphData } = await api.get("/dashboard/teacher/knowledge-graph", {
        params: { class_section: user?.class_section || "9-A" },
      });
      setData(graphData);
      setStats({
        students: graphData.nodes.filter((n: GraphNode) => n.type === "student").length,
        kcs: graphData.nodes.filter((n: GraphNode) => n.type === "kc").length,
        edges: graphData.edges.length,
      });
    } catch {
      toast.error("Failed to load knowledge graph");
    } finally {
      setLoading(false);
    }
  }

  const simulate = useCallback(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Initialize positions if needed
    if (nodesRef.current.length === 0) {
      nodesRef.current = data.nodes.map((n, i) => {
        const angle = (i / data.nodes.length) * Math.PI * 2;
        const radius = n.type === "kc" ? 120 : 250;
        return {
          ...n,
          x: width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 50,
          y: height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 50,
          vx: 0,
          vy: 0,
        };
      });
    }

    const nodes = nodesRef.current;
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));

    // Force simulation step
    const alpha = 0.3;
    const repulsion = 800;
    const attraction = 0.005;
    const centerForce = 0.01;

    // Repulsion between all nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x! - nodes[i].x!;
        const dy = nodes[j].y! - nodes[i].y!;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = repulsion / (dist * dist);
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        nodes[i].vx! -= fx;
        nodes[i].vy! -= fy;
        nodes[j].vx! += fx;
        nodes[j].vy! += fy;
      }
    }

    // Attraction along edges
    for (const edge of data.edges) {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (!source || !target) continue;
      const dx = target.x! - source.x!;
      const dy = target.y! - source.y!;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = dist * attraction;
      source.vx! += dx * force;
      source.vy! += dy * force;
      target.vx! -= dx * force;
      target.vy! -= dy * force;
    }

    // Center gravity
    for (const node of nodes) {
      node.vx! += (width / 2 - node.x!) * centerForce;
      node.vy! += (height / 2 - node.y!) * centerForce;
    }

    // Apply velocity with damping
    for (const node of nodes) {
      node.vx! *= 0.6;
      node.vy! *= 0.6;
      node.x! += node.vx! * alpha;
      node.y! += node.vy! * alpha;
      // Boundary
      node.x = Math.max(30, Math.min(width - 30, node.x!));
      node.y = Math.max(30, Math.min(height - 30, node.y!));
    }

    // Draw
    ctx.clearRect(0, 0, width, height);

    // Draw edges
    for (const edge of data.edges) {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (!source || !target) continue;

      ctx.beginPath();
      ctx.moveTo(source.x!, source.y!);
      ctx.lineTo(target.x!, target.y!);
      ctx.strokeStyle = getMasteryColor(edge.mastery);
      ctx.globalAlpha = 0.3 + edge.mastery * 0.5;
      ctx.lineWidth = 1 + edge.mastery * 2;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // Draw nodes
    for (const node of nodes) {
      const radius = node.type === "kc" ? 18 : 10;
      const color = GROUP_COLORS[node.group] || "#6b7280";

      ctx.beginPath();
      ctx.arc(node.x!, node.y!, radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 2;
      ctx.stroke();

      // Label
      ctx.font = node.type === "kc" ? "bold 10px Inter, sans-serif" : "9px Inter, sans-serif";
      ctx.fillStyle = "#1f2937";
      ctx.textAlign = "center";
      ctx.fillText(node.label, node.x!, node.y! + radius + 12);
    }

    animRef.current = requestAnimationFrame(simulate);
  }, [data]);

  useEffect(() => {
    if (data) {
      nodesRef.current = [];
      simulate();
    }
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [data, simulate]);

  // Handle canvas resize
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = 500;
      }
    };
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, []);

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Knowledge Graph</h2>
          <div className="flex gap-2">
            <Badge variant="outline">{stats.students} Students</Badge>
            <Badge variant="outline">{stats.kcs} Knowledge Components</Badge>
            <Badge variant="outline">{stats.edges} Connections</Badge>
          </div>
        </div>

        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          </div>
        ) : (
          <>
            <Card>
              <CardContent className="p-4">
                <canvas
                  ref={canvasRef}
                  className="w-full rounded-lg bg-gray-50"
                  style={{ height: 500 }}
                />
              </CardContent>
            </Card>

            {/* Legend */}
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <Card>
                <CardContent className="flex items-center gap-3 pt-4">
                  <div className="h-4 w-4 rounded-full bg-[#6366f1]" />
                  <span className="text-sm text-gray-700">Students</span>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="flex items-center gap-3 pt-4">
                  <div className="h-4 w-4 rounded-full bg-[#f59e0b]" />
                  <span className="text-sm text-gray-700">Algebra KCs</span>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="flex items-center gap-3 pt-4">
                  <div className="h-4 w-4 rounded-full bg-[#10b981]" />
                  <span className="text-sm text-gray-700">Geometry KCs</span>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="flex items-center gap-3 pt-4">
                  <div className="h-4 w-4 rounded-full bg-[#3b82f6]" />
                  <span className="text-sm text-gray-700">Statistics KCs</span>
                </CardContent>
              </Card>
            </div>

            {/* Edge color legend */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Mastery Level (Edge Color)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-8 rounded bg-[#ef4444]" />
                    <span className="text-xs text-gray-600">Beginning (&lt;40%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-8 rounded bg-[#f59e0b]" />
                    <span className="text-xs text-gray-600">Developing (40-65%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-8 rounded bg-[#84cc16]" />
                    <span className="text-xs text-gray-600">Proficient (65-85%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-8 rounded bg-[#22c55e]" />
                    <span className="text-xs text-gray-600">Mastered (85%+)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </AppShell>
  );
}
