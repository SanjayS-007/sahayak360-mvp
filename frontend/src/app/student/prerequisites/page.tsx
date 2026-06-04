"use client";

import { useState } from "react";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GitBranch, ArrowRight, CheckCircle2, Circle } from "lucide-react";

interface KCNode {
  id: string;
  name: string;
  prerequisites: string[];
  next: string[];
  domain: string;
}

// Prerequisites graph data
const KC_GRAPH: KCNode[] = [
  { id: "ALG-LINEAR-EQ", name: "Linear Equations", prerequisites: [], next: ["ALG-QUAD-EQ", "GEO-COORDINATE"], domain: "Algebra" },
  { id: "ALG-QUAD-EQ", name: "Quadratic Equations", prerequisites: ["ALG-LINEAR-EQ", "ALG-FACTORING"], next: ["ALG-POLYNOMIALS", "ALG-FUNCTIONS"], domain: "Algebra" },
  { id: "ALG-FACTORING", name: "Factoring", prerequisites: ["ALG-LINEAR-EQ"], next: ["ALG-QUAD-EQ"], domain: "Algebra" },
  { id: "ALG-POLYNOMIALS", name: "Polynomials", prerequisites: ["ALG-QUAD-EQ"], next: ["ALG-FUNCTIONS"], domain: "Algebra" },
  { id: "ALG-FUNCTIONS", name: "Functions", prerequisites: ["ALG-POLYNOMIALS", "ALG-QUAD-EQ"], next: [], domain: "Algebra" },
  { id: "GEO-TRIANGLES", name: "Triangles", prerequisites: [], next: ["GEO-CIRCLES", "TRIG-BASIC"], domain: "Geometry" },
  { id: "GEO-CIRCLES", name: "Circles", prerequisites: ["GEO-TRIANGLES"], next: ["GEO-COORDINATE"], domain: "Geometry" },
  { id: "GEO-COORDINATE", name: "Coordinate Geometry", prerequisites: ["ALG-LINEAR-EQ", "GEO-CIRCLES"], next: [], domain: "Geometry" },
  { id: "TRIG-BASIC", name: "Basic Trigonometry", prerequisites: ["GEO-TRIANGLES"], next: ["TRIG-IDENTITIES"], domain: "Trigonometry" },
  { id: "TRIG-IDENTITIES", name: "Trig Identities", prerequisites: ["TRIG-BASIC"], next: [], domain: "Trigonometry" },
  { id: "STAT-MEASURES", name: "Statistical Measures", prerequisites: [], next: ["STAT-PROBABILITY"], domain: "Statistics" },
  { id: "STAT-PROBABILITY", name: "Probability", prerequisites: ["STAT-MEASURES"], next: [], domain: "Statistics" },
];

const DOMAIN_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  Algebra: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
  Geometry: { bg: "bg-green-50", text: "text-green-700", border: "border-green-200" },
  Trigonometry: { bg: "bg-orange-50", text: "text-orange-700", border: "border-orange-200" },
  Statistics: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
};

export default function PrerequisitesMapPage() {
  const [selectedNode, setSelectedNode] = useState<KCNode | null>(null);

  const domains = [...new Set(KC_GRAPH.map((n) => n.domain))];

  function getNodeById(id: string) {
    return KC_GRAPH.find((n) => n.id === id);
  }

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="flex items-center gap-3">
          <GitBranch className="h-7 w-7 text-emerald-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Prerequisites Map</h2>
            <p className="text-sm text-gray-500">See how topics connect and build on each other</p>
          </div>
        </div>

        {/* Domain legend */}
        <div className="flex flex-wrap gap-2">
          {domains.map((d) => (
            <Badge key={d} variant="outline" className={`${DOMAIN_COLORS[d]?.bg} ${DOMAIN_COLORS[d]?.text} ${DOMAIN_COLORS[d]?.border}`}>
              {d}
            </Badge>
          ))}
        </div>

        {/* Graph visualization */}
        <div className="grid gap-4 md:grid-cols-2">
          {domains.map((domain) => (
            <Card key={domain} className={DOMAIN_COLORS[domain]?.border}>
              <CardHeader className="pb-2">
                <CardTitle className={`text-sm font-semibold ${DOMAIN_COLORS[domain]?.text}`}>
                  {domain}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {KC_GRAPH.filter((n) => n.domain === domain).map((node) => (
                    <button
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className={`w-full rounded-lg border p-3 text-left transition-all hover:shadow-sm ${
                        selectedNode?.id === node.id
                          ? `${DOMAIN_COLORS[domain]?.border} ${DOMAIN_COLORS[domain]?.bg} ring-2 ring-offset-1`
                          : "border-gray-100 hover:border-gray-200"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        {node.prerequisites.length === 0 ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                        ) : (
                          <Circle className="h-4 w-4 text-gray-300 shrink-0" />
                        )}
                        <span className="text-sm font-medium">{node.name}</span>
                      </div>
                      {node.prerequisites.length > 0 && (
                        <p className="mt-1 text-xs text-gray-400 ml-6">
                          Needs: {node.prerequisites.map((p) => getNodeById(p)?.name).join(", ")}
                        </p>
                      )}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Selected node detail */}
        {selectedNode && (
          <Card className="border-indigo-200 bg-indigo-50/50">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-indigo-500" />
                {selectedNode.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Prerequisites */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Prerequisites</p>
                {selectedNode.prerequisites.length === 0 ? (
                  <p className="text-sm text-green-600">No prerequisites — you can start here!</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {selectedNode.prerequisites.map((p) => {
                      const node = getNodeById(p);
                      return (
                        <Badge key={p} variant="outline" className="cursor-pointer hover:bg-white" onClick={() => setSelectedNode(node || null)}>
                          {node?.name}
                        </Badge>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Leads to */}
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Unlocks Next</p>
                {selectedNode.next.length === 0 ? (
                  <p className="text-sm text-gray-500">This is an advanced topic — no further prerequisites.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {selectedNode.next.map((n) => {
                      const node = getNodeById(n);
                      return (
                        <Badge key={n} variant="outline" className="cursor-pointer hover:bg-white" onClick={() => setSelectedNode(node || null)}>
                          <ArrowRight className="h-3 w-3 mr-1" /> {node?.name}
                        </Badge>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Learning Path */}
              <div className="pt-2 border-t">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Suggested Learning Path</p>
                <div className="flex items-center gap-1 flex-wrap text-xs">
                  {selectedNode.prerequisites.map((p, i) => (
                    <span key={p} className="flex items-center gap-1">
                      <span className="rounded bg-white px-2 py-1 border">{getNodeById(p)?.name}</span>
                      <ArrowRight className="h-3 w-3 text-gray-400" />
                    </span>
                  ))}
                  <span className="rounded bg-indigo-100 px-2 py-1 border border-indigo-200 font-medium text-indigo-700">
                    {selectedNode.name}
                  </span>
                  {selectedNode.next.length > 0 && (
                    <>
                      <ArrowRight className="h-3 w-3 text-gray-400" />
                      <span className="rounded bg-white px-2 py-1 border text-gray-500">
                        {selectedNode.next.map((n) => getNodeById(n)?.name).join(" / ")}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
