<!-- markdownlint-disable-file -->

# Task Details: Sahayak 360 — Peak Platform Enhancement

## Research Reference

**Source Research**: #file:../research/20260604-platform-enhancement-research.md

---

## Phase 1: Early Warning & Alert System

### Task 1.1: Create Backend Alert Computation Endpoint

Create a new route that computes real-time alerts for a teacher's class by leveraging the existing `risk_scorer.py` engine and `MasteryRecord` data.

**New file**: `backend/api/routes_alerts.py`

**Endpoint**: `GET /api/alerts/teacher?class_section=9-A`

**Logic**:
1. Query all students in the class section
2. For each student: fetch mastery records → compute `overall_mastery` → fetch recent assessment events
3. Call existing `compute_academic_risk()`, `compute_behavioral_risk()`, `compute_cognitive_risk()`, `compute_composite_risk()` from `core/risk_scorer.py`
4. Filter students with `risk_tier` in (HIGH, CRITICAL)
5. For students with declining trend (last 3 scores decreasing), add `PREDICTIVE_DECLINE` alert type
6. Sort by `composite_score` descending (most urgent first)

**Response schema**:
```python
class AlertItem(BaseModel):
    student_id: str
    student_name: str
    alert_type: str  # "risk_critical", "risk_high", "trend_declining", "new_gap"
    risk_tier: str
    composite_score: float
    contributing_factors: list[str]
    recommended_action: str
    created_at: datetime

class AlertsResponse(BaseModel):
    alerts: list[AlertItem]
    total_critical: int
    total_high: int
    class_section: str
```

- **Files**:
  - `backend/api/routes_alerts.py` — New router file
  - `backend/main.py` — Register new router at `/api/alerts`
- **Success**:
  - `GET /api/alerts/teacher?class_section=9-A` returns prioritized alert list
  - Response includes contributing factors and recommended action text
  - Only HIGH/CRITICAL students + trend-declining students appear
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 20-60) — ABC Risk Scorer algorithm
  - #file:../research/20260604-platform-enhancement-research.md (Lines 220-260) — Gap analysis table
- **Dependencies**:
  - Existing `core/risk_scorer.py` (all functions)
  - Existing `services/dashboard_analytics.py` (student mastery queries)

---

### Task 1.2: Create Backend Ticket Management Endpoints

Expose the existing `InterventionTicket` model through CRUD-like endpoints for the teacher Kanban UI.

**Add to**: `backend/api/routes_alerts.py` (same router)

**Endpoints**:

```python
# List tickets for teacher (filterable by status)
GET /api/alerts/tickets?class_section=9-A&status=open,assigned,in_progress

# Get ticket detail with full history
GET /api/alerts/tickets/{ticket_id}

# Transition ticket status (state machine enforced)
PATCH /api/alerts/tickets/{ticket_id}/transition
Body: { "new_status": "in_progress", "note": "Started remedial session" }

# Get ticket statistics for teacher
GET /api/alerts/tickets/stats?class_section=9-A
Response: { total: 15, by_status: {open: 5, in_progress: 3, ...}, by_priority: {P1: 2, ...} }
```

**Transition logic**: Use existing `can_transition()` and `transition_ticket()` from `core/ticket_lifecycle.py`. If invalid transition, return 400 with valid options.

**Ticket listing query**:
```python
stmt = select(InterventionTicket).where(
    InterventionTicket.teacher_id == user.user_id,
    InterventionTicket.status.in_(status_filter),
).order_by(
    InterventionTicket.priority,  # P1 first
    InterventionTicket.created_at.desc(),
)
```

- **Files**:
  - `backend/api/routes_alerts.py` — Add ticket endpoints
  - `backend/db/models.py` — May need to add `created_at` default if missing
- **Success**:
  - Tickets queryable by status, sorted by priority
  - State transitions enforced (invalid → 400 error with valid options)
  - History array updated on each transition
  - Stats endpoint returns aggregated counts
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 96-135) — Ticket lifecycle state machine
  - #file:../research/20260604-platform-enhancement-research.md (Lines 175-210) — Ingestion auto-creates tickets
- **Dependencies**:
  - Existing `core/ticket_lifecycle.py` (can_transition, transition_ticket)
  - Existing `db/models.py` InterventionTicket model

---

### Task 1.3: Create Backend Student Risk Breakdown Endpoint

Expose the full ABC risk computation for a single student (not just the tier label).

**Add to**: `backend/api/routes_alerts.py`

**Endpoint**: `GET /api/alerts/student-risk/{student_id}`

**Logic**:
1. Fetch all mastery records for student
2. Compute `overall_mastery` average
3. Fetch latest assessment event → extract `cognitive_analysis` JSON (already has gaps)
4. Call `compute_academic_risk()`, `compute_behavioral_risk()`, `compute_cognitive_risk()`
5. Call `compute_composite_risk()` for final tier + factors
6. Return full breakdown

**Response schema**:
```python
class RiskBreakdownResponse(BaseModel):
    student_id: str
    student_name: str
    composite_score: float  # 0-100
    risk_tier: str
    abc_scores: dict  # {academic: 45.0, behavioral: 20.0, cognitive: 60.0}
    contributing_factors: list[str]
    gap_details: list[dict]  # [{kc_id, kc_name, severity, mastery}]
    trend: str
    urgency_rank: int
```

- **Files**:
  - `backend/api/routes_alerts.py` — Add risk breakdown endpoint
- **Success**:
  - Returns full ABC scores (not just tier)
  - Contributing factors explain WHY the risk is what it is
  - Gap details include severity level per KC
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 20-60) — Full risk scoring algorithm
  - #file:../research/20260604-platform-enhancement-research.md (Lines 62-80) — Behavioral risk computation
- **Dependencies**:
  - Task 1.1 (router file exists)

---

### Task 1.4: Create Backend MTSS Plan Endpoint

Compute and return the MTSS intervention plan for a student on-demand.

**Add to**: `backend/api/routes_alerts.py`

**Endpoint**: `GET /api/alerts/student-mtss/{student_id}`

**Logic**:
1. Compute risk (reuse Task 1.3 logic)
2. Fetch gaps from mastery records (mastery < 0.65)
3. Query Neo4j for prerequisite gaps (if driver available)
4. Call existing `build_mtss_plan()` from `core/mtss_engine.py`
5. Return plan with actionable cards

**Response schema**:
```python
class MTSSActionItem(BaseModel):
    action_type: str  # "micro_test", "remedial_content", etc.
    target_kc_id: str
    target_kc_name: str
    priority: int
    description: str
    estimated_sessions: int
    can_dispatch: bool  # True for micro_test (enables 1-click button)

class MTSSPlanResponse(BaseModel):
    student_id: str
    assigned_tier: str  # "tier_1", "tier_2", "tier_3"
    tier_description: str  # Human-readable
    actions: list[MTSSActionItem]
    escalation_note: str | None
    total_estimated_sessions: int
```

- **Files**:
  - `backend/api/routes_alerts.py` — Add MTSS endpoint
- **Success**:
  - Returns tiered plan with prioritized actions
  - Actions with `action_type == "micro_test"` have `can_dispatch: true`
  - Escalation note present for Tier 3 students
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 64-95) — MTSS engine full spec
  - #file:../research/20260604-platform-enhancement-research.md (Lines 100-120) — Action generation per severity
- **Dependencies**:
  - Task 1.3 (risk computation reuse)
  - Existing `core/mtss_engine.py` (build_mtss_plan)

---

### Task 1.5: Build Teacher Alerts Page (`/teacher/alerts`)

Create the primary alert feed page showing all at-risk students with severity, recommendations, and quick-actions.

**New file**: `frontend/src/app/teacher/alerts/page.tsx`

**UI Structure**:
```
┌─────────────────────────────────────────────────────┐
│ ⚠️ Alerts & Early Warnings              [9-A ▼]    │
├─────────────────────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                   │
│ │ 🔴3 │ │ 🟠5 │ │ 🟡8 │ │ 📊16│                   │
│ │Crit │ │High │ │Mod  │ │Total│                   │
│ └─────┘ └─────┘ └─────┘ └─────┘                   │
├─────────────────────────────────────────────────────┤
│ Filter: [All] [Critical] [High] [Declining Trend]   │
├─────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────┐   │
│ │ 🔴 Ravi Kumar (STU-2001)        P1 CRITICAL  │   │
│ │ Composite Risk: 78/100                        │   │
│ │ Factors: ■ Academic Low ■ Deep Prereq Gaps    │   │
│ │ Recommended: Prerequisite review + Micro-test │   │
│ │ [View Details] [Send Quiz] [Create Ticket]    │   │
│ └───────────────────────────────────────────────┘   │
│ ┌───────────────────────────────────────────────┐   │
│ │ 🟠 Priya Sharma (STU-2005)      P2 HIGH      │   │
│ │ Composite Risk: 62/100                        │   │
│ │ Factors: ■ Behavioral Concerns                │   │
│ │ Trend: 📉 Declining (last 3 assessments)      │   │
│ │ [View Details] [Send Quiz] [Schedule Meeting] │   │
│ └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Features**:
- Stat cards at top with animated counters (critical/high/moderate/total)
- Filter tabs by risk tier + "Declining Trend" special filter
- Each alert card shows: student name, risk tier badge, composite score bar, contributing factors as color-coded pills, recommended action text, and quick-action buttons
- "View Details" → navigates to `/teacher/students/[id]`
- "Send Quiz" → opens quiz dispatch modal (Task 1.8)
- "Create Ticket" → creates intervention ticket with pre-filled data
- Cards have severity-colored left border (critical=red, high=orange)
- Critical cards have subtle pulse animation
- Staggered card entrance animations (50ms delay each)

**API calls**: `GET /api/alerts/teacher?class_section=${classSection}`

- **Files**:
  - `frontend/src/app/teacher/alerts/page.tsx` — New page
  - `frontend/src/lib/api.ts` — Add `alertsApi` with `getAlerts()`, `getTickets()`, etc.
- **Success**:
  - Page loads alert feed sorted by urgency
  - Filter buttons work (Critical/High/Declining)
  - Quick-action buttons trigger appropriate actions
  - Animations play on initial load
  - Loading state shows skeleton cards
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 275-310) — Innovation Feature 1 (ABC Radar)
  - #file:../research/20260604-platform-enhancement-research.md (Lines 400-440) — Demo flow minute 2
- **Dependencies**:
  - Task 1.1 (alert endpoint exists)
  - Task 1.3 (risk breakdown available)

---

### Task 1.6: Build Intervention Command Center (`/teacher/interventions`)

Create a Kanban-style board for managing intervention tickets across their lifecycle states.

**New file**: `frontend/src/app/teacher/interventions/page.tsx`

**UI Structure**:
```
┌─────────────────────────────────────────────────────────────────────┐
│ 📋 Intervention Command Center                        [Stats ▼]     │
├─────────────────────────────────────────────────────────────────────┤
│  Open (5)       │ In Progress (3) │ Awaiting (2)   │ Resolved (8)  │
│ ┌─────────────┐ │ ┌─────────────┐ │ ┌────────────┐ │ ┌───────────┐ │
│ │P1 🔴        │ │ │P2 🟠        │ │ │P3 🟡       │ │ │✅ Done    │ │
│ │Ravi Kumar   │ │ │Anita Shah   │ │ │Suresh P    │ │ │Meera K    │ │
│ │Micro Test   │ │ │Remediation  │ │ │Practice    │ │ │Fractions  │ │
│ │KC: Fractions│ │ │KC: Algebra  │ │ │KC: Ratios  │ │ │+12% gain  │ │
│ │[▶ Start]    │ │ │[📝 Evidence]│ │ │[✓ Resolve] │ │ │           │ │
│ └─────────────┘ │ └─────────────┘ │ └────────────┘ │ └───────────┘ │
│ ┌─────────────┐ │                 │                │               │
│ │P2 🟠        │ │                 │                │               │
│ │Kumar S      │ │                 │                │               │
│ │Parent Mtg   │ │                 │                │               │
│ │[▶ Start]    │ │                 │                │               │
│ └─────────────┘ │                 │                │               │
└─────────────────────────────────────────────────────────────────────┘
```

**Features**:
- 4 column Kanban: Open → In Progress → Awaiting Evidence → Resolved
- Each ticket card shows: priority badge (P1-P4 with color), student name, ticket type icon, target KC name, action button for next valid transition
- Click card → expand to show full history timeline
- Action buttons respect state machine (only show valid next states)
- Stats toggle shows: total by status, by priority, avg resolution time
- Resolved tickets show mastery improvement delta (green "+12%")
- Empty columns show helpful text ("No tickets awaiting evidence")

**API calls**:
- `GET /api/alerts/tickets?class_section=9-A&status=open,assigned,in_progress,awaiting_evidence,resolved`
- `PATCH /api/alerts/tickets/{id}/transition` (on button click)

- **Files**:
  - `frontend/src/app/teacher/interventions/page.tsx` — New page
  - `frontend/src/components/interventions/ticket-card.tsx` — Reusable ticket card
  - `frontend/src/components/interventions/ticket-timeline.tsx` — History timeline
- **Success**:
  - Tickets grouped by status in columns
  - Transition buttons work (API call + optimistic UI update)
  - Invalid transitions prevented (button disabled with tooltip)
  - Stats summary visible
  - Responsive (stacks columns on mobile)
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 96-140) — Ticket lifecycle states & transitions
  - #file:../research/20260604-platform-enhancement-research.md (Lines 310-330) — Innovation Feature 3 (Ticket Kanban)
- **Dependencies**:
  - Task 1.2 (ticket endpoints exist)

---

### Task 1.7: Enhance Student Detail Page with Risk Radar + MTSS + Root Cause

Transform the existing student detail page from a simple profile into a comprehensive intervention dashboard.

**Modify**: `frontend/src/app/teacher/students/[id]/page.tsx`

**New sections to ADD (below existing content)**:

**Section A — ABC Risk Radar** (Recharts RadarChart):
```
┌─────────────────────────────┐
│ 🎯 Risk Assessment          │
│                             │
│     Academic (45)           │
│       /    \                │
│      /      \               │
│ Cognitive    Behavioral     │
│   (60)         (20)        │
│                             │
│ Composite: 42/100 [MODERATE]│
│ Factors: ■ Deep Prereq Gaps │
└─────────────────────────────┘
```

**Section B — MTSS Intervention Plan** (Action cards):
```
┌─────────────────────────────────────────┐
│ 🏥 Recommended Interventions (Tier 2)   │
│                                         │
│ ┌─────────────────────┐ ┌────────────┐ │
│ │ 1. Prerequisite     │ │ 2. Micro   │ │
│ │    Review           │ │    Test    │ │
│ │ KC: Linear Eqs     │ │ KC: Quadra.│ │
│ │ Sessions: 2        │ │ Sessions: 1│ │
│ │ [📚 Assign]        │ │ [🎯 Send]  │ │
│ └─────────────────────┘ └────────────┘ │
└─────────────────────────────────────────┘
```

**Section C — Root Cause Flow** (Prerequisite chain):
```
┌───────────────────────────────────────────────────┐
│ 🔍 Root Cause Analysis                            │
│                                                   │
│ [Algebra Expr.] ──→ [Linear Eqs] ──→ [Quadratic] │
│   ✅ 78%              ⚠️ 42%            ❌ 25%    │
│                      ROOT CAUSE                   │
│                                                   │
│ "Student struggles with Quadratics because        │
│  Linear Equations was never fully mastered"       │
└───────────────────────────────────────────────────┘
```

**Section D — Intervention Timeline** (from ticket history):
```
┌────────────────────────────────────┐
│ 📅 Intervention History            │
│                                    │
│ ● Jun 3 — Micro test dispatched    │
│ │  KC: Fractions (scored 3/5)      │
│ ● Jun 1 — Ticket created (P2)     │
│ │  Type: Remediation Plan          │
│ ● May 28 — Risk escalated to HIGH │
│ │  Composite: 55 → 62             │
└────────────────────────────────────┘
```

**API calls**:
- `GET /api/alerts/student-risk/{id}` (ABC scores)
- `GET /api/alerts/student-mtss/{id}` (MTSS plan)
- `GET /api/query/student/{id}/insights` (AI narrative) — ALREADY EXISTS, just not called
- `GET /api/alerts/tickets?student_id={id}` (ticket history)

- **Files**:
  - `frontend/src/app/teacher/students/[id]/page.tsx` — Add new sections
  - `frontend/src/components/student-detail/risk-radar.tsx` — ABC radar component
  - `frontend/src/components/student-detail/mtss-actions.tsx` — MTSS action cards
  - `frontend/src/components/student-detail/root-cause-flow.tsx` — Prerequisite chain
  - `frontend/src/components/student-detail/intervention-timeline.tsx` — History timeline
- **Success**:
  - ABC Radar chart renders with 3 axes (Academic, Behavioral, Cognitive)
  - MTSS actions are clickable (micro-test dispatches, others create tickets)
  - Root cause flow shows prerequisite chain with mastery at each node
  - Timeline shows chronological intervention history
  - All sections load independently (parallel API calls)
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 275-295) — ABC Radar spec
  - #file:../research/20260604-platform-enhancement-research.md (Lines 296-330) — Smart Interventions spec
  - #file:../research/20260604-platform-enhancement-research.md (Lines 330-360) — Root Cause Explorer spec
- **Dependencies**:
  - Task 1.3 (risk endpoint)
  - Task 1.4 (MTSS endpoint)
  - Task 1.2 (tickets endpoint for history)

---

### Task 1.8: Add Quiz Dispatch Capability

Add a modal that lets teachers send a targeted micro-test to a student with 1 click.

**New component**: `frontend/src/components/quiz/dispatch-modal.tsx`

**UI**:
```
┌─────────────────────────────────────┐
│ 🎯 Send Micro-Test to Ravi Kumar   │
│                                     │
│ Target Knowledge Components:        │
│ ☑ Fractions (mastery: 35%)         │
│ ☑ Decimal Operations (mastery: 42%)│
│ ☐ Linear Equations (mastery: 68%)  │
│                                     │
│ Questions: [5 ▼]                    │
│                                     │
│ Delivery: ● WebSocket (real-time)   │
│                                     │
│ [Cancel]              [🚀 Dispatch] │
└─────────────────────────────────────┘
```

**Features**:
- Pre-selects KCs where mastery < 0.65 (student's gaps)
- Teacher can toggle KCs on/off
- Number of questions selector (3, 5, 8, 10)
- On dispatch: calls `POST /api/quiz/dispatch` (ALREADY EXISTS)
- Success toast: "Quiz sent to Ravi! They'll receive it in real-time."
- If WebSocket not available, shows "Quiz queued for next login"

**API call**: `POST /api/quiz/dispatch` with `{ student_id, target_kc_ids, num_questions }`

- **Files**:
  - `frontend/src/components/quiz/dispatch-modal.tsx` — New modal component
  - Integration points: alerts page (Task 1.5), student detail (Task 1.7), interventions (Task 1.6)
- **Success**:
  - Modal opens with student's gaps pre-selected
  - Dispatch call succeeds and returns session ID
  - Toast confirms delivery method
  - Student quiz page receives quiz via WebSocket (already implemented)
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 360-380) — One-Click Micro-Test spec
  - #file:../research/20260604-platform-enhancement-research.md (Lines 170-200) — MCP Quiz Dispatcher pipeline
- **Dependencies**:
  - Existing `POST /api/quiz/dispatch` endpoint (already built)
  - Existing WebSocket quiz delivery (already working)

---

### Task 1.9: Update Sidebar Navigation

Add Alerts and Interventions links with live badge counts to the teacher sidebar.

**Modify**: `frontend/src/components/shared/sidebar.tsx`

**Changes**:
```typescript
import { Bell, ClipboardCheck } from "lucide-react";

const teacherLinks = [
  { href: "/teacher/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/teacher/alerts", label: "Alerts", icon: Bell, badge: true },
  { href: "/teacher/interventions", label: "Interventions", icon: ClipboardCheck },
  { href: "/teacher/input", label: "Input Data", icon: Upload },
  { href: "/teacher/students", label: "Students", icon: Users },
  { href: "/teacher/knowledge-graph", label: "Knowledge Graph", icon: Network },
  { href: "/teacher/query", label: "AI Query", icon: MessageSquare },
];
```

**Badge behavior**: The Alerts link shows a red badge with count of CRITICAL+HIGH alerts. Fetched on sidebar mount, refreshed every 60 seconds.

- **Files**:
  - `frontend/src/components/shared/sidebar.tsx` — Update teacherLinks, add badge logic
  - `frontend/src/lib/api.ts` — Add alertsApi functions
- **Success**:
  - Sidebar shows "Alerts" with red badge count
  - "Interventions" link appears between Alerts and Input Data
  - Badge updates without page refresh (polling or WebSocket)
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 375-395) — Sidebar enhancement spec
- **Dependencies**:
  - Task 1.1 (alert endpoint for badge count)

---

## Phase 2: AI Intelligence Layer

### Task 2.1: Integrate AI Insights on Student Detail Page

Call the EXISTING but UNUSED `/query/student/{id}/insights` endpoint and display it as an AI-generated narrative card.

**Add to**: `frontend/src/app/teacher/students/[id]/page.tsx`

**UI**:
```
┌─────────────────────────────────────────────┐
│ ✨ AI Insights                    [Refresh] │
│                                             │
│ "Ravi shows a declining pattern in algebra  │
│  topics over the last 3 assessments. His    │
│  strongest area is Geometry (85% mastery).  │
│  Priority focus should be on Fractions and  │
│  Linear Equations which are prerequisites   │
│  for upcoming Quadratics unit."             │
│                                             │
│ 🎯 Gaps: Fractions, Linear Eqs             │
│ ⭐ Strengths: Geometry, Statistics          │
│ 📈 Trend: Declining                         │
└─────────────────────────────────────────────┘
```

**API call**: `GET /api/query/student/{id}/insights` — ALREADY EXISTS in backend + API client

- **Files**:
  - `frontend/src/app/teacher/students/[id]/page.tsx` — Add AI insights section
  - `frontend/src/components/student-detail/ai-insights.tsx` — AI insight card component
- **Success**:
  - Insights card renders with narrative text
  - Gaps and strengths shown as tagged pills
  - Refresh button re-fetches
  - Loading state shows skeleton text lines
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 195-215) — routes_query.py /student/{id}/insights
- **Dependencies**:
  - Existing endpoint (no backend work needed)

---

### Task 2.2: Add Class Patterns Section to Teacher Dashboard

Call the EXISTING but UNUSED `/query/class/{section}/patterns` endpoint and show it prominently on the dashboard.

**Modify**: `frontend/src/app/teacher/dashboard/page.tsx`

**New section** (below stat cards):
```
┌──────────────────────────────────────────────────┐
│ 🧠 AI Class Insights                            │
│                                                  │
│ "Class 9-A has 5 students below 50% mastery in  │
│  Fractions. This is a systemic gap — consider   │
│  a class-wide revision session before the next  │
│  unit on Ratios which depends on Fractions."    │
│                                                  │
│ Struggling KCs:                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│ │❌ Fractions │ │⚠️ Linear Eq │ │⚠️ Decimals │ │
│ │  38% avg   │ │  52% avg   │ │  55% avg   │ │
│ │  8 students │ │  5 students │ │  4 students│ │
│ └─────────────┘ └─────────────┘ └────────────┘ │
└──────────────────────────────────────────────────┘
```

**API call**: `GET /api/query/class/{section}/patterns` — ALREADY EXISTS

- **Files**:
  - `frontend/src/app/teacher/dashboard/page.tsx` — Add class patterns section
- **Success**:
  - Class patterns displayed with struggling KC cards
  - Each KC card shows severity color, average mastery, affected student count
  - Links to student list filtered by that KC gap
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 200-215) — Class patterns endpoint spec
- **Dependencies**:
  - Existing endpoint (no backend work needed)

---

### Task 2.3: Enhance AI Query Page

Transform the basic query input into a full AI assistant experience.

**Modify**: `frontend/src/app/teacher/query/page.tsx`

**Enhancements**:
1. Smart suggestions based on current class state (generated from struggling KCs)
2. Rich result cards with data tables (not just text answers)
3. Cypher query display (collapsible, for transparency)
4. Confidence score indicator
5. Follow-up question suggestions after each answer

**New suggestions** (dynamic, computed from class data):
- "Which students need prerequisite review for [weakest KC]?"
- "Show me students whose mastery declined this week"
- "Who has the most intervention tickets open?"
- "What's the root cause of [weakest KC] gaps?"

- **Files**:
  - `frontend/src/app/teacher/query/page.tsx` — Enhance with rich results
- **Success**:
  - Results show structured data tables when available
  - Confidence indicator (high/medium/low)
  - Suggested follow-up questions appear after each answer
  - Cypher query viewable in collapsed section
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 145-175) — NL-to-Cypher pipeline
- **Dependencies**:
  - Existing `/query/ask` endpoint (working)

---

### Task 2.4: AI-Generated Intervention Recommendations

Add Gemini-powered recommendation text to MTSS action cards that explain WHY each action was chosen.

**Modify**: Backend MTSS endpoint (Task 1.4 response) to include AI-generated `reasoning` field.

**New endpoint enhancement**: After `build_mtss_plan()`, call Gemini with a prompt:
```
"Given student {name} with mastery gaps in {gaps} and risk factors {factors}, 
explain in 1-2 sentences why {action_type} targeting {kc_name} is the recommended next step."
```

- **Files**:
  - `backend/api/routes_alerts.py` — Add Gemini call to MTSS endpoint
  - `frontend/src/components/student-detail/mtss-actions.tsx` — Display reasoning text
- **Success**:
  - Each MTSS action card shows a brief AI explanation
  - Graceful fallback to static text if Gemini unavailable
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 64-95) — MTSS engine spec
- **Dependencies**:
  - Task 1.4 (MTSS endpoint)
  - Existing `llm/gemini_client.py`

---

## Phase 3: Admin Decision Support

### Task 3.1: Create Backend Admin Analytics Endpoints

Build comprehensive endpoints for school-wide decision support.

**New file**: `backend/api/routes_admin_analytics.py`

**Endpoints**:

```python
# Risk heatmap: section × subject matrix
GET /api/admin/analytics/risk-heatmap
Response: { sections: ["9-A", "9-B"], subjects: ["math", "science"],
            matrix: [[{avg_risk: 45, critical_count: 2}, ...], ...] }

# Section comparison
GET /api/admin/analytics/section-comparison
Response: { sections: [{name, avg_mastery, total_students, risk_dist, top_gaps}] }

# Intervention effectiveness
GET /api/admin/analytics/effectiveness
Response: { by_type: [{type, created, resolved, avg_days, avg_mastery_improvement}],
            overall_resolution_rate: 0.72, avg_time_to_resolve_days: 4.5 }

# Teacher workload
GET /api/admin/analytics/teacher-workload
Response: { teachers: [{teacher_id, name, open_tickets, students, avg_risk}] }
```

**Logic for effectiveness**:
- For each resolved ticket: compare student mastery on `target_kc_id` BEFORE ticket creation vs AFTER resolution
- Group by intervention type → compute average improvement per type

- **Files**:
  - `backend/api/routes_admin_analytics.py` — New router
  - `backend/main.py` — Register at `/api/admin/analytics`
- **Success**:
  - Risk heatmap shows section × subject risk matrix
  - Effectiveness shows which intervention types yield best mastery improvement
  - Teacher workload shows ticket distribution
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 220-260) — Gap analysis showing admin data needs
- **Dependencies**:
  - Existing `InterventionTicket` model with data from ingestion pipeline

---

### Task 3.2: Build Admin Analytics Page (`/admin/analytics`)

Create the school-wide decision support dashboard.

**New file**: `frontend/src/app/admin/analytics/page.tsx`

**UI Structure**:
```
┌─────────────────────────────────────────────────────────┐
│ 📊 School Analytics                                     │
├──────────────────────────────┬──────────────────────────┤
│ Risk Heatmap                 │ Section Comparison        │
│ ┌─────┬──────┬────────┐     │                          │
│ │     │ Math │ Sci    │     │ 9-A: ████████ 62%        │
│ │ 9-A │ 🟡45 │ 🟢28  │     │ 9-B: ██████ 55%          │
│ │ 9-B │ 🟠58 │ 🟡42  │     │ 9-C: █████████ 71%       │
│ └─────┴──────┴────────┘     │                          │
├──────────────────────────────┴──────────────────────────┤
│ Intervention Effectiveness                               │
│                                                         │
│ Micro-Test:     ████████████░░ +15% mastery gain        │
│ Remediation:    ██████████░░░░ +12% mastery gain        │
│ Peer Tutoring:  ████████░░░░░░ +9% mastery gain         │
│ Parent Meeting: ██████░░░░░░░░ +6% mastery gain         │
├─────────────────────────────────────────────────────────┤
│ Teacher Workload                                         │
│ ┌──────────────────────────────┐                        │
│ │ Teacher A: 12 tickets (3 P1) │                        │
│ │ Teacher B: 8 tickets (1 P1)  │                        │
│ └──────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

- **Files**:
  - `frontend/src/app/admin/analytics/page.tsx` — New page
  - `frontend/src/lib/api.ts` — Add `adminAnalyticsApi`
- **Success**:
  - Heatmap renders with color-coded risk cells
  - Section comparison shows horizontal bars
  - Effectiveness chart shows mastery improvement per intervention type
  - Teacher workload visible with priority breakdown
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 220-260) — Admin needs
- **Dependencies**:
  - Task 3.1 (admin endpoints)

---

### Task 3.3: Add Intervention Effectiveness Dashboard

Enhance the admin analytics with a detailed effectiveness view showing causal connection between interventions and outcomes.

**UI** (embedded in Task 3.2 page, or expandable section):
- Bar chart: intervention type → average mastery improvement
- Funnel chart: Created → Assigned → In Progress → Resolved → Confirmed Improvement
- Metric cards: Resolution rate, Avg time to resolve, Best-performing intervention type
- Timeline: Show intervention volume over last 30 days

- **Files**:
  - `frontend/src/app/admin/analytics/page.tsx` — Effectiveness section
- **Success**:
  - Clear visualization of which interventions are most effective
  - Admin can identify if micro-tests or remediation yield better results
  - Data-driven decision support for resource allocation
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 310-330) — Closed-loop tracking
- **Dependencies**:
  - Task 3.1 (effectiveness endpoint)
  - Task 3.2 (page exists)

---

### Task 3.4: Enhance Admin Overview

Add alert summary, intervention stats, and teacher workload to the existing admin dashboard.

**Modify**: `frontend/src/app/admin/dashboard/page.tsx`

**Add**:
- Alert summary card (total critical across all sections)
- Intervention resolution rate card
- "Sections needing attention" list (sections with > 3 critical students)
- Quick links to analytics sub-views

- **Files**:
  - `frontend/src/app/admin/dashboard/page.tsx` — Add new stat cards and links
- **Success**:
  - Admin sees at-a-glance: total students at risk, resolution rate, sections to watch
  - Links navigate to detailed analytics
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 220-260) — Admin data needs
- **Dependencies**:
  - Task 3.1 (endpoints for data)

---

## Phase 4: Student Empowerment & Self-Paced Learning

### Task 4.1: Build Student Goals & Progress Page (`/student/goals`)

Create a motivational goal-tracking page that makes learning progress visible and rewarding.

**New file**: `frontend/src/app/student/goals/page.tsx`

**UI Structure**:
```
┌─────────────────────────────────────────────────────┐
│ 🎯 My Learning Goals                               │
├─────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐     │
│ │ 🔥 Current Streak: 5 days                   │     │
│ │ ████████████████████░░░░░░░░ 62% overall    │     │
│ └─────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────┤
│ Knowledge Components:                               │
│                                                     │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐         │
│ │⭐ ADVANCED│ │✅ PROFICNT│ │📝 BASIC   │         │
│ │ Geometry  │ │ Statistics│ │ Fractions │         │
│ │ 87%       │ │ 72%       │ │ 42%       │         │
│ │ 🏅        │ │ 🎖️        │ │ → Practice│         │
│ └───────────┘ └───────────┘ └───────────┘         │
│                                                     │
│ ┌───────────┐ ┌───────────┐                        │
│ │⚠️ BELOW   │ │❌ NOT YET │                        │
│ │ Decimals  │ │ Quadratic │                        │
│ │ 35%       │ │ 0%        │                        │
│ │ → Practice│ │ Locked 🔒 │                        │
│ └───────────┘ └───────────┘                        │
├─────────────────────────────────────────────────────┤
│ 🏆 Badges Earned: 3/10                             │
│ [🏅 First Quiz] [🎖️ 3-Day Streak] [⭐ Mastered 1]│
└─────────────────────────────────────────────────────┘
```

**Features**:
- Overall progress bar with animated fill
- KC cards with mastery level badges (color-coded)
- "Practice" button on below-proficiency KCs → triggers quiz (Task 4.2)
- Streak counter (consecutive days with activity)
- Badge collection (milestone achievements)
- Locked KCs (prerequisites not met) with tooltip explaining why

**Data source**: `GET /api/dashboard/student/mastery` (existing endpoint)

- **Files**:
  - `frontend/src/app/student/goals/page.tsx` — New page
  - `frontend/src/components/student/mastery-card.tsx` — KC mastery card with level badge
  - `frontend/src/components/student/badge-collection.tsx` — Achievement badges
- **Success**:
  - All KCs displayed with correct mastery level and color
  - Practice buttons link to quiz dispatch
  - Streak counter works (based on assessment event dates)
  - Badges award for milestones (first quiz, streak, mastery level up)
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 380-395) — Student empowerment spec
- **Dependencies**:
  - Existing student mastery endpoint

---

### Task 4.2: Add Practice Mode (Self-Triggered Quiz)

Allow students to request a practice quiz targeting their weak KCs.

**New endpoint**: `POST /api/quiz/practice` (student-initiated, targets own gaps)

**Logic**:
1. Fetch student's mastery records where mastery < 0.65
2. Auto-select bottom 3 KCs (or specific KCs if provided in body)
3. Call existing `dispatch_micro_test()` with student as target
4. Return quiz session directly (no WebSocket needed — immediate)

**Frontend**: "Practice Now" button on student goals page and dashboard → opens quiz immediately

- **Files**:
  - `backend/api/routes_quiz.py` — Add `/quiz/practice` endpoint
  - `frontend/src/app/student/goals/page.tsx` — Practice button behavior
  - `frontend/src/app/student/quiz/page.tsx` — Handle practice mode entry
- **Success**:
  - Student clicks "Practice" → quiz questions appear immediately
  - Quiz targets student's weakest KCs
  - On completion, mastery updates (existing flow)
  - Goals page reflects new mastery after quiz
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 150-170) — Quiz generator spec
- **Dependencies**:
  - Existing quiz_generator.py + quiz_dispatcher.py

---

### Task 4.3: Enhance Student Dashboard with AI Tips + Intervention Status

Make the student dashboard personalized and actionable.

**Modify**: `frontend/src/app/student/dashboard/page.tsx`

**Add**:
1. AI study tip card (from Gemini): "Focus on Fractions this week — it's a prerequisite for 3 upcoming topics"
2. Active intervention banner: "Your teacher assigned a Remediation Plan for Linear Equations"
3. Next recommended action: "Practice Fractions (3 questions)" button
4. Recent quiz results with mastery delta

- **Files**:
  - `frontend/src/app/student/dashboard/page.tsx` — Add AI tip, intervention banner, recommendation
- **Success**:
  - AI tip appears (call to student insights endpoint)
  - If student has active tickets, banner shows
  - "Practice" button triggers quiz for weakest KC
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 195-215) — Student insights endpoint
- **Dependencies**:
  - Existing endpoints (insights, mastery)

---

### Task 4.4: Add Mastery Level Badges and Streak Tracking

Implement gamification elements that motivate consistent engagement.

**Badge definitions**:
- 🏅 "First Step" — Complete first quiz
- 🎖️ "Streak Starter" — 3 consecutive days with activity
- 🔥 "On Fire" — 7-day streak
- ⭐ "Knowledge Master" — Reach ADVANCED on any KC
- 🎯 "Gap Closer" — Improve a KC from BELOW_BASIC to BASIC
- 💎 "All Proficient" — All KCs at PROFICIENT or above
- 🏆 "Perfect Score" — Score 100% on any quiz

**Streak logic**: Count consecutive days where student has at least 1 assessment event or quiz completion.

**Storage**: Computed from existing `AssessmentEvent` and `QuizSession` timestamps (no new tables needed).

- **Files**:
  - `backend/api/routes_dashboard.py` — Add streak + badge computation to student mastery endpoint
  - `frontend/src/components/student/badge-collection.tsx` — Badge display
- **Success**:
  - Badges compute correctly from existing data
  - Streak counter accurate
  - Visual badge collection on goals page
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 380-395) — Gamification spec
- **Dependencies**:
  - Existing assessment/quiz data

---

## Phase 5: UI Peak Polish & Production Readiness

### Task 5.1: Implement Skeleton Loading States

Replace all spinner loading with shimmer skeleton states.

**Create**: `frontend/src/components/ui/skeleton.tsx`

```tsx
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded bg-gray-200", className)} />;
}

export function CardSkeleton() {
  return (
    <div className="rounded-lg border p-6 space-y-3">
      <Skeleton className="h-4 w-1/3" />
      <Skeleton className="h-8 w-2/3" />
      <Skeleton className="h-3 w-full" />
    </div>
  );
}

export function TableRowSkeleton({ cols = 4 }) { ... }
```

**Apply to**: All pages that currently show spinners (teacher dashboard, student detail, admin, alerts, etc.)

- **Files**:
  - `frontend/src/components/ui/skeleton.tsx` — Skeleton components
  - All page files — Replace spinner with skeleton patterns
- **Success**:
  - No spinning circles anywhere in the app
  - Skeleton shapes match the content they replace
  - Smooth transition from skeleton → real content
- **Dependencies**: None (pure frontend)

---

### Task 5.2: Add Staggered Card Entrance Animations + Animated Counters

Make every page feel alive with motion.

**Card stagger** (CSS-only approach for performance):
```css
.card-stagger > * {
  opacity: 0;
  transform: translateY(16px);
  animation: fadeSlideUp 0.4s ease-out forwards;
}
.card-stagger > *:nth-child(1) { animation-delay: 0ms; }
.card-stagger > *:nth-child(2) { animation-delay: 60ms; }
.card-stagger > *:nth-child(3) { animation-delay: 120ms; }
.card-stagger > *:nth-child(4) { animation-delay: 180ms; }
```

**Animated counter** (React hook):
```tsx
function useAnimatedNumber(target: number, duration = 800) {
  const [value, setValue] = useState(0);
  useEffect(() => { /* requestAnimationFrame interpolation */ }, [target]);
  return value;
}
```

- **Files**:
  - `frontend/src/components/ui/animated-counter.tsx` — Counter component
  - `frontend/src/app/globals.css` — Add stagger keyframes
  - All dashboard pages — Apply `card-stagger` class to grid containers
- **Success**:
  - Stat cards animate in with stagger
  - Numbers count up from 0 to final value
  - Animations complete within 500ms
  - No jank or layout shift
- **Dependencies**: None

---

### Task 5.3: Apply Consistent Severity Color System

Create a unified color mapping for risk/severity/status across the entire app.

**Utility functions** (add to `frontend/src/lib/utils.ts`):
```typescript
export function getSeverityColor(severity: string): string { ... }
export function getRiskColor(tier: string): string { ... }
export function getStatusColor(status: string): string { ... }
export function getMasteryColor(mastery: number): string { ... }
```

**Apply everywhere**: All badges, progress bars, chart colors, card borders use these functions instead of hardcoded colors.

- **Files**:
  - `frontend/src/lib/utils.ts` — Add color utility functions
  - All components using color — Standardize to utility calls
- **Success**:
  - Same risk tier shows same color everywhere
  - No inconsistent color usage
  - Color meaning is always: green=good, yellow=mild, orange=moderate, red=severe/critical
- **Dependencies**: None

---

### Task 5.4: Risk Pulse Animation + Alert Banner

Add attention-drawing animations for critical states.

**Risk pulse**: Critical student cards have a subtle glowing border animation.
```css
.risk-pulse-critical {
  animation: pulse-red 2s ease-in-out infinite;
}
@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
}
```

**Alert banner**: Top-of-page dismissible banner when critical alerts exist.
```
┌─ ⚠️ 3 students require immediate attention ─── [View Alerts] [✕] ─┐
```

- **Files**:
  - `frontend/src/app/globals.css` — Pulse keyframes
  - `frontend/src/components/shared/alert-banner.tsx` — Top banner component
  - `frontend/src/components/shared/app-shell.tsx` — Integrate alert banner
- **Success**:
  - Critical cards pulse softly (not distracting, but noticeable)
  - Alert banner appears when critical alerts exist
  - Banner dismissible per session
  - "View Alerts" navigates to alerts page
- **Dependencies**: Task 1.1 (alert data for banner)

---

### Task 5.5: Mobile-Responsive Bottom Navigation

Add bottom tab navigation for mobile viewports (< 768px).

**UI**: Fixed bottom bar with 4 icon tabs (role-dependent), hides sidebar on mobile.

```
┌──────────────────────────────────────────┐
│ [🏠 Home] [⚠️ Alerts] [📊 Input] [👤 Me]│
└──────────────────────────────────────────┘
```

- **Files**:
  - `frontend/src/components/shared/bottom-nav.tsx` — Mobile bottom nav
  - `frontend/src/components/shared/app-shell.tsx` — Hide sidebar on mobile, show bottom nav
- **Success**:
  - Below 768px: sidebar hidden, bottom nav visible
  - Above 768px: sidebar visible, bottom nav hidden
  - Active tab highlighted
  - Touch-friendly (44px min tap targets)
- **Dependencies**: None

---

### Task 5.6: Enhanced Teacher Dashboard

Bring all Phase 1-2 data into the main dashboard for maximum first-impression impact.

**Modify**: `frontend/src/app/teacher/dashboard/page.tsx`

**Final dashboard layout**:
```
┌─────────────────────────────────────────────────────────┐
│ [Alert Banner: "3 students need attention"]             │
├─────────────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                   │
│ │ 18   │ │ 62%  │ │ 🔴 3 │ │ 📋 7 │                   │
│ │Studts│ │Avg   │ │Alerts│ │Tickets│                   │
│ └──────┘ └──────┘ └──────┘ └──────┘                   │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────┐ ┌────────────────────────┐ │
│ │ Risk Distribution       │ │ 🧠 AI Class Insights   │ │
│ │ [Pie Chart]             │ │ "5 students below 50%  │ │
│ │ Low:8 Mod:5 High:3 Crit:2│ │  in Fractions..."     │ │
│ └─────────────────────────┘ └────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ Struggling Topics (class-wide)                          │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│ │❌ Fract. │ │⚠️ Linear │ │⚠️ Decimal│                │
│ │  38% avg │ │  52% avg │ │  55% avg │                │
│ └──────────┘ └──────────┘ └──────────┘                │
├─────────────────────────────────────────────────────────┤
│ Recent Alerts (top 3)                                   │
│ • 🔴 Ravi Kumar — Critical risk (78/100)              │
│ • 🟠 Priya S — High risk, declining trend             │
│ • 🟠 Kumar M — High risk, behavioral concerns        │
│ [See All Alerts →]                                      │
└─────────────────────────────────────────────────────────┘
```

- **Files**:
  - `frontend/src/app/teacher/dashboard/page.tsx` — Full redesign with all new sections
- **Success**:
  - Dashboard immediately shows alerts + class insights + struggling topics
  - First impression demonstrates all platform capabilities
  - All stat cards have animated counters
  - Staggered entrance animations
  - Risk distribution pie chart with severity colors
- **Research References**:
  - #file:../research/20260604-platform-enhancement-research.md (Lines 400-445) — Demo flow spec
- **Dependencies**:
  - Task 1.1 (alerts data)
  - Task 2.2 (class patterns data)
  - Task 5.2 (animations)
  - Task 5.3 (color system)

---

## Implementation Priority & Dependency Graph

```
Phase 1 (Core — must do first):
  1.1 → 1.2 → 1.3 → 1.4 (backend endpoints, sequential)
  1.5 + 1.6 (parallel, both need 1.1-1.4)
  1.7 (needs 1.3, 1.4)
  1.8 (independent, can parallel)
  1.9 (needs 1.1 for badge count)

Phase 2 (AI layer — can start after 1.1-1.4 done):
  2.1 (independent — existing endpoint)
  2.2 (independent — existing endpoint)
  2.3 (independent — existing endpoint)
  2.4 (needs 1.4)

Phase 3 (Admin — can start after Phase 1 done):
  3.1 → 3.2 → 3.3 → 3.4

Phase 4 (Student — can start anytime, independent):
  4.1 → 4.2 (sequential)
  4.3 (independent)
  4.4 (independent)

Phase 5 (Polish — apply continuously):
  5.1, 5.2, 5.3, 5.4 (can be done in any order)
  5.5 (independent)
  5.6 (needs 1.1, 2.2 — do last)
```

## Challenge Statement Mapping

| Feature | Challenge 1: Learning Gaps | Challenge 2: Decision-Making |
|---|---|---|
| Alert System (1.1, 1.5) | ✅ Timely identification | ✅ Early warning |
| Ticket Kanban (1.2, 1.6) | ✅ Low teacher burden | ✅ Actionability |
| ABC Risk Radar (1.3, 1.7) | ✅ Actionable insights | ✅ Decision support |
| MTSS Actions (1.4, 1.7) | ✅ Actionable, low burden | ✅ Early intervention |
| Quiz Dispatch (1.8) | ✅ Timely feedback | |
| AI Insights (2.1, 2.2) | ✅ Actionable insights | ✅ Decision support |
| NL Query (2.3) | | ✅ Decision support |
| Admin Heatmap (3.2) | | ✅ At-scale visibility |
| Effectiveness (3.3) | | ✅ Evidence-based decisions |
| Student Goals (4.1) | ✅ Student progress | |
| Practice Mode (4.2) | ✅ Self-paced, timely | |
| AI Tips (4.3) | ✅ Actionable for students | |
| Skeleton/Animations (5.x) | ✅ Classroom integration | ✅ Reliability |

## Success Criteria Summary

- **3-Click Intervention**: Teacher sees alert → views student → dispatches action (3 clicks max)
- **10-Second Feedback**: Quiz dispatch → student receives (WebSocket) within 10 seconds
- **Closed Loop**: Detect gap → create ticket → track execution → measure improvement
- **Zero Manual Risk Scoring**: All risk computed automatically from assessment data
- **100% Engine Exposure**: Every `core/` module has a corresponding frontend surface
- **5-Minute Demo**: Complete teacher→student→admin flow demonstrable in 5 minutes
- **Mobile-Ready**: All critical teacher actions possible on phone (bottom nav + responsive)
- **AI Transparency**: NL queries show the Cypher generated, insights cite data sources
