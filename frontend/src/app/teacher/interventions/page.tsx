"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { alertsApi } from "@/lib/api";
import { useAuthStore } from "@/store/auth-store";
import {
  ClipboardCheck,
  Clock,
  Play,
  FileCheck,
  CheckCircle2,
  ChevronRight,
  AlertTriangle,
  Loader2,
} from "lucide-react";

interface Ticket {
  ticket_id: string;
  student_id: string;
  student_name: string;
  teacher_id: string;
  ticket_type: string;
  priority: string;
  status: string;
  target_kc_id: string;
  target_kc_name: string;
  description: string;
  created_at: string;
  history: Array<{ from_status: string; to_status: string; timestamp: string; note: string }>;
}

interface TicketStats {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
}

const STATUS_COLUMNS = [
  { key: "open", label: "Open", icon: Clock, color: "text-indigo-600 bg-indigo-50" },
  { key: "in_progress", label: "In Progress", icon: Play, color: "text-blue-600 bg-blue-50" },
  { key: "awaiting_evidence", label: "Awaiting Evidence", icon: FileCheck, color: "text-amber-600 bg-amber-50" },
  { key: "resolved", label: "Resolved", icon: CheckCircle2, color: "text-emerald-600 bg-emerald-50" },
];

const NEXT_TRANSITIONS: Record<string, { status: string; label: string }[]> = {
  open: [{ status: "assigned", label: "Assign" }, { status: "in_progress", label: "Start" }],
  assigned: [{ status: "in_progress", label: "Start" }],
  in_progress: [{ status: "awaiting_evidence", label: "Await Evidence" }, { status: "resolved", label: "Resolve" }],
  awaiting_evidence: [{ status: "resolved", label: "Resolve" }, { status: "in_progress", label: "Continue" }],
  resolved: [{ status: "closed", label: "Close" }],
};

const PRIORITY_COLORS: Record<string, string> = {
  P1: "bg-red-100 text-red-700 border-red-200",
  P2: "bg-orange-100 text-orange-700 border-orange-200",
  P3: "bg-amber-100 text-amber-700 border-amber-200",
  P4: "bg-gray-100 text-gray-600 border-gray-200",
};

const TYPE_LABELS: Record<string, string> = {
  micro_test_dispatch: "Micro Test",
  remediation_plan: "Remediation",
  parent_meeting: "Parent Meeting",
  specialist_referral: "Specialist",
  progress_check: "Progress Check",
};

export default function TeacherInterventionsPage() {
  const { user } = useAuthStore();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<TicketStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [transitioning, setTransitioning] = useState<string>("");

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [ticketsRes, statsRes] = await Promise.all([
        alertsApi.getTickets({ status: "open,assigned,in_progress,awaiting_evidence,resolved" }),
        alertsApi.getTicketStats(),
      ]);
      setTickets(ticketsRes.data);
      setStats(statsRes.data);
    } catch {
      toast.error("Failed to load interventions");
    } finally {
      setLoading(false);
    }
  }

  async function handleTransition(ticketId: string, newStatus: string) {
    setTransitioning(ticketId);
    try {
      await alertsApi.transitionTicket(ticketId, { new_status: newStatus });
      toast.success(`Ticket updated to ${newStatus.replace("_", " ")}`);
      await loadData();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Transition failed");
    } finally {
      setTransitioning("");
    }
  }

  const getTicketsForStatus = (status: string) =>
    tickets.filter((t) => t.status === status || (status === "open" && t.status === "assigned"));

  if (loading) {
    return (
      <AppShell requiredRole="teacher">
        <div className="space-y-6">
          <div className="h-8 w-72 animate-pulse rounded bg-gray-200" />
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-64 animate-pulse rounded-lg bg-gray-100" />
            ))}
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell requiredRole="teacher">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Intervention Command Center</h2>
            <p className="mt-1 text-sm text-gray-500">
              Track and manage student support actions across their lifecycle
            </p>
          </div>
          {stats && (
            <div className="flex gap-3">
              <Badge variant="outline" className="text-xs">
                {stats.total} total
              </Badge>
              {stats.by_priority.P1 && (
                <Badge className="bg-red-100 text-red-700 text-xs">
                  {stats.by_priority.P1} urgent
                </Badge>
              )}
            </div>
          )}
        </div>

        {/* Kanban Board */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {STATUS_COLUMNS.map((column) => {
            const columnTickets = getTicketsForStatus(column.key);
            return (
              <div key={column.key} className="space-y-3">
                {/* Column Header */}
                <div className={`flex items-center gap-2 rounded-lg px-3 py-2 ${column.color}`}>
                  <column.icon className="h-4 w-4" />
                  <span className="text-sm font-medium">{column.label}</span>
                  <Badge variant="outline" className="ml-auto text-xs h-5 min-w-5 justify-center">
                    {columnTickets.length}
                  </Badge>
                </div>

                {/* Ticket Cards */}
                <div className="space-y-2 min-h-[200px]">
                  {columnTickets.length === 0 ? (
                    <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center">
                      <p className="text-xs text-gray-400">No tickets</p>
                    </div>
                  ) : (
                    columnTickets.map((ticket, idx) => (
                      <div
                        key={ticket.ticket_id}
                        className="animate-in fade-in slide-in-from-bottom-1"
                        style={{ animationDelay: `${idx * 40}ms`, animationFillMode: "both" }}
                      >
                        <TicketCard
                          ticket={ticket}
                          onTransition={handleTransition}
                          isTransitioning={transitioning === ticket.ticket_id}
                        />
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}

function TicketCard({
  ticket,
  onTransition,
  isTransitioning,
}: {
  ticket: Ticket;
  onTransition: (ticketId: string, newStatus: string) => void;
  isTransitioning: boolean;
}) {
  const transitions = NEXT_TRANSITIONS[ticket.status] || [];
  const priorityColor = PRIORITY_COLORS[ticket.priority] || PRIORITY_COLORS.P3;
  const typeLabel = TYPE_LABELS[ticket.ticket_type] || ticket.ticket_type;

  return (
    <Card className="hover:shadow-sm transition-shadow">
      <CardContent className="p-3 space-y-2">
        {/* Top row: Priority + Type */}
        <div className="flex items-center justify-between">
          <Badge className={`text-[10px] px-1.5 py-0 ${priorityColor}`}>
            {ticket.priority}
          </Badge>
          <span className="text-[10px] text-gray-400 font-mono">
            {ticket.ticket_id.slice(0, 12)}
          </span>
        </div>

        {/* Student name */}
        <p className="text-sm font-medium text-gray-900 truncate">
          {ticket.student_name}
        </p>

        {/* Type + KC */}
        <div className="space-y-1">
          <p className="text-xs text-gray-500">{typeLabel}</p>
          <p className="text-xs text-gray-700 font-medium truncate">
            {ticket.target_kc_name}
          </p>
        </div>

        {/* Action buttons */}
        {transitions.length > 0 && (
          <div className="flex gap-1 pt-1">
            {transitions.slice(0, 2).map((t) => (
              <Button
                key={t.status}
                size="sm"
                variant="outline"
                className="text-[10px] h-6 px-2 flex-1"
                disabled={isTransitioning}
                onClick={() => onTransition(ticket.ticket_id, t.status)}
              >
                {isTransitioning ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <>
                    <ChevronRight className="h-3 w-3 mr-0.5" />
                    {t.label}
                  </>
                )}
              </Button>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
