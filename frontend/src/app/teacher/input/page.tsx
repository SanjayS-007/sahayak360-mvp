"use client";

import { useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ingestApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import { Upload, MessageSquare, Camera, Loader2, CheckCircle } from "lucide-react";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

type TabId = "structured" | "freetext" | "vision";

export default function TeacherInputPage() {
  const [activeTab, setActiveTab] = useState<TabId>("structured");

  const tabs = [
    { id: "structured" as TabId, label: "Structured Input", icon: Upload },
    { id: "freetext" as TabId, label: "Natural Language", icon: MessageSquare },
    { id: "vision" as TabId, label: "Scan Image", icon: Camera },
  ];

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">Input Assessment Data</h2>

        {/* Tab selector */}
        <div className="flex gap-2 rounded-lg border bg-white p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-1 items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? "bg-primary-600 text-white shadow-sm"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {activeTab === "structured" && <StructuredForm />}
        {activeTab === "freetext" && <FreetextForm />}
        {activeTab === "vision" && <VisionForm />}
      </div>
    </AppShell>
  );
}

function StructuredForm() {
  const { user } = useAuthStore();
  const [studentId, setStudentId] = useState("");
  const [classSection, setClassSection] = useState(user?.class_section || "");
  const [subject, setSubject] = useState("mathematics");
  const [maxScore, setMaxScore] = useState("");
  const [totalObtained, setTotalObtained] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setResult(null);

    try {
      const { data } = await ingestApi.structured({
        teacher_id: user?.user_id,
        student_id: studentId,
        class_section: classSection,
        subject,
        max_score: parseFloat(maxScore),
        total_obtained: parseFloat(totalObtained),
      });
      setResult(data);
      toast.success("Assessment data processed successfully!");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(error.response?.data?.detail || "Failed to process data");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Structured Assessment Input</CardTitle>
        <CardDescription>Enter marks directly in structured format</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Student ID</label>
              <Input
                placeholder="STU-01"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Class Section</label>
              <Input
                placeholder="8-A"
                value={classSection}
                onChange={(e) => setClassSection(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Subject</label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="flex h-10 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
              >
                <option value="mathematics">Mathematics</option>
                <option value="science">Science</option>
                <option value="english">English</option>
                <option value="hindi">Hindi</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Max Score</label>
              <Input
                type="number"
                placeholder="100"
                value={maxScore}
                onChange={(e) => setMaxScore(e.target.value)}
                min="0"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Total Obtained</label>
              <Input
                type="number"
                placeholder="78"
                value={totalObtained}
                onChange={(e) => setTotalObtained(e.target.value)}
                min="0"
                required
              />
            </div>
          </div>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Submit Assessment
          </Button>
        </form>
        {result && <ResultDisplay result={result} />}
      </CardContent>
    </Card>
  );
}

function FreetextForm() {
  const { user } = useAuthStore();
  const [rawText, setRawText] = useState("");
  const [classSection, setClassSection] = useState(user?.class_section || "");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setResult(null);

    try {
      const { data } = await ingestApi.freetext({
        teacher_id: user?.user_id || "",
        raw_text: rawText,
        class_section: classSection,
      });
      setResult(data);
      toast.success("Text parsed and processed successfully!");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(error.response?.data?.detail || "Failed to process text");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Natural Language Input</CardTitle>
        <CardDescription>
          Describe the assessment in your own words — AI will extract the data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Class Section</label>
            <Input
              placeholder="8-A"
              value={classSection}
              onChange={(e) => setClassSection(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Assessment Description</label>
            <textarea
              className="flex min-h-[120px] w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
              placeholder="e.g. Ravi scored 8/10 in fractions test. He got Q1 and Q5 wrong — both on equivalent fractions. Priya got full marks."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              required
              minLength={10}
            />
          </div>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Parse & Process
          </Button>
        </form>
        {result && <ResultDisplay result={result} />}
      </CardContent>
    </Card>
  );
}

function VisionForm() {
  const { user } = useAuthStore();
  const [classSection, setClassSection] = useState(user?.class_section || "");
  const [subject, setSubject] = useState("mathematics");
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) {
      setFile(accepted[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/png": [], "image/jpeg": [] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error("Please upload an image first");
      return;
    }
    setIsSubmitting(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("teacher_id", user?.user_id || "");
    formData.append("class_section", classSection);
    formData.append("subject", subject);

    try {
      const { data } = await ingestApi.vision(formData);
      setResult(data);
      toast.success("Image processed successfully!");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(error.response?.data?.detail || "Failed to process image");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Scan Answer Sheet</CardTitle>
        <CardDescription>Upload a photo of an answer sheet for AI extraction</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Class Section</label>
              <Input
                placeholder="8-A"
                value={classSection}
                onChange={(e) => setClassSection(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Subject</label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="flex h-10 w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
              >
                <option value="mathematics">Mathematics</option>
                <option value="science">Science</option>
                <option value="english">English</option>
              </select>
            </div>
          </div>

          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed transition-colors ${
              isDragActive
                ? "border-primary-500 bg-primary-50"
                : file
                ? "border-accent-500 bg-accent-50"
                : "border-gray-300 hover:border-gray-400"
            }`}
          >
            <input {...getInputProps()} />
            {file ? (
              <div className="text-center">
                <CheckCircle className="mx-auto h-8 w-8 text-accent-600" />
                <p className="mt-2 text-sm font-medium">{file.name}</p>
                <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(0)} KB</p>
              </div>
            ) : (
              <div className="text-center">
                <Camera className="mx-auto h-8 w-8 text-gray-400" />
                <p className="mt-2 text-sm text-gray-600">
                  Drag & drop an image or click to browse
                </p>
                <p className="text-xs text-gray-400">PNG or JPEG, max 10MB</p>
              </div>
            )}
          </div>

          <Button type="submit" disabled={isSubmitting || !file}>
            {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Extract & Process
          </Button>
        </form>
        {result && <ResultDisplay result={result} />}
      </CardContent>
    </Card>
  );
}

function ResultDisplay({ result }: { result: Record<string, unknown> }) {
  return (
    <div className="mt-4 rounded-lg border border-accent-200 bg-accent-50 p-4">
      <div className="flex items-center gap-2 mb-2">
        <CheckCircle className="h-5 w-5 text-accent-600" />
        <span className="text-sm font-semibold text-accent-700">Processing Complete</span>
      </div>
      <div className="space-y-1 text-sm text-gray-700">
        {result.event_id ? <p>Event ID: <Badge variant="outline">{String(result.event_id)}</Badge></p> : null}
        {result.parse_method ? <p>Method: {String(result.parse_method)}</p> : null}
        {result.cognitive_analysis ? (
          <p>Gaps detected: {String((result.cognitive_analysis as Record<string, unknown>).gaps_detected ?? 0)}</p>
        ) : null}
      </div>
    </div>
  );
}
