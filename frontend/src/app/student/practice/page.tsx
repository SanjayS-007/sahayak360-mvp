"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { practiceApi } from "@/lib/api";
import {
  CheckCircle2,
  XCircle,
  ArrowRight,
  RotateCcw,
  Trophy,
  Loader2,
  Zap,
  Brain,
} from "lucide-react";

interface Question {
  id: string;
  text: string;
  options: string[];
}

interface ResultItem {
  question_id: string;
  correct: boolean;
  correct_index: number;
  explanation: string;
}

interface SubmitResult {
  score: number;
  correct: number;
  total: number;
  results: ResultItem[];
  mastery_after: number;
  next_difficulty: string;
  xp_earned?: number;
  badges_earned?: Array<{ name: string; icon: string }>;
  message: string;
}

type Phase = "select" | "practice" | "results";

export default function PracticePageWrapper() {
  return (
    <Suspense fallback={<div className="flex h-64 items-center justify-center"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" /></div>}>
      <PracticePage />
    </Suspense>
  );
}

function PracticePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const preselectedKC = searchParams.get("kc");

  const [phase, setPhase] = useState<Phase>(preselectedKC ? "practice" : "select");
  const [availableKCs, setAvailableKCs] = useState<Array<{ kc_id: string; levels: string[]; total_questions: number }>>([]);
  const [selectedKC, setSelectedKC] = useState(preselectedKC || "");
  const [difficulty, setDifficulty] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<Array<{ question_id: string; selected_index: number }>>([]);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (phase === "select") {
      loadAvailableKCs();
    }
    if (preselectedKC && phase === "practice" && questions.length === 0) {
      generateQuestions(preselectedKC);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadAvailableKCs() {
    try {
      const { data } = await practiceApi.availableKCs();
      setAvailableKCs(data.kcs);
    } catch {
      toast.error("Failed to load practice topics");
    }
  }

  async function generateQuestions(kcId: string) {
    setLoading(true);
    try {
      const { data } = await practiceApi.generate({ kc_id: kcId, count: 5 });
      setQuestions(data.questions);
      setDifficulty(data.difficulty);
      setSelectedKC(kcId);
      setCurrentQ(0);
      setAnswers([]);
      setSelectedOption(null);
      setPhase("practice");
    } catch {
      toast.error("Failed to generate questions. Try another topic.");
      setPhase("select");
    } finally {
      setLoading(false);
    }
  }

  function selectAnswer(index: number) {
    setSelectedOption(index);
  }

  function confirmAnswer() {
    if (selectedOption === null) return;
    const newAnswers = [...answers, { question_id: questions[currentQ].id, selected_index: selectedOption }];
    setAnswers(newAnswers);
    setSelectedOption(null);

    if (currentQ < questions.length - 1) {
      setCurrentQ(currentQ + 1);
    } else {
      submitPractice(newAnswers);
    }
  }

  async function submitPractice(finalAnswers: typeof answers) {
    setLoading(true);
    try {
      const { data } = await practiceApi.submit({
        kc_id: selectedKC,
        difficulty,
        answers: finalAnswers,
      });
      setResult(data);
      setPhase("results");
    } catch {
      toast.error("Failed to submit. Your progress may not be saved.");
    } finally {
      setLoading(false);
    }
  }

  function tryNextLevel() {
    if (result) {
      setDifficulty(result.next_difficulty);
      generateQuestions(selectedKC);
    }
  }

  // --- RENDER ---

  if (loading && phase === "practice" && questions.length === 0) {
    return (
      <AppShell requiredRole="student">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          <span className="ml-3 text-gray-600">Generating questions...</span>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6 max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3">
          <Brain className="h-7 w-7 text-indigo-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Practice Mode</h2>
            <p className="text-sm text-gray-500">Progressive difficulty • Earn mastery points</p>
          </div>
        </div>

        {/* SELECT PHASE */}
        {phase === "select" && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Choose a Topic to Practice</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2">
                {availableKCs.map((kc) => (
                  <button
                    key={kc.kc_id}
                    onClick={() => generateQuestions(kc.kc_id)}
                    className="rounded-lg border p-4 text-left hover:border-indigo-400 hover:bg-indigo-50 transition-colors"
                  >
                    <p className="font-medium text-gray-900">{kc.kc_id.replace(/-/g, " ")}</p>
                    <p className="text-xs text-gray-500 mt-1">{kc.total_questions} questions • {kc.levels.join(", ")}</p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* PRACTICE PHASE */}
        {phase === "practice" && questions.length > 0 && (
          <>
            {/* Progress bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>{selectedKC.replace(/-/g, " ")}</span>
                <Badge variant="outline" className="capitalize">{difficulty}</Badge>
              </div>
              <Progress value={((currentQ + 1) / questions.length) * 100} className="h-2" />
              <p className="text-xs text-gray-400">Question {currentQ + 1} of {questions.length}</p>
            </div>

            {/* Question Card */}
            <Card>
              <CardContent className="pt-6">
                <p className="text-lg font-medium text-gray-900 mb-6">{questions[currentQ].text}</p>
                <div className="space-y-3">
                  {questions[currentQ].options.map((opt, idx) => (
                    <button
                      key={idx}
                      onClick={() => selectAnswer(idx)}
                      className={`w-full rounded-lg border p-4 text-left transition-all ${
                        selectedOption === idx
                          ? "border-indigo-500 bg-indigo-50 ring-2 ring-indigo-200"
                          : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      <span className="text-sm font-medium text-gray-500 mr-3">
                        {String.fromCharCode(65 + idx)}.
                      </span>
                      <span className="text-gray-800">{opt}</span>
                    </button>
                  ))}
                </div>

                <Button
                  onClick={confirmAnswer}
                  disabled={selectedOption === null || loading}
                  className="mt-6 w-full"
                >
                  {currentQ < questions.length - 1 ? (
                    <>Next <ArrowRight className="ml-2 h-4 w-4" /></>
                  ) : (
                    <>Submit Practice <Zap className="ml-2 h-4 w-4" /></>
                  )}
                </Button>
              </CardContent>
            </Card>
          </>
        )}

        {/* RESULTS PHASE */}
        {phase === "results" && result && (
          <>
            {/* Score Card */}
            <Card className={result.score >= 0.8 ? "border-green-200 bg-green-50" : result.score >= 0.5 ? "border-yellow-200 bg-yellow-50" : "border-red-200 bg-red-50"}>
              <CardContent className="pt-6 text-center">
                <Trophy className={`mx-auto h-12 w-12 ${result.score >= 0.8 ? "text-green-500" : result.score >= 0.5 ? "text-yellow-500" : "text-red-400"}`} />
                <h3 className="mt-3 text-2xl font-bold">{result.correct}/{result.total}</h3>
                <p className="text-gray-600">{result.message}</p>
                <div className="mt-4 flex justify-center gap-4 text-sm">
                  <span>Score: <strong>{Math.round(result.score * 100)}%</strong></span>
                  <span>Mastery: <strong>{Math.round(result.mastery_after * 100)}%</strong></span>
                </div>
                {result.xp_earned !== undefined && (
                  <div className="mt-3 inline-flex items-center gap-1 rounded-full bg-yellow-100 px-3 py-1 text-sm font-semibold text-yellow-800">
                    +{result.xp_earned} XP earned!
                  </div>
                )}
                {result.badges_earned && result.badges_earned.length > 0 && (
                  <div className="mt-2 flex justify-center gap-2">
                    {result.badges_earned.map((b) => (
                      <span key={b.name} className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-3 py-1 text-xs font-medium text-purple-700">
                        {b.icon} {b.name}
                      </span>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Explanations */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Review</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {result.results.map((r, idx) => (
                  <div key={r.question_id} className="flex gap-3 items-start">
                    {r.correct ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-800">Q{idx + 1}: {questions[idx]?.text}</p>
                      <p className="text-xs text-gray-500 mt-1">{r.explanation}</p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex gap-3">
              <Button variant="outline" onClick={() => { setPhase("select"); setResult(null); }}>
                <RotateCcw className="mr-2 h-4 w-4" /> Different Topic
              </Button>
              <Button onClick={tryNextLevel}>
                Continue ({result.next_difficulty}) <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
