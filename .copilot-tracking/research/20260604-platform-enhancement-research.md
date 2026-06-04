# Task Research Notes: Sahayak 360 — Peak Platform Enhancement ("Goated Edition")

<!-- markdownlint-disable-file -->

## Executive Summary

Sahayak 360 has a **massive untapped backend** — 70%+ of its analytical engines are built, tested, and running in the ingestion pipeline but have **ZERO frontend exposure**. The enhancement strategy is NOT "build new backend logic" but rather **surface the hidden power** through polished, innovative UI/UX that makes judges say "this is production-grade."

**Challenge Statements Addressed:**
1. **Learning Gaps & Timely Feedback** → BKT mastery + real-time WebSocket quizzes + AI-generated interventions
2. **School Decision-Making & Early Intervention** → ABC Risk Scorer + MTSS Engine + Ticket Lifecycle + NL-to-Cypher queries

---

## Part 1: Complete Codebase Architecture Deep-Dive

### 1.1 Backend Core Engines (The Hidden Goldmine)

#### `backend/core/risk_scorer.py` (Lines 1-183) — ABC Early Warning System

**What it does**: Computes multi-dimensional risk using a weighted composite model.

```python
WEIGHTS = {
    "academic": 0.50,   # 50% — mastery + gap severity + declining trend
    "behavioral": 0.25, # 25% — attendance + participation + engagement (swipe)
    "cognitive": 0.25,  # 25% — prerequisite gap depth + bloom regression
}
```

**Academic Risk (0-100)**: `(1.0 - overall_mastery) * 60` + gap severity points (MILD=2, MODERATE=5, SEVERE=10, CRITICAL=15, capped at 30) + trend penalty (10 if declining)

**Behavioral Risk (0-100)**: Attendance (<75% → +40, <85% → +20, <95% → +10) + Participation (ACTIVE=0, PASSIVE=+20, DISENGAGED=+40) + Swipe engagement (<0.3 → +20, <0.5 → +10)

**Cognitive Risk (0-100)**: Prerequisite gap depth × 20 (max 60) + Bloom regression count × 15 (max 40)

**Tier Assignment**:
- `composite >= 75` → CRITICAL
- `composite >= 55` → HIGH
- `composite >= 35` → MODERATE
- `composite < 35` → LOW

**Contributing factors auto-detected**: `academic_performance_low`, `behavioral_concerns`, `deep_prerequisite_gaps`, `critical_gap_present`

**Key types**: `RiskTier(Enum)`, `ABCScores(dataclass)`, `RiskAssessment(dataclass)` with `student_id`, `composite_score`, `tier`, `abc_scores`, `contributing_factors`, `urgency_rank`

**FRONTEND STATUS**: ❌ NOT EXPOSED — only simple `risk_tier` string shown on student cards. The full ABC breakdown, composite score, contributing factors, and urgency rank are never displayed.

---

#### `backend/core/mtss_engine.py` (Lines 1-160) — Multi-Tiered System of Support

**What it does**: Maps risk tiers to intervention tiers and auto-generates prioritized action plans.

**Tier Mapping**:
- `RiskTier.LOW` → `MTSSTier.TIER_1` (Universal — classroom-level)
- `RiskTier.MODERATE` → `MTSSTier.TIER_2` (Targeted — small-group)
- `RiskTier.HIGH` → `MTSSTier.TIER_2` (Targeted — small-group)
- `RiskTier.CRITICAL` → `MTSSTier.TIER_3` (Intensive — individual)

**7 Intervention Types**:
1. `MICRO_TEST` — Quick assessment quiz
2. `REMEDIAL_CONTENT` — Intensive guided learning
3. `PEER_TUTORING` — Collaborative practice
4. `PARENT_MEETING` — Parent-teacher conference
5. `SPECIALIST_REFERRAL` — External support
6. `PREREQUISITE_REVIEW` — Foundational concept revision
7. `EXTENDED_PRACTICE` — Additional drill exercises

**Action Generation Logic**:
- Prerequisite remediations generated FIRST (max 3)
- Per-gap actions mapped by severity:
  - CRITICAL → `REMEDIAL_CONTENT` (3 sessions)
  - SEVERE → `MICRO_TEST` (1 session)
  - MODERATE → `EXTENDED_PRACTICE` (2 sessions)
  - MILD → `MICRO_TEST` (1 session)
- TIER_3 always gets `PARENT_MEETING` added

**Output**: `MTSSPlan` with `student_id`, `assigned_tier`, `risk_assessment`, `actions[]`, `escalation_note`

**FRONTEND STATUS**: ❌ NOT EXPOSED — Interventions are generated and stored during ingestion but teachers never see them.

---

#### `backend/core/ticket_lifecycle.py` (Lines 1-140) — Intervention Ticket State Machine

**What it does**: Industrial-grade ticket management for tracking intervention actions from creation to resolution.

**7 States**: `OPEN → ASSIGNED → IN_PROGRESS → AWAITING_EVIDENCE → RESOLVED → ESCALATED → CLOSED`

**Valid Transitions**:
```python
VALID_TRANSITIONS = {
    OPEN: {ASSIGNED, ESCALATED, CLOSED},
    ASSIGNED: {IN_PROGRESS, ESCALATED, CLOSED},
    IN_PROGRESS: {AWAITING_EVIDENCE, RESOLVED, ESCALATED},
    AWAITING_EVIDENCE: {IN_PROGRESS, RESOLVED, ESCALATED},
    RESOLVED: {CLOSED, IN_PROGRESS},  # can reopen!
    ESCALATED: {ASSIGNED, CLOSED},
    CLOSED: set(),  # terminal
}
```

**Priority Levels**: P1 (same day), P2 (within 2 days), P3 (within 1 week), P4 (scheduled review)

**Ticket Types**: `MICRO_TEST_DISPATCH`, `REMEDIATION_PLAN`, `PARENT_MEETING`, `SPECIALIST_REFERRAL`, `PROGRESS_CHECK`

**Features**: History tracking (`TicketEvent` with timestamp, from→to status, actor, note), auto-resolution timestamping, invalid transition ValueError

**FRONTEND STATUS**: ❌ NOT EXPOSED — DB model `InterventionTicket` is written to during ingestion but there is ZERO UI to view, manage, or transition tickets.

---

#### `backend/core/mastery_updater.py` (Lines 1-120) — Bayesian Knowledge Tracing

**What it does**: Probabilistic mastery estimation using the BKT algorithm from learning science research.

**BKT Parameters**:
```python
DEFAULT_BKT = BKTParams(
    p_learn=0.10,   # probability of learning per opportunity
    p_guess=0.20,   # probability of guessing correctly
    p_slip=0.10,    # probability of slipping (knowing but wrong)
    p_transit=0.10, # transition probability after observation
)
```

**Update Algorithm**:
- If correct: `P(L|correct) = P(correct|L) × P(L) / P(correct)` where `P(correct|L) = 1 - p_slip`
- If incorrect: `P(L|incorrect) = P(incorrect|L) × P(L) / P(incorrect)` where `P(incorrect|L) = p_slip`
- After observation: `posterior = posterior + (1 - posterior) × p_transit`

**Partial Credit Handling** (innovative):
- Score ≥ 80% → treat as correct
- Score ≤ 40% → treat as incorrect
- 40-80% → weighted average of both update paths: `pct × P(correct_update) + (1-pct) × P(incorrect_update)`

**Output**: `MasteryUpdate` with `kc_id`, `prior_mastery`, `posterior_mastery`, `delta`, `new_level`, `evidence`

**FRONTEND STATUS**: ⚠️ RUNNING in pipeline but frontend shows simple mastery % — never shows the probabilistic nature, confidence intervals, or the learning-over-time curve that BKT enables.

---

#### `backend/core/threshold_evaluator.py` (Lines 1-120) — Gap Severity Engine

**What it does**: Classifies mastery gaps into actionable severity levels with auto-recommendations.

**Threshold Configuration**:
```python
ThresholdConfig(
    mastery_threshold=0.65,    # proficiency target
    proficiency_threshold=0.85, # advanced target
    critical_threshold=0.30,    # emergency level
    severe_threshold=0.40,
    moderate_threshold=0.55,
)
```

**Severity Classification**: `NONE (≥0.65)` → `MILD (≥0.55)` → `MODERATE (≥0.40)` → `SEVERE (≥0.30)` → `CRITICAL (<0.30)`

**Auto-Recommendations Generated Per Gap**:
- NONE: "On track, continue practice"
- MILD: "Minor gap — targeted practice needed"
- MODERATE: "Moderate gap — focused intervention required"
- SEVERE: "Severe gap — immediate remediation needed"
- CRITICAL: "Critical gap — prerequisite review + intensive support"

**Intervention Trigger Rule**: `needs_intervention()` = TRUE if ≥1 SEVERE/CRITICAL gap OR ≥3 gaps total

**FRONTEND STATUS**: ❌ NOT EXPOSED — Frontend shows mastery as a plain percentage bar. Severity labels, color-coded badges, and recommendations are never displayed.

---

#### `backend/core/knowledge_dag.py` (Lines 1-140) — Prerequisite Chain Analysis

**What it does**: Neo4j-backed DAG for prerequisite relationships, root-cause gap analysis, and mastery propagation.

**Mastery Levels**: `NOT_ATTEMPTED (<0.01)` → `BELOW_BASIC (<0.40)` → `BASIC (<0.65)` → `PROFICIENT (<0.85)` → `ADVANCED (≥0.85)`

**Root Cause Algorithm** (`propagate_gap_upstream`):
- Walks UP the prerequisite DAG from failed KC (max depth 3)
- Identifies unmastered prerequisites (mastery < 0.65) along the path
- Returns ordered remediation path (deepest cause FIRST)
- This means if a student fails Quadratics, the system traces back to check if they failed Linear Equations, then further back to Algebraic Expressions

**Neo4j Cypher Queries Built-In**:
- `CYPHER_UPSERT_KC` — Create/update knowledge components
- `CYPHER_UPSERT_MASTERY` — Student→KC mastery relationships
- `CYPHER_ADD_PREREQUISITE` — KC→KC prerequisite edges
- `CYPHER_GET_STUDENT_GAPS` — All KCs below threshold for a student
- `CYPHER_GET_PREREQUISITE_CHAIN` — Walk prerequisite path (1..3 hops)

**FRONTEND STATUS**: ⚠️ Knowledge graph page EXISTS and renders nodes, but does NOT show prerequisite chains, root-cause analysis, or remediation paths. It's purely visual, not actionable.

---

#### `backend/core/ast_schema.py` (Lines 1-200) — Universal Assessment Schema

**What it does**: Frozen contract (v2.0) that ALL data entering the system MUST conform to.

**6 Ingestion Channels**: `SWIPE_PWA`, `VISION_SCAN`, `FREETEXT`, `VOICE`, `PET_TRACKER`, `PARENT_FEEDBACK`

**Multi-Dimensional Data Model**:
- `AcademicPayload` — assessment type, scores, per-KC items
- `PETPayload` — Physical Education & Training (athletic rating, activity tags)
- `BehavioralPayload` — attendance streak, participation rating, swipe engagement indicator
- `ParentalPayload` — sentiment, concern tags, raw notes
- `ValidationResult` — sum-check, anomaly flags, discrepancy detection

**Key Insight**: The schema supports VOICE and PARENT_FEEDBACK channels that aren't implemented yet — future extensibility built-in.

---

### 1.2 AI/LLM Layer

#### `backend/llm/gemini_client.py` — Gemini 2.5 Flash Interface

Three modes: `generate_text()`, `generate_with_image()`, `generate_json()`

#### `backend/llm/quiz_generator.py` (Lines 1-80) — Adaptive Quiz Generation

- Takes target KC IDs + current mastery levels
- Calibrates difficulty based on mastery (low mastery = easier questions)
- Returns `QuizQuestion` objects with `bloom_level` and `difficulty` metadata
- Graceful fallback to template questions if Gemini fails
- Pads with fallback if Gemini returns fewer than requested

#### `backend/llm/nl_to_cypher.py` (Lines 1-110) — Natural Language Querying

- Converts teacher questions → Cypher queries → executes on Neo4j
- **Safety validation**: Blocks ALL write operations (CREATE, MERGE, DELETE, SET, etc.)
- Full pipeline: NL → Gemini → Cypher → Neo4j → Records → Formatted answer
- Results limited to 50 records for safety

#### `backend/llm/freetext_parser.py` — Natural Language Score Entry

- Teacher types "Ravi scored 8/10 in fractions" → Gemini parses → AST
- Handles multiple students in one sentence
- Extracts KC mapping, scores, and metadata

---

### 1.3 MCP Quiz Dispatcher (`backend/mcp/quiz_dispatcher.py`, Lines 1-150)

**Full Pipeline**:
1. Fetch student context (mastery state + prerequisites from Neo4j)
2. Generate questions (Gemini with difficulty calibration OR fallback templates)
3. Create QuizSession in PostgreSQL (status: "pending")
4. Dispatch via WebSocket to student (if online) → status becomes "active"
5. HTTP fallback if WebSocket unavailable

**Scoring**: Compares responses to `correct_answer`, computes per-KC mastery deltas, updates records

**WebSocket delivery format**:
```json
{
  "type": "quiz_dispatch",
  "session_id": "QZ-XXXXXXXX",
  "questions": [...],  // student-facing (no answers)
  "time_limit_seconds": 600,
  "teacher_id": "TCH-001"
}
```

---

### 1.4 Ingestion Orchestrator (`backend/services/ingestion_orchestrator.py`, Lines 1-250)

**THE 10-STEP PIPELINE** (executed on EVERY assessment event):

```
Step 1:  Route → Rehydration Governor (fast/slow/vision lane)
Step 2:  Validate → Pandas cross-field validation
Step 3:  Gaps → Threshold evaluation (severity classification)
Step 4:  Mastery → BKT update (prior → posterior)
Step 5:  Risk → ABC composite scoring
Step 6:  MTSS → Build intervention plan (if needed)
Step 7:  Tickets → Auto-create intervention tickets (max 5 per event)
Step 8:  Persist → Assessment event to PostgreSQL
Step 9:  Mastery Records → Upsert per-KC mastery
Step 10: Neo4j Sync → Update knowledge graph (graceful failure)
```

**This means**: Every time a teacher enters a score, the system AUTOMATICALLY:
- Detects gaps with severity
- Updates mastery probabilities
- Computes multi-dimensional risk
- Generates intervention plans
- Creates prioritized tickets
- Syncs the knowledge graph

**FRONTEND STATUS**: ❌ The teacher enters data and gets back a simple "accepted" response. They NEVER see the risk computation, the MTSS plan, or the auto-created tickets.

---

### 1.5 Dashboard Analytics Service (`backend/services/dashboard_analytics.py`, Lines 1-200)

**Class Analytics** (already exposed via `/dashboard/teacher/overview`):
- `total_students`, `class_avg_mastery`, `risk_distribution`, `struggling_kcs[]`, `recent_events`, `open_tickets`

**Student Profile** (already exposed via `/dashboard/teacher/student-detail/{id}`):
- `overall_mastery`, `trend` (improving/stable/declining), `gaps[]`, `strengths[]`, `assessment_count`, `timeline[]`, `radar_data[]`

**What's NOT exposed**: The `open_tickets` count is shown but individual tickets are NOT queryable from frontend.

---

### 1.6 API Endpoints (All Routes)

| Route | Method | Purpose | Frontend Usage |
|---|---|---|---|
| `/api/auth/login` | POST | JWT login | ✅ Used |
| `/api/auth/register` | POST | User registration | ✅ Used |
| `/api/auth/me` | GET | Profile fetch | ✅ Used |
| `/api/ingest/structured` | POST | Structured score entry | ✅ Used |
| `/api/ingest/freetext` | POST | NL score entry | ✅ Used |
| `/api/ingest/vision` | POST | Image → scores | ✅ Used |
| `/api/dashboard/teacher/overview` | GET | Class analytics | ✅ Used |
| `/api/dashboard/teacher/students` | GET | Student list | ✅ Used |
| `/api/dashboard/teacher/student-detail/{id}` | GET | Student profile | ✅ Used |
| `/api/dashboard/student/mastery` | GET | Student self-mastery | ✅ Used |
| `/api/dashboard/student/analytics` | GET | Student charts | ✅ Used |
| `/api/dashboard/admin/overview` | GET | Admin stats | ✅ Used |
| `/api/query/ask` | POST | NL → Cypher → answer | ✅ Used (basic) |
| `/api/query/student/{id}/insights` | GET | AI student insights | ❌ NOT used |
| `/api/query/class/{section}/patterns` | GET | Class pattern detection | ❌ NOT used |
| `/api/quiz/dispatch` | POST | Teacher dispatches quiz | ❌ NOT used (no UI) |
| `/api/quiz/submit` | POST | Student submits quiz | ✅ Used |
| `/api/quiz/{id}` | GET | Get quiz session | ✅ Used |
| `/api/ws/student` | WebSocket | Real-time notifications | ✅ Used (quiz page) |

---

### 1.7 Frontend Current State

**Sidebar Navigation** (`frontend/src/components/shared/sidebar.tsx`):
```
Teacher: Dashboard | Input Data | Students | Knowledge Graph | AI Query
Student: My Progress | Analytics | Quizzes
Admin: Overview | Teachers
```

**Frontend API Client** (`frontend/src/lib/api.ts`):
- `authApi`: login, register, getProfile
- `ingestApi`: structured, freetext, vision
- `dashboardApi`: teacherOverview, studentList, studentDetail, studentMastery, studentAnalytics, adminOverview
- `queryApi`: ask, studentInsights, classPatterns
- `quizApi`: dispatch, submit, getSession

**Key Observation**: `queryApi.studentInsights()` and `queryApi.classPatterns()` are DEFINED in the API client but NEVER CALLED anywhere in the frontend components.

---

### 1.8 Database Models (`backend/db/models.py`)

| Model | Key Fields | Records |
|---|---|---|
| `User` | user_id, email, full_name, role, class_section, institution_id, department_id | ~23 (3 teachers, 18 students, 2 admins) |
| `AssessmentEvent` | event_id, student_id, teacher_id, subject, channel, items(JSON), cognitive_analysis(JSON), behavioral_data(JSON) | ~106 events |
| `MasteryRecord` | student_id, kc_id, kc_name, mastery(float), mastery_level, attempts | ~180 records (18 students × 10 KCs) |
| `InterventionTicket` | ticket_id, student_id, teacher_id, ticket_type, priority, status, target_kc_id, description, history(JSON) | Auto-generated during ingestion |
| `QuizSession` | session_id, student_id, teacher_id, ticket_id, target_kc_ids(JSON), questions(JSON), responses(JSON), score | From quiz dispatches |

---

## Part 2: Gap Analysis — What's Built vs What's Shown

### 2.1 The Critical Frontend-Backend Mismatch

| Backend Engine | Processing Status | Frontend Exposure | Impact if Surfaced |
|---|---|---|---|
| **ABC Risk Scorer** | ✅ Runs every ingest | ❌ Only tier label shown | Teachers see multi-dimensional risk radar → instant prioritization |
| **MTSS Engine** | ✅ Auto-generates plans | ❌ Never shown | Teachers get AI intervention plans → 1-click action |
| **Ticket Lifecycle** | ✅ Tickets auto-created | ❌ No management UI | Full Kanban workflow → track outcomes, measure effectiveness |
| **BKT Mastery** | ✅ Bayesian updates | ⚠️ Shown as simple % | Mastery confidence visualization → proper learning curves |
| **Gap Severity** | ✅ Classified every event | ❌ Only mastery % | Color-coded severity badges → instant gap identification |
| **Prerequisite Chains** | ✅ DAG traversal | ⚠️ Graph renders | Root-cause flow → "why" behind gaps, not just "what" |
| **AI Student Insights** | ✅ Endpoint ready | ❌ Never called | Personalized AI narratives on student pages |
| **AI Class Patterns** | ✅ Endpoint ready | ❌ Never called | Dashboard-level AI insights → proactive teaching |
| **Quiz Dispatch (Teacher-side)** | ✅ Full MCP pipeline | ❌ No dispatch UI | Teacher sends targeted micro-test → real-time to student |
| **Contributing Factors** | ✅ Auto-detected | ❌ Never shown | Explainable AI → teacher understands WHY risk is high |

### 2.2 Innovation Potential Score

**Already Built (just needs UI)**: 8/10 features
**Needs New Backend Work**: 2/10 features (parent portal, effectiveness tracking)
**Estimated Frontend Effort**: 3-5 new pages + enhancements to 4 existing pages

---

## Part 3: Innovation Strategy — "Goated" Differentiators

### 3.1 Judge-Winning Features (Unique to Sahayak 360)

#### 🏆 Feature 1: "ABC Risk Radar" — Multi-Dimensional Student Health

**What judges see**: A radar/spider chart showing Academic, Behavioral, and Cognitive risk dimensions with contributing factors explanation. NOT just "this student is at risk" but "this student has deep prerequisite gaps (cognitive=60) combined with declining attendance (behavioral=40)."

**Why it's goated**: No other student EdTech product shows multi-dimensional risk. They all use single-score thresholds. This demonstrates proper Early Warning System methodology used by research institutions.

**Implementation**: Call existing `compute_composite_risk()` → display `ABCScores` as radar + `contributing_factors` as pills.

---

#### 🏆 Feature 2: "Smart Interventions" — AI-Generated Action Plans

**What judges see**: When a teacher views a high-risk student, they see an auto-generated MTSS intervention plan with prioritized actions they can execute in 1 click (dispatch micro-test, schedule parent meeting, assign remedial content).

**Why it's goated**: The system doesn't just DETECT problems — it PRESCRIBES solutions. Teachers don't need to figure out what to do; the AI tells them. This is prescriptive analytics, not just descriptive.

**Implementation**: Surface existing `MTSSPlan.actions[]` → clickable cards → each triggers the appropriate API action.

---

#### 🏆 Feature 3: "Intervention Command Center" — Ticket Kanban Board

**What judges see**: A full Kanban-style board showing intervention tickets across states (Open, In Progress, Awaiting Evidence, Resolved). Teachers drag tickets between columns. Each ticket links back to the student and KC it targets.

**Why it's goated**: Shows that the platform doesn't just create recommendations — it TRACKS whether they were executed and whether they WORKED. This is the "closed loop" that makes early warning systems actually effective.

**Implementation**: New API endpoint to query tickets by status + frontend Kanban UI + state transition calls.

---

#### 🏆 Feature 4: "Root Cause Explorer" — Prerequisite Chain Visualization

**What judges see**: When a student has a gap in "Quadratic Equations," the UI shows a visual flow: "Quadratic Equations ← Linear Equations ← Algebraic Expressions" with mastery levels at each node. The DEEPEST unmastered node is highlighted as the ROOT CAUSE.

**Why it's goated**: This demonstrates causal reasoning. Instead of "student failed quadratics," the insight is "student failed quadratics BECAUSE they never mastered linear equations." This changes the intervention from "practice more quadratics" to "go back to linear equations first."

**Implementation**: Call existing `propagate_gap_upstream()` → render as a horizontal flow diagram on student detail page.

---

#### 🏆 Feature 5: "AI Teaching Assistant" — Context-Aware NL Queries

**What judges see**: Teacher asks "Why is Ravi struggling this month?" and gets a rich answer combining Neo4j knowledge graph data with Gemini reasoning: "Ravi's mastery in Fractions dropped from 72% to 45% over 3 assessments. Root cause: unmastered prerequisite 'Decimal Operations' (38% mastery). Behavioral signal: attendance dropped to 80%. Recommendation: Prerequisite review followed by micro-test."

**Why it's goated**: This is the holy grail of educational AI — contextual, multi-source reasoning that combines structured data (mastery records), graph data (prerequisites), and behavioral signals into a coherent natural language explanation.

**Implementation**: Enhance existing NL-to-Cypher with Gemini post-processing that combines graph results with mastery data.

---

#### 🏆 Feature 6: "One-Click Micro-Test Dispatch" — Real-Time Adaptive Assessment

**What judges see**: Teacher clicks "Send Micro-Test" on a student card → quiz appears on student's screen in real-time (WebSocket) → student completes → mastery instantly updates → teacher sees result without page refresh.

**Why it's goated**: Shows real-time bidirectional communication. The full loop (identify gap → generate quiz → deliver → score → update mastery) happens in under 30 seconds with zero manual effort.

**Implementation**: All backend exists (`quiz_generator.py` + `quiz_dispatcher.py` + WebSocket). Just needs a "Dispatch Quiz" button on student detail page + dispatch KC selector modal.

---

#### 🏆 Feature 7: "Predictive Decline Alert" — Before They Fall Behind

**What judges see**: Dashboard shows "3 students predicted to decline next week" based on trend analysis of last 5 assessment events + behavioral signals. Each alert has a confidence score and recommended action.

**Why it's goated**: Moves from reactive ("student already failed") to PREDICTIVE ("student will likely fail if we don't act now"). This is the difference between an assessment tool and a true Early Warning System.

**Implementation**: New computation in `dashboard_analytics.py` that analyzes `trend` field + risk trajectory.

---

### 3.2 UX Innovation Differentiators

| Innovation | Description | Technical Approach |
|---|---|---|
| **Severity-Coded Everything** | Every mastery value shows as color-coded pill (green→yellow→orange→red→purple) not just numbers | CSS classes mapped from `GapSeverity` enum |
| **Animated Confidence Bars** | Mastery bars animate on load + show BKT confidence width | Framer Motion + posterior width |
| **Smart Suggestions** | NL query page shows AI-generated question suggestions based on current class state | Pre-compute from `struggling_kcs` |
| **Intervention Timeline** | Student detail shows intervention history as a vertical timeline with ticket state changes | Query `InterventionTicket.history[]` JSON |
| **Skeleton Loading** | All pages use shimmer skeletons instead of spinners | Tailwind animate-pulse |
| **Staggered Reveal** | Cards enter with cascade animation (each 50ms delayed) | CSS transition-delay or framer `staggerChildren` |
| **Risk Pulse** | Critical students' cards have subtle pulsing red border | CSS `@keyframes pulse` + conditional class |
| **Toast Notifications** | Real-time toasts when interventions update or quizzes complete | Sonner (already installed) + WebSocket events |

---

## Part 4: Technical Implementation Specifications

### 4.1 New API Endpoints Needed

```python
# New: Get intervention tickets for a teacher
GET /api/dashboard/teacher/tickets?status=open&class_section=9-A
Response: { tickets: InterventionTicket[], total: int, by_status: {...} }

# New: Transition ticket status
PATCH /api/dashboard/teacher/tickets/{ticket_id}/transition
Body: { new_status: "in_progress", note: "Started remediation" }

# New: Get risk breakdown for a student
GET /api/dashboard/teacher/student-risk/{student_id}
Response: { composite_score, tier, abc_scores: {academic, behavioral, cognitive}, contributing_factors[], urgency_rank }

# New: Get MTSS plan for a student (on-demand computation)
GET /api/dashboard/teacher/student-mtss/{student_id}
Response: { tier, actions: InterventionAction[], escalation_note }

# New: Get prerequisite chain for a KC
GET /api/query/prerequisite-chain/{kc_id}?student_id=STU-2001
Response: { chain: [{kc_id, name, mastery, is_root_cause}], depth }

# New: Predictive alerts
GET /api/dashboard/teacher/alerts?class_section=9-A
Response: { alerts: [{student_id, type, confidence, reason, recommended_action}] }

# New: Intervention effectiveness (admin)
GET /api/dashboard/admin/effectiveness
Response: { by_type: [{intervention_type, total_created, resolved_count, avg_mastery_improvement}] }
```

### 4.2 New Frontend Pages Needed

| Page | Route | Purpose | Backend Endpoints |
|---|---|---|---|
| Teacher Alerts | `/teacher/alerts` | Live alert feed + predictive warnings | `/teacher/alerts` + `/teacher/tickets` |
| Teacher Interventions | `/teacher/interventions` | Kanban ticket board | `/teacher/tickets` + `/tickets/{id}/transition` |
| Admin Analytics | `/admin/analytics` | School-wide heatmaps + effectiveness | `/admin/overview` + `/admin/effectiveness` |
| Student Goals | `/student/goals` | Learning goals + badges + streaks | New simple endpoint |

### 4.3 Enhanced Existing Pages

| Page | Enhancement | Backend Dependency |
|---|---|---|
| Student Detail (`/teacher/students/[id]`) | Add: ABC Risk Radar, MTSS Actions, Root Cause Flow, AI Insights, Intervention Timeline | `/student-risk/{id}`, `/student-mtss/{id}`, `/student/{id}/insights`, `/prerequisite-chain/{kc_id}` |
| Teacher Dashboard | Add: Alert count card, AI class pattern insight, struggling KC severity badges | `/teacher/alerts` count, `/class/{section}/patterns` |
| Student Dashboard | Add: Personalized AI study tip, active intervention status, quiz history | `/query/student/{id}/insights`, ticket status |
| Admin Dashboard | Add: Section comparison, teacher workload, intervention stats | `/admin/effectiveness` |
| Query Page | Add: Suggested questions from class state, richer result display | Already exists, just UI enhancement |

### 4.4 Sidebar Navigation Enhancement

```typescript
// New teacher links
const teacherLinks = [
  { href: "/teacher/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/teacher/alerts", label: "Alerts", icon: Bell, badge: alertCount },
  { href: "/teacher/interventions", label: "Interventions", icon: ClipboardCheck },
  { href: "/teacher/input", label: "Input Data", icon: Upload },
  { href: "/teacher/students", label: "Students", icon: Users },
  { href: "/teacher/knowledge-graph", label: "Knowledge Graph", icon: Network },
  { href: "/teacher/query", label: "AI Query", icon: MessageSquare },
];

// New student links
const studentLinks = [
  { href: "/student/dashboard", label: "My Progress", icon: LayoutDashboard },
  { href: "/student/goals", label: "Goals", icon: Target },
  { href: "/student/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/student/quiz", label: "Quizzes", icon: ClipboardList },
];

// New admin links
const adminLinks = [
  { href: "/admin/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/admin/teachers", label: "Teachers", icon: Users },
];
```

---

## Part 5: Design System Specifications

### 5.1 Risk Color Palette

```css
/* Risk Tier Colors */
--risk-low: #10b981;        /* emerald-500 */
--risk-moderate: #f59e0b;   /* amber-500 */
--risk-high: #f97316;       /* orange-500 */
--risk-critical: #ef4444;   /* red-500 */

/* Gap Severity Colors */
--severity-none: #10b981;     /* green */
--severity-mild: #84cc16;     /* lime */
--severity-moderate: #eab308; /* yellow */
--severity-severe: #f97316;   /* orange */
--severity-critical: #dc2626; /* red-600 */

/* MTSS Tier Colors */
--tier-1: #3b82f6; /* blue — universal */
--tier-2: #f59e0b; /* amber — targeted */
--tier-3: #ef4444; /* red — intensive */

/* Ticket Status Colors */
--status-open: #6366f1;      /* indigo */
--status-assigned: #8b5cf6;  /* violet */
--status-in-progress: #3b82f6; /* blue */
--status-awaiting: #f59e0b;  /* amber */
--status-resolved: #10b981;  /* green */
--status-escalated: #ef4444; /* red */
--status-closed: #6b7280;   /* gray */
```

### 5.2 Animation Specifications

```css
/* Card entrance animation */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.card-animate { animation: slideUp 0.4s ease-out forwards; }
.card-animate:nth-child(1) { animation-delay: 0ms; }
.card-animate:nth-child(2) { animation-delay: 50ms; }
.card-animate:nth-child(3) { animation-delay: 100ms; }

/* Risk pulse for critical students */
@keyframes riskPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}
.risk-critical { animation: riskPulse 2s infinite; }

/* Mastery bar animation */
@keyframes fillBar {
  from { width: 0; }
  to { width: var(--mastery-pct); }
}

/* Counter animation */
function animateValue(el, start, end, duration) {
  // requestAnimationFrame-based count-up
}
```

### 5.3 Component Library Additions Needed

| Component | Purpose | Props |
|---|---|---|
| `<RiskRadar />` | Spider/radar chart for ABC scores | `academic, behavioral, cognitive` |
| `<SeverityBadge />` | Color-coded gap severity pill | `severity: GapSeverity` |
| `<InterventionCard />` | Clickable MTSS action card | `action: InterventionAction, onExecute()` |
| `<TicketKanban />` | Drag-drop ticket board | `tickets[], onTransition()` |
| `<PrerequisiteFlow />` | Horizontal chain visualization | `chain: KCNode[], rootCause` |
| `<AlertBanner />` | Animated alert strip | `alerts[], priority` |
| `<MasteryBar />` | Animated bar with severity color | `mastery, severity, animated` |
| `<TimelineEvent />` | Vertical timeline item | `event: TicketEvent` |
| `<Skeleton />` | Shimmer loading placeholder | `variant: 'card'|'line'|'circle'` |
| `<AnimatedCounter />` | Count-up number animation | `value, duration, prefix` |
| `<AIInsightCard />` | Gemini-generated insight display | `insight: string, confidence` |
| `<QuizDispatchModal />` | KC selector + quiz send | `studentId, gaps[], onDispatch()` |

---

## Part 6: Demo Flow for Judges (5-Minute Script)

### Minute 1: Login & Overview
1. Click "Teacher" demo card → auto-login
2. Dashboard shows class overview with risk distribution pie chart
3. **NEW**: Alert banner at top "⚠️ 3 students need attention" (animated entry)
4. Click alert banner → navigates to Alerts page

### Minute 2: Smart Alerts & Interventions
5. Alerts page shows prioritized student alerts with severity
6. Click highest-priority alert (Ravi, CRITICAL risk)
7. Student detail page loads with **ABC Risk Radar** (spider chart)
8. **NEW**: "AI Insights" section shows natural language summary from Gemini
9. **NEW**: "Root Cause" section shows prerequisite chain flow diagram

### Minute 3: One-Click Intervention
10. **NEW**: "Recommended Actions" section shows MTSS plan (3 action cards)
11. Click "Send Micro-Test" → KC selector modal appears
12. Select KCs → Click "Dispatch" → Toast: "Quiz sent to Ravi's device"
13. **Switch to Student login** → Quiz appears in real-time (WebSocket!)
14. Complete quiz → Score shown → Mastery updates

### Minute 4: Tracking & Effectiveness
15. Back to Teacher → **NEW**: "Interventions" page (Kanban board)
16. Show tickets in various states (Open, In Progress, Resolved)
17. Drag a ticket from "In Progress" → "Awaiting Evidence"
18. **NEW**: Intervention timeline on student page shows history

### Minute 5: Admin & AI Query
19. Switch to Admin login → **NEW**: School-wide analytics
20. Risk heatmap (section × subject matrix)
21. Intervention effectiveness chart
22. Switch to Teacher → AI Query → "Which students need prerequisite review for quadratics?"
23. System responds with structured answer from Neo4j

---

## Part 7: Technical Dependencies & Risks

### No New Infrastructure Required
- All computation uses existing PostgreSQL + Neo4j + Gemini
- WebSocket infrastructure already deployed and working
- Frontend deploys via existing Vercel pipeline
- Backend deploys via existing Render pipeline

### New npm Packages (Frontend)
- `framer-motion` — For staggered animations and transitions (lightweight, 16KB)
- `@dnd-kit/core` — For Kanban drag-and-drop (4KB)
- None for charts — Recharts already installed and used

### Risk Mitigation
| Risk | Mitigation |
|---|---|
| Neo4j cold start | All features gracefully degrade without Neo4j (existing pattern in codebase) |
| Gemini API quota | Quiz generator has fallback templates; insights show "AI temporarily unavailable" |
| WebSocket disconnect | Quiz page already polls via HTTP as fallback |
| Large class performance | Dashboard queries already paginated; tickets filtered by status |

---

## Part 8: Success Metrics

### For Judges
- [ ] Full demo flow completes in under 5 minutes
- [ ] Every backend engine has a visible frontend surface
- [ ] AI features respond in under 3 seconds
- [ ] Real-time quiz dispatch works end-to-end
- [ ] Risk explanation is human-readable (not just numbers)
- [ ] Intervention tracking shows closed-loop workflow

### For Architecture
- [ ] No new backend infrastructure added (leverages existing)
- [ ] All new endpoints follow existing API patterns
- [ ] Frontend uses existing component library (Card, Badge, Button, etc.)
- [ ] Type safety maintained (TypeScript interfaces for all new data)
- [ ] Error handling follows existing patterns (toast notifications)

### For Innovation
- [ ] Multi-dimensional risk scoring (ABC model) — unique in EdTech
- [ ] Prescriptive AI interventions (not just descriptive analytics)
- [ ] Real-time adaptive assessment via WebSocket
- [ ] Causal root-cause analysis via knowledge graph
- [ ] Natural language decision support over graph database
- [ ] Closed-loop intervention tracking (detect → act → verify)
