"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth-store";
import { authApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { GraduationCap, Loader2, BookOpen, User, Shield, ChevronRight } from "lucide-react";
import type { LoginResponse } from "@/types";

const DEMO_ACCOUNTS = [
  {
    role: "Teacher",
    name: "Ms. Priya Sharma",
    detail: "Class 9-A · Mathematics · 13 students",
    email: "teacher1@school.com",
    password: "Demo@2026Secure",
    icon: BookOpen,
    color: "from-blue-500 to-blue-600",
    bg: "bg-blue-50 hover:bg-blue-100 border-blue-200 hover:border-blue-400",
    badge: "bg-blue-100 text-blue-700",
  },
  {
    role: "Student",
    name: "Aarav Patel",
    detail: "Class 9-A · Mastery 14% · At risk",
    email: "student1@school.com",
    password: "Demo@2026Secure",
    icon: User,
    color: "from-emerald-500 to-emerald-600",
    bg: "bg-emerald-50 hover:bg-emerald-100 border-emerald-200 hover:border-emerald-400",
    badge: "bg-emerald-100 text-emerald-700",
  },
  {
    role: "Admin",
    name: "Dr. Suresh Menon",
    detail: "3 teachers · 18 students · Full access",
    email: "admin1@school.com",
    password: "Demo@2026Secure",
    icon: Shield,
    color: "from-violet-500 to-violet-600",
    bg: "bg-violet-50 hover:bg-violet-100 border-violet-200 hover:border-violet-400",
    badge: "bg-violet-100 text-violet-700",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fillingDemo, setFillingDemo] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const { data } = await authApi.login(email, password);
      const resp = data as LoginResponse;
      const user = {
        user_id: resp.user_id,
        email,
        full_name: resp.full_name,
        role: resp.role,
        class_section: resp.class_section,
      };
      login(resp.access_token, user);
      toast.success(`Welcome, ${resp.full_name}!`);
      router.push(`/${resp.role}/dashboard`);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(error.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const fillDemo = (account: typeof DEMO_ACCOUNTS[0]) => {
    setFillingDemo(account.role);
    // Simulate natural typing feel with a brief flash
    setEmail("");
    setPassword("");
    setTimeout(() => {
      setEmail(account.email);
      setPassword(account.password);
      setFillingDemo(null);
      toast.success(`Demo credentials loaded for ${account.name}`, {
        description: "Click Sign In to continue",
        duration: 3000,
      });
    }, 300);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50 p-4">
      <div className="w-full max-w-md space-y-4">
        {/* Demo accounts panel */}
        <Card className="border-dashed border-2 border-gray-200 shadow-sm">
          <CardContent className="pt-4 pb-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3 text-center">
              ✦ Judge Preview — Select a demo account
            </p>
            <div className="space-y-2">
              {DEMO_ACCOUNTS.map((account) => {
                const Icon = account.icon;
                const isLoading = fillingDemo === account.role;
                return (
                  <button
                    key={account.role}
                    onClick={() => fillDemo(account)}
                    disabled={isLoading || isSubmitting}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-150 text-left group ${account.bg}`}
                  >
                    <div className={`flex-shrink-0 h-9 w-9 rounded-lg bg-gradient-to-br ${account.color} flex items-center justify-center shadow-sm`}>
                      {isLoading ? (
                        <Loader2 className="h-4 w-4 text-white animate-spin" />
                      ) : (
                        <Icon className="h-4 w-4 text-white" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-gray-900 text-sm">{account.name}</span>
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${account.badge}`}>
                          {account.role}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 truncate">{account.detail}</p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-400 group-hover:text-gray-600 flex-shrink-0 transition-transform group-hover:translate-x-0.5" />
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Login form */}
        <Card className="shadow-md">
          <CardHeader className="text-center pb-4">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-100">
              <GraduationCap className="h-7 w-7 text-primary-600" />
            </div>
            <CardTitle className="text-2xl">Sahayak 360</CardTitle>
            <CardDescription>AI-powered educational analytics</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="teacher@school.edu"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={isSubmitting || fillingDemo !== null}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>
            </form>
            <p className="mt-4 text-center text-sm text-gray-500">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="font-medium text-primary-600 hover:underline">
                Create one
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
