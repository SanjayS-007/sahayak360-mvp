"use client";

import { useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { queryApi } from "@/lib/api";
import { MessageSquare, Loader2, Sparkles } from "lucide-react";
import type { QueryResponse } from "@/types";

export default function TeacherQueryPage() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<Array<{ q: string; a: QueryResponse }>>([]);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || question.length < 5) return;
    setIsLoading(true);

    try {
      const { data } = await queryApi.ask(question);
      setHistory((prev) => [{ q: question, a: data }, ...prev]);
      setQuestion("");
    } catch {
      toast.error("Failed to process query");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">AI Query Assistant</h2>
        <p className="text-gray-500">
          Ask questions about your students in natural language
        </p>

        {/* Query input */}
        <Card>
          <CardContent className="pt-6">
            <form onSubmit={handleAsk} className="flex gap-3">
              <Input
                placeholder="e.g. Which students are struggling with fractions?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="flex-1"
                minLength={5}
              />
              <Button type="submit" disabled={isLoading || question.length < 5}>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Suggestions */}
        {history.length === 0 && (
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {[
              "Who needs the most help right now?",
              "What are the common gaps in class 8-A?",
              "Show me students below 50% mastery in algebra",
              "Which topics should I revisit this week?",
            ].map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => setQuestion(suggestion)}
                className="rounded-lg border bg-white p-3 text-left text-sm text-gray-700 hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <MessageSquare className="mb-1 h-4 w-4 text-primary-500" />
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* History */}
        <div className="space-y-4">
          {history.map((item, idx) => (
            <Card key={idx}>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-primary-500" />
                  <p className="text-sm font-medium text-gray-700">{item.q}</p>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-900">{item.a.answer}</p>
                {item.a.confidence > 0 && (
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant={item.a.confidence > 0.5 ? "success" : "warning"}>
                      Confidence: {Math.round(item.a.confidence * 100)}%
                    </Badge>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
