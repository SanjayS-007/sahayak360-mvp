"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { quizApi } from "@/lib/api";
import { Clock, CheckCircle, XCircle, Loader2, RefreshCw } from "lucide-react";

interface QuizQuestion {
  question_id: string;
  question_text: string;
  options: string[];
  bloom_level?: string;
  kc_id?: string;
}

interface QuizResult {
  session_id: string;
  score: number;
  total_questions: number;
  correct_count: number;
  mastery_deltas: Record<string, number>;
}

interface PendingSession {
  session_id: string;
  student_id: string;
  status: string;
  target_kc_ids: string[];
  dispatched_at: string | null;
}

type QuizState = "idle" | "active" | "submitted";

export default function StudentQuizPage() {
  const [state, setState] = useState<QuizState>("idle");
  const [pendingSessions, setPendingSessions] = useState<PendingSession[]>([]);
  const [sessionId, setSessionId] = useState("");
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [timeLeft, setTimeLeft] = useState(600);
  const [isLoading, setIsLoading] = useState(false);
  const [polling, setPolling] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  // Poll for pending quizzes every 10 seconds
  const checkPendingQuizzes = useCallback(async () => {
    try {
      const { data } = await quizApi.getPending();
      const pending = (data || []).filter((s: PendingSession) => s.status === "pending");
      setPendingSessions(pending);
      if (pending.length > 0 && state === "idle") {
        toast.info("You have a pending quiz from your teacher!");
      }
    } catch {
      // Silent fail - will retry
    }
  }, [state]);

  useEffect(() => {
    checkPendingQuizzes();
    pollRef.current = setInterval(checkPendingQuizzes, 10000);
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [checkPendingQuizzes]);

  // Timer countdown
  useEffect(() => {
    if (state === "active" && timeLeft > 0) {
      timerRef.current = setInterval(() => {
        setTimeLeft((t) => {
          if (t <= 1) {
            handleSubmit();
            return 0;
          }
          return t - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  const startQuiz = async (pendingSessionId: string) => {
    setIsLoading(true);
    try {
      const { data } = await quizApi.getSession(pendingSessionId);
      setSessionId(data.session_id);
      setQuestions(data.questions || []);
      setTimeLeft(data.time_limit_seconds || 600);
      setState("active");
      setAnswers({});
      // Stop polling while quiz is active
      if (pollRef.current) clearInterval(pollRef.current);
    } catch {
      toast.error("Failed to load quiz");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setIsLoading(true);

    const responses = questions.map((q) => ({
      question_id: q.question_id,
      answer: answers[q.question_id] || "",
    }));

    try {
      const { data } = await quizApi.submit(sessionId, responses);
      setResult(data);
      setState("submitted");
      toast.success("Quiz submitted!");
    } catch {
      toast.error("Failed to submit quiz");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setPolling(true);
    await checkPendingQuizzes();
    setPolling(false);
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Assessment Quiz</h2>
          {state === "idle" && (
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={polling}>
              <RefreshCw className={`h-4 w-4 mr-2 ${polling ? "animate-spin" : ""}`} />
              Check for quizzes
            </Button>
          )}
        </div>

        {state === "idle" && pendingSessions.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <Clock className="h-12 w-12 text-gray-300 mb-4" />
              <p className="text-lg font-medium text-gray-600">No active quiz</p>
              <p className="text-sm text-gray-400 mt-1">
                Your teacher will send you a quiz when it&apos;s time. Checking every 10 seconds...
              </p>
            </CardContent>
          </Card>
        )}

        {state === "idle" && pendingSessions.length > 0 && (
          <div className="space-y-3">
            {pendingSessions.map((session) => (
              <Card key={session.session_id} className="border-primary-200 bg-primary-50/50">
                <CardContent className="flex items-center justify-between py-4">
                  <div>
                    <p className="font-semibold text-gray-900">Quiz Available</p>
                    <p className="text-sm text-gray-500">
                      Topics: {session.target_kc_ids?.join(", ") || "Mixed"}
                    </p>
                    {session.dispatched_at && (
                      <p className="text-xs text-gray-400 mt-1">
                        Sent: {new Date(session.dispatched_at).toLocaleString()}
                      </p>
                    )}
                  </div>
                  <Button onClick={() => startQuiz(session.session_id)} disabled={isLoading}>
                    {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Start Quiz
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {state === "active" && (
          <>
            {/* Timer bar */}
            <div className="flex items-center justify-between rounded-lg border bg-white p-4">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary-600" />
                <span className="font-mono text-lg font-bold">{formatTime(timeLeft)}</span>
              </div>
              <Badge>
                {Object.keys(answers).length}/{questions.length} answered
              </Badge>
            </div>

            {/* Questions */}
            <div className="space-y-4">
              {questions.map((q, idx) => (
                <Card key={q.question_id}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">
                      Q{idx + 1}. {q.question_text}
                    </CardTitle>
                    {q.bloom_level && <Badge variant="outline" className="w-fit">{q.bloom_level}</Badge>}
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {q.options.map((option) => (
                        <button
                          key={option}
                          onClick={() => setAnswers((prev) => ({ ...prev, [q.question_id]: option }))}
                          className={`w-full rounded-lg border p-3 text-left text-sm transition-colors ${
                            answers[q.question_id] === option
                              ? "border-primary-500 bg-primary-50 text-primary-700"
                              : "border-gray-200 hover:bg-gray-50"
                          }`}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Button onClick={handleSubmit} className="w-full" size="lg" disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Submit Answers
            </Button>
          </>
        )}

        {state === "submitted" && result && (
          <Card>
            <CardHeader>
              <CardTitle>Quiz Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="text-center">
                <p className="text-5xl font-bold text-primary-600">
                  {result.correct_count}/{result.total_questions}
                </p>
                <p className="mt-1 text-gray-500">Score: {Math.round(result.score * 100)}%</p>
                <Progress value={result.score * 100} className="mt-4 mx-auto max-w-xs" />
              </div>

              {/* Per-KC results */}
              {Object.keys(result.mastery_deltas).length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">Mastery Updates</p>
                  {Object.entries(result.mastery_deltas).map(([kc, score]) => (
                    <div key={kc} className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">{kc}</span>
                      <div className="flex items-center gap-1">
                        {(score as number) >= 0.7 ? (
                          <CheckCircle className="h-4 w-4 text-accent-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-danger-400" />
                        )}
                        <span className="font-medium">{Math.round((score as number) * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <Button
                variant="outline"
                onClick={() => {
                  setState("idle");
                  setResult(null);
                  setAnswers({});
                  setQuestions([]);
                  // Resume polling
                  checkPendingQuizzes();
                  pollRef.current = setInterval(checkPendingQuizzes, 10000);
                }}
                className="w-full"
              >
                Done
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </AppShell>
  );
}
