"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { InfoTooltip } from "@/components/shared/info-tooltip";

interface GraphNode {
  id: string;
  label: string;
  type: "student" | "kc";
  group: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
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

const GROUP_COLORS: Record<string, { fill: string; glow: string; text: string }> = {
  student: { fill: "#818cf8", glow: "#6366f1", text: "#312e81" },
  alg: { fill: "#fbbf24", glow: "#f59e0b", text: "#78350f" },
  geo: { fill: "#34d399", glow: "#10b981", text: "#064e3b" },
  stat: { fill: "#60a5fa", glow: "#3b82f6", text: "#1e3a5f" },
  trig: { fill: "#f87171", glow: "#ef4444", text: "#7f1d1d" },
};

function getMasteryColor(mastery: number): string {
  if (mastery >= 0.85) return "#22c55e";
  if (mastery >= 0.65) return "#84cc16";
  if (mastery >= 0.40) return "#fbbf24";
  return "#f87171";
}

function getMasteryOpacity(mastery: number): number {
  return 0.15 + mastery * 0.6;
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
  const alphaRef = useRef(1.0);
  const settledRef = useRef(false);
  const mouseRef = useRef<{ x: number; y: number } | null>(null);

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

  const render = useCallback(() => {
    if (!data || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const dpr = window.devicePixelRatio || 1;

    // Initialize positions in a structured layout (KCs in center ring, students in outer ring)
    if (nodesRef.current.length === 0) {
      const kcNodes = data.nodes.filter(n => n.type === "kc");
      const studentNodes = data.nodes.filter(n => n.type === "student");

      const allNodes: GraphNode[] = [];

      // KCs in a tight inner circle
      kcNodes.forEach((n, i) => {
        const angle = (i / kcNodes.length) * Math.PI * 2 - Math.PI / 2;
        const radius = Math.min(width, height) * 0.18;
        allNodes.push({
          ...n,
          x: width / (2 * dpr) + Math.cos(angle) * radius,
          y: height / (2 * dpr) + Math.sin(angle) * radius,
          vx: 0,
          vy: 0,
          radius: 22,
        });
      });

      // Students in outer ring
      studentNodes.forEach((n, i) => {
        const angle = (i / studentNodes.length) * Math.PI * 2 - Math.PI / 2;
        const radius = Math.min(width, height) * 0.35;
        allNodes.push({
          ...n,
          x: width / (2 * dpr) + Math.cos(angle) * radius + (Math.random() - 0.5) * 20,
          y: height / (2 * dpr) + Math.sin(angle) * radius + (Math.random() - 0.5) * 20,
          vx: 0,
          vy: 0,
          radius: 12,
        });
      });

      nodesRef.current = allNodes;
      alphaRef.current = 1.0;
      settledRef.current = false;
    }

    const nodes = nodesRef.current;
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));

    // Only simulate forces if not yet settled
    if (!settledRef.current) {
      const alpha = alphaRef.current;

      // Repulsion between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const minDist = nodes[i].radius + nodes[j].radius + 30;
          if (dist < minDist * 3) {
            const force = (1200 * alpha) / (dist * dist);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            nodes[i].vx -= fx;
            nodes[i].vy -= fy;
            nodes[j].vx += fx;
            nodes[j].vy += fy;
          }
        }
      }

      // Attraction along edges (shorter rest length)
      for (const edge of data.edges) {
        const source = nodeMap.get(edge.source);
        const target = nodeMap.get(edge.target);
        if (!source || !target) continue;
        const dx = target.x - source.x;
        const dy = target.y - source.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const idealDist = 120 + (1 - edge.mastery) * 60; // Stronger mastery = closer
        const force = (dist - idealDist) * 0.003 * alpha;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        source.vx += fx;
        source.vy += fy;
        target.vx -= fx;
        target.vy -= fy;
      }

      // Center gravity (stronger for KCs)
      const cx = width / (2 * dpr);
      const cy = height / (2 * dpr);
      for (const node of nodes) {
        const strength = node.type === "kc" ? 0.02 : 0.008;
        node.vx += (cx - node.x) * strength * alpha;
        node.vy += (cy - node.y) * strength * alpha;
      }

      // Apply velocity with strong damping
      for (const node of nodes) {
        node.vx *= 0.4;
        node.vy *= 0.4;
        node.x += node.vx;
        node.y += node.vy;
        // Boundary with padding
        const pad = node.radius + 40;
        node.x = Math.max(pad, Math.min(width / dpr - pad, node.x));
        node.y = Math.max(pad, Math.min(height / dpr - pad, node.y));
      }

      // Decay alpha — simulation converges and stops
      alphaRef.current *= 0.96;
      if (alphaRef.current < 0.005) {
        settledRef.current = true;
      }
    }

    // ─── RENDER ───────────────────────────────────────────
    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, width / dpr, height / dpr);

    // Dark subtle background
    const bgGrad = ctx.createRadialGradient(
      width / (2 * dpr), height / (2 * dpr), 0,
      width / (2 * dpr), height / (2 * dpr), width / (2 * dpr)
    );
    bgGrad.addColorStop(0, "#1e1b4b08");
    bgGrad.addColorStop(1, "#f8fafc");
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width / dpr, height / dpr);

    // Determine hovered node
    const mouse = mouseRef.current;
    let hovered: GraphNode | null = null;
    if (mouse) {
      for (const node of nodes) {
        const dx = mouse.x - node.x;
        const dy = mouse.y - node.y;
        if (Math.sqrt(dx * dx + dy * dy) < node.radius + 5) {
          hovered = node;
          break;
        }
      }
    }

    // Get edges connected to hovered node
    const hoveredEdges = new Set<string>();
    const connectedNodes = new Set<string>();
    if (hovered) {
      connectedNodes.add(hovered.id);
      for (const edge of data.edges) {
        if (edge.source === hovered.id || edge.target === hovered.id) {
          hoveredEdges.add(`${edge.source}-${edge.target}`);
          connectedNodes.add(edge.source);
          connectedNodes.add(edge.target);
        }
      }
    }

    // Draw edges (curved bezier)
    for (const edge of data.edges) {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (!source || !target) continue;

      const edgeKey = `${edge.source}-${edge.target}`;
      const isHighlighted = hoveredEdges.has(edgeKey);
      const isDimmed = hovered && !isHighlighted;

      // Curved edge via quadratic bezier
      const mx = (source.x + target.x) / 2;
      const my = (source.y + target.y) / 2;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const offset = 15;
      const cpx = mx + (dy / Math.sqrt(dx * dx + dy * dy || 1)) * offset;
      const cpy = my - (dx / Math.sqrt(dx * dx + dy * dy || 1)) * offset;

      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      ctx.quadraticCurveTo(cpx, cpy, target.x, target.y);

      const color = getMasteryColor(edge.mastery);
      ctx.strokeStyle = color;
      ctx.globalAlpha = isDimmed ? 0.05 : isHighlighted ? 0.9 : getMasteryOpacity(edge.mastery);
      ctx.lineWidth = isHighlighted ? 2.5 : 1 + edge.mastery * 1.5;
      ctx.stroke();
      ctx.globalAlpha = 1;
    }

    // Draw nodes
    for (const node of nodes) {
      const colors = GROUP_COLORS[node.group] || GROUP_COLORS.student;
      const isConnected = !hovered || connectedNodes.has(node.id);
      const isHovered = hovered?.id === node.id;
      const isDimmed = hovered && !isConnected;

      ctx.globalAlpha = isDimmed ? 0.2 : 1;

      // Glow effect for KCs
      if (node.type === "kc" && !isDimmed) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + 6, 0, Math.PI * 2);
        const glowGrad = ctx.createRadialGradient(
          node.x, node.y, node.radius - 2,
          node.x, node.y, node.radius + 8
        );
        glowGrad.addColorStop(0, colors.glow + "40");
        glowGrad.addColorStop(1, colors.glow + "00");
        ctx.fillStyle = glowGrad;
        ctx.fill();
      }

      // Node body
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      const grad = ctx.createRadialGradient(
        node.x - node.radius * 0.3, node.y - node.radius * 0.3, 0,
        node.x, node.y, node.radius
      );
      grad.addColorStop(0, "#ffffff");
      grad.addColorStop(0.5, colors.fill);
      grad.addColorStop(1, colors.glow);
      ctx.fillStyle = grad;
      ctx.fill();

      // Border
      ctx.strokeStyle = isHovered ? "#1e1b4b" : "#ffffff";
      ctx.lineWidth = isHovered ? 3 : 2;
      ctx.stroke();

      // Icon inside — initial letter for students, abbreviated for KCs
      ctx.font = node.type === "kc"
        ? `bold ${node.radius * 0.55}px Inter, system-ui, sans-serif`
        : `bold ${node.radius * 0.9}px Inter, system-ui, sans-serif`;
      ctx.fillStyle = "#ffffff";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      if (node.type === "student") {
        ctx.fillText(node.label[0], node.x, node.y);
      } else {
        // Abbreviate KC name
        const abbr = node.label.split(" ").map(w => w[0]).join("").slice(0, 3);
        ctx.fillText(abbr, node.x, node.y);
      }

      // Label below node
      ctx.font = node.type === "kc"
        ? "600 10px Inter, system-ui, sans-serif"
        : "500 9px Inter, system-ui, sans-serif";
      ctx.fillStyle = isDimmed ? "#9ca3af" : "#374151";
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillText(node.label, node.x, node.y + node.radius + 6);

      ctx.globalAlpha = 1;
    }

    // Tooltip for hovered node
    if (hovered) {
      const connCount = data.edges.filter(
        e => e.source === hovered.id || e.target === hovered.id
      ).length;
      const avgMastery = data.edges
        .filter(e => e.source === hovered.id || e.target === hovered.id)
        .reduce((sum, e) => sum + e.mastery, 0) / (connCount || 1);

      const tooltipText = hovered.type === "kc"
        ? `${hovered.label} — Avg: ${Math.round(avgMastery * 100)}% · ${connCount} students`
        : `${hovered.label} — ${connCount} KCs · Avg: ${Math.round(avgMastery * 100)}%`;

      const tx = hovered.x;
      const ty = hovered.y - hovered.radius - 18;

      ctx.font = "600 11px Inter, system-ui, sans-serif";
      const metrics = ctx.measureText(tooltipText);
      const pad = 8;
      const tw = metrics.width + pad * 2;
      const th = 22;

      // Tooltip background
      ctx.fillStyle = "#1f2937ee";
      ctx.beginPath();
      const rx = tx - tw / 2;
      const ry = ty - th / 2;
      ctx.roundRect(rx, ry, tw, th, 6);
      ctx.fill();

      // Tooltip text
      ctx.fillStyle = "#ffffff";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(tooltipText, tx, ty);
    }

    ctx.restore();

    // Continue animation until settled, then one final frame on hover
    if (!settledRef.current) {
      animRef.current = requestAnimationFrame(render);
    }
  }, [data]);

  // Redraw on hover (after settled)
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    mouseRef.current = {
      x: (e.clientX - rect.left),
      y: (e.clientY - rect.top),
    };
    if (settledRef.current) {
      // Re-render for hover effect
      cancelAnimationFrame(animRef.current);
      animRef.current = requestAnimationFrame(render);
    }
  }, [render]);

  const handleMouseLeave = useCallback(() => {
    mouseRef.current = null;
    setHoveredNode(null);
    if (settledRef.current) {
      cancelAnimationFrame(animRef.current);
      animRef.current = requestAnimationFrame(render);
    }
  }, [render]);

  useEffect(() => {
    if (data) {
      nodesRef.current = [];
      settledRef.current = false;
      alphaRef.current = 1.0;
      render();
    }
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [data, render]);

  // Handle canvas resize with DPR
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const resize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        const dpr = window.devicePixelRatio || 1;
        const w = parent.clientWidth;
        const h = 560;
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = `${w}px`;
        canvas.style.height = `${h}px`;
        // Re-layout on resize
        nodesRef.current = [];
        settledRef.current = false;
        alphaRef.current = 1.0;
        if (data) render();
      }
    };
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [data, render]);

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Knowledge Graph</h2>
              <p className="text-sm text-gray-500 mt-1">Student-KC mastery relationships · Hover to explore connections</p>
            </div>
            <InfoTooltip
              title="Knowledge Graph Visualization"
              sections={[
                { heading: "Why this feature", content: "Visualizes the entire learning ecosystem as an interactive network. Each student is connected to Knowledge Components (topics) they have been assessed on. The strength and color of connections reveal mastery levels at a glance — spotting clusters, isolated students, and topic bottlenecks that tables and charts cannot show." },
                { heading: "Reading the graph", content: "Gold/Green/Blue/Red nodes are Knowledge Components (colored by domain: Algebra, Geometry, Statistics, Trigonometry). Purple nodes are students. Edge colors show mastery: RED = critical (<40%), AMBER = needs work (40-65%), LIME = good (65-85%), GREEN = mastered (85%+). Thicker, brighter edges mean stronger mastery. Nodes cluster naturally — students close to a KC have higher mastery in it." },
                { heading: "How to use effectively", content: "Hover over any node to see its connections highlighted. Look for students floating far from KC nodes (disconnected = low mastery). Look for KC nodes surrounded by red edges (class-wide struggle). Use this to identify peer tutoring opportunities — strong students near a KC can help those far from it." },
              ]}
            />
          </div>
          <div className="flex gap-2">
            <Badge variant="outline" className="bg-indigo-50 border-indigo-200 text-indigo-700">{stats.students} Students</Badge>
            <Badge variant="outline" className="bg-amber-50 border-amber-200 text-amber-700">{stats.kcs} Knowledge Components</Badge>
            <Badge variant="outline" className="bg-gray-50 border-gray-200 text-gray-600">{stats.edges} Edges</Badge>
          </div>
        </div>

        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
          </div>
        ) : (
          <>
            <Card className="overflow-hidden border-gray-200 shadow-sm">
              <CardContent className="p-0">
                <canvas
                  ref={canvasRef}
                  className="w-full cursor-crosshair"
                  style={{ height: 560, background: "linear-gradient(135deg, #fafbff 0%, #f1f5f9 100%)" }}
                  onMouseMove={handleMouseMove}
                  onMouseLeave={handleMouseLeave}
                />
              </CardContent>
            </Card>

            {/* Legends side by side */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Node legend */}
              <Card>
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-sm font-semibold text-gray-700">Node Types</CardTitle>
                </CardHeader>
                <CardContent className="pb-4">
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { color: "#818cf8", label: "Students", shape: "small" },
                      { color: "#fbbf24", label: "Algebra" },
                      { color: "#34d399", label: "Geometry" },
                      { color: "#60a5fa", label: "Statistics" },
                      { color: "#f87171", label: "Trigonometry" },
                    ].map((item) => (
                      <div key={item.label} className="flex items-center gap-2">
                        <div
                          className="rounded-full shadow-sm border border-white"
                          style={{
                            width: item.shape === "small" ? 14 : 18,
                            height: item.shape === "small" ? 14 : 18,
                            background: `radial-gradient(circle at 30% 30%, #fff, ${item.color})`,
                          }}
                        />
                        <span className="text-xs text-gray-600 font-medium">{item.label}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Edge color legend */}
              <Card>
                <CardHeader className="pb-2 pt-4">
                  <CardTitle className="text-sm font-semibold text-gray-700">Mastery Level (Edge Color)</CardTitle>
                </CardHeader>
                <CardContent className="pb-4">
                  <div className="space-y-2">
                    {[
                      { color: "#f87171", label: "Beginning", range: "< 40%" },
                      { color: "#fbbf24", label: "Developing", range: "40–65%" },
                      { color: "#84cc16", label: "Proficient", range: "65–85%" },
                      { color: "#22c55e", label: "Mastered", range: "85%+" },
                    ].map((item) => (
                      <div key={item.label} className="flex items-center gap-3">
                        <div className="h-2 w-10 rounded-full" style={{ background: item.color, opacity: 0.8 }} />
                        <span className="text-xs text-gray-600">
                          <span className="font-medium">{item.label}</span> ({item.range})
                        </span>
                      </div>
                    ))}
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
