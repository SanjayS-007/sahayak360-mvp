"use client";

import { useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { queryApi } from "@/lib/api";
import {
  MessageSquare,
  Loader2,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Database,
  Brain,
  Lightbulb,
  Users,
  TrendingDown,
  AlertTriangle,
  Target,
} from "lucide-react";
import type { QueryResponse } from "@/types";

const SMART_SUGGESTIONS = [
  { text: "Who needs the most help right now?", icon: AlertTriangle, color: "text-red-500" },
  { text: "Which students have declining mastery trends?", icon: TrendingDown, color: "text-amber-500" },
  { text: "Show me prerequisite gaps for struggling students", icon: Target, color: "text-blue-500" },
  { text: "What are the common gaps across my class?", icon: Users, color: "text-purple-500" },
  { text: "Which topics should I revisit this week?", icon: Lightbulb, color: "text-emerald-500" },
  { text: "Who has the most open intervention tickets?", icon: Brain, color: "text-indigo-500" },
];

const FOLLOW_UP_MAP: Record<string, string[]> = {
  struggling: [
    "What are their prerequisite gaps?",
    "Should I send them a micro-test?",
    "Show their mastery timeline",
  ],
  default: [
    "Drill deeper into this pattern",
    "Which students are improving fastest?",
    "What interventions worked best this month?",
  ],
};

export default function TeacherQueryPage() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<Array<{ q: string; a: QueryResponse; showCypher?: boolean }>>([]);

  const handleAsk = async (q?: string) => {
    const query = q || question;
    if (!query.trim() || query.length < 5) return;
    setIsLoading(true);

    try {
      const { data } = await queryApi.ask(query);
      setHistory((prev) => [{ q: query, a: data, showCypher: false }, ...prev]);
      setQuestion("");
    } catch {
      toast.error("Failed to process query");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAsk();
  };

  const toggleCypher = (idx: number) => {
    setHistory((prev) =>
      prev.map((item, i) => (i === idx ? { ...item, showCypher: !item.showCypher } : item))
    );
  };

  const getConfidenceConfig = (confidence: number) => {
    if (confidence >= 0.7) return { label: "High", color: "bg-emerald-100 text-emerald-700" };
    if (confidence >= 0.4) return { label: "Medium", color: "bg-amber-100 text-amber-700" };
    return { label: "Low", color: "bg-red-100 text-red-700" };
  };

  const getFollowUps = (query: string): string[] => {
    if (query.toLowerCase().includes("struggling") || query.toLowerCase().includes("help"))
      return FOLLOW_UP_MAP.struggling;
    return FOLLOW_UP_MAP.default;
  };

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Query Assistant</h2>
          <p className="mt-1 text-sm text-gray-500">
            Ask anything about your students — powered by knowledge graph + Gemini AI
          </p>
        </div>

        {/* Query input */}
        <Card className="border-primary-200 shadow-sm">
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <div className="relative flex-1">
                <Brain className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="e.g. Which students need prerequisite review for fractions?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  className="pl-10"
                  minLength={5}
                />
              </div>
              <Button type="submit" disabled={isLoading || question.length < 5} className="px-5">
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-1" />
                    Ask
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Smart Suggestions */}
        {history.length === 0 && (
          <div>
            <p className="text-sm font-medium text-gray-500 mb-3">Suggested questions:</p>
            <div className="grid grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
              {SMART_SUGGESTIONS.map((suggestion) => {
                const Icon = suggestion.icon;
                return (
                  <button
                    key={suggestion.text}
                    onClick={() => { setQuestion(suggestion.text); handleAsk(suggestion.text); }}
                    disabled={isLoading}
                    className="flex items-start gap-3 rounded-lg border bg-white p-3 text-left text-sm text-gray-700 hover:border-primary-300 hover:bg-primary-50/50 transition-all hover:shadow-sm disabled:opacity-50"
                  >
                    <Icon className={`h-4 w-4 mt-0.5 shrink-0 ${suggestion.color}`} />
                    <span>{suggestion.text}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Results */}
        <div className="space-y-4">
          {history.map((item, idx) => {
            const conf = getConfidenceConfig(item.a.confidence || 0);
            const followUps = getFollowUps(item.q);
            return (
              <Card key={idx} className="overflow-hidden animate-in fade-in slide-in-from-top-2" style={{ animationDelay: "0ms" }}>
                {/* Question Header */}
                <CardHeader className="pb-2 bg-gray-50/50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MessageSquare className="h-4 w-4 text-primary-500" />
                      <p className="text-sm font-medium text-gray-700">{item.q}</p>
                    </div>
                    {item.a.confidence > 0 && (
                      <Badge className={conf.color}>
                        {conf.label} confidence
                      </Badge>
                    )}
                  </div>
                </CardHeader>

                {/* Answer Body */}
                <CardContent className="pt-4 space-y-3">
                  <div className="rounded-lg bg-white p-3 border border-gray-100">
                    <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">{item.a.answer}</p>
                  </div>

                  {/* Data Table (if structured data returned) */}
                  {(() => {
                    const tableData = item.a.data as Array<Record<string, unknown>> | undefined;
                    if (!tableData || !Array.isArray(tableData) || tableData.length === 0) return null;
                    return (
                    <div className="overflow-x-auto rounded-lg border">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            {Object.keys(tableData[0]).map((key) => (
                              <th key={key} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                {key.replace(/_/g, " ")}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {tableData.slice(0, 10).map((row, rIdx) => (
                            <tr key={rIdx} className="border-t">
                              {Object.values(row).map((val, cIdx) => (
                                <td key={cIdx} className="px-3 py-2 text-gray-700">
                                  {typeof val === "number" && val < 1 && val > 0
                                    ? `${(val * 100).toFixed(0)}%`
                                    : String(val ?? "-")}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    );
                  })()}

                  {/* Cypher Query (collapsible) */}
                  {item.a.cypher_used && (
                    <div>
                      <button
                        onClick={() => toggleCypher(idx)}
                        className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <Database className="h-3 w-3" />
                        <span>View query</span>
                        {item.showCypher ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                      </button>
                      {item.showCypher && (
                        <pre className="mt-2 rounded-lg bg-gray-900 p-3 text-xs text-gray-300 overflow-x-auto">
                          {item.a.cypher_used}
                        </pre>
                      )}
                    </div>
                  )}

                  {/* Follow-up Suggestions */}
                  <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
                    {followUps.map((followUp) => (
                      <button
                        key={followUp}
                        onClick={() => { setQuestion(followUp); handleAsk(followUp); }}
                        disabled={isLoading}
                        className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs text-gray-600 hover:bg-primary-50 hover:border-primary-200 hover:text-primary-700 transition-all disabled:opacity-50"
                      >
                        {followUp}
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}
