"use client";

import { useAuthStore } from "@/store/auth-store";
import { Bell } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function Header() {
  const { user } = useAuthStore();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-gray-200 bg-white/80 px-6 backdrop-blur">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">
          {user?.role === "teacher" && "Teacher Portal"}
          {user?.role === "student" && "Student Portal"}
          {user?.role === "admin" && "Admin Panel"}
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <button className="relative rounded-lg p-2 hover:bg-gray-100">
          <Bell className="h-5 w-5 text-gray-600" />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-danger-500" />
        </button>
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-sm font-medium text-primary-700">
            {user?.full_name?.charAt(0) || "U"}
          </div>
          <Badge variant="outline">{user?.class_section || user?.role}</Badge>
        </div>
      </div>
    </header>
  );
}
