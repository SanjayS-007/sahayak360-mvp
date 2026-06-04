"use client";

import { useEffect, useState, useRef } from "react";
import { useAuthStore } from "@/store/auth-store";
import { Bell } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { notificationsApi } from "@/lib/api";

interface NotifItem {
  id: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string | null;
}

export function Header() {
  const { user } = useAuthStore();
  const [notifs, setNotifs] = useState<NotifItem[]>([]);
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadNotifs();
    const interval = setInterval(loadNotifs, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function loadNotifs() {
    try {
      const { data } = await notificationsApi.getAll();
      setNotifs(data.notifications || []);
      setUnread(data.unread_count || 0);
    } catch {
      // silent
    }
  }

  async function markAllRead() {
    try {
      await notificationsApi.markAllRead();
      setUnread(0);
      setNotifs((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch {
      // silent
    }
  }

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
        {/* Notification Bell */}
        <div className="relative" ref={dropdownRef}>
          <button
            className="relative rounded-lg p-2 hover:bg-gray-100"
            onClick={() => setOpen(!open)}
          >
            <Bell className="h-5 w-5 text-gray-600" />
            {unread > 0 && (
              <span className="absolute right-1 top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </button>

          {open && (
            <div className="absolute right-0 top-12 z-50 w-80 rounded-lg border bg-white shadow-lg">
              <div className="flex items-center justify-between border-b px-4 py-3">
                <span className="text-sm font-semibold">Notifications</span>
                {unread > 0 && (
                  <button onClick={markAllRead} className="text-xs text-indigo-600 hover:underline">
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-72 overflow-y-auto">
                {notifs.length === 0 ? (
                  <p className="p-4 text-center text-sm text-gray-400">No notifications yet</p>
                ) : (
                  notifs.slice(0, 10).map((n) => (
                    <div
                      key={n.id}
                      className={`border-b px-4 py-3 last:border-0 ${!n.read ? "bg-indigo-50" : ""}`}
                    >
                      <p className="text-sm font-medium text-gray-800">{n.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

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
