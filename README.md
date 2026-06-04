<div align="center">

# सहायक 360 — SAHAYAK 360

### The Complete AI-Powered Learning Intelligence Platform

> *"Every student can learn — given the right support at the right time."*

[![Live Demo](https://img.shields.io/badge/LIVE_DEMO-sahayak360--mvp.vercel.app-22c55e?style=for-the-badge&logo=vercel)](https://sahayak360-mvp.vercel.app)
[![API Status](https://img.shields.io/badge/API-LIVE_on_Render-005571?style=for-the-badge&logo=render)](https://sahayak360-api.onrender.com/health)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-008CC1?style=for-the-badge&logo=neo4j)](https://neo4j.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini_1.5_Flash-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/Pipeline_Tests-8%2F8_PASS-brightgreen?style=for-the-badge)](#-running-tests)

---

### 🎯 Built to Solve Two Critical Problems in Indian Education

| Problem | Impact | How Sahayak 360 Solves It |
|---|---|---|
| **Learning gaps & timely feedback** — Teachers cannot diagnose individual gaps in large, mixed-ability classrooms. Students who need support are identified too late or not at all. | Students fall further behind. Teachers burn out trying to give individual attention. | Real-time gap detection after every assessment. AI-generated adaptive quizzes dispatched directly to the student's screen within seconds. Bloom's taxonomy-aligned feedback — zero marking effort for the teacher. |
| **School decision-making & early intervention** — Schools lack integrated systems connecting learning, attendance, and assessment data for early risk identification and planning. | School leaders fly blind. At-risk students slip through. Interventions are reactive, not proactive. | Live risk heatmaps across every section. MTSS tier classification (Tier 1/2/3) per student. Admin dashboards showing teacher workload, class risk %, and intervention ticket status — all in one view. |

</div>

---

## 🏆 What Makes This Different

Most EdTech tools track grades. **Sahayak 360 tracks understanding.**

```
Traditional Tool:                    Sahayak 360:
──────────────────                   ────────────────────────────────────
"Aarav scored 45% on Ch.4"     →     "Aarav's root gap is PREREQUISITE:
                                      Linear Equations → Quadratics.
                                      Mastery: 10%. Risk: HIGH (Tier 2).
                                      Adaptive quiz dispatched NOW.
                                      Intervention ticket raised for
                                      Ms. Priya Sharma."
```

- Bayesian Knowledge Tracing (BKT) — mastery as a **probability**, not a percentage
- Neo4j knowledge graph traces gaps to their **root prerequisite**, not just the symptom
- MTSS Tier 1/2/3 assignment with structured intervention plans — **auto-generated**
- HTTP-polled adaptive quizzes appear on the student's screen **within 10 seconds** of dispatch
- Admin sees institution-wide risk, workload, and effectiveness — **real-time, all in one place**

---

## ⚡ 4-Second End-to-End Flow

```
Teacher photographs answer sheet   →   4 seconds   →   "Aarav: HIGH RISK — Tier 2"
                                                        Root gap: ALG-LINEAR-EQ
                                                        Adaptive quiz dispatched ✓
                                                        Intervention ticket raised ✓
                                                        Admin risk heatmap updated ✓
```

- **3 input channels:** structured JSON · natural language · photo of answer sheet
- **BKT:** Bayesian mastery update on every KC after every submission
- **Neo4j:** prerequisite chain traversal — fix root causes, not symptoms
- **MTSS:** Tier 1 / 2 / 2+ / 3 with structured intervention action lists
- **HTTP polling:** quiz appears on student dashboard automatically, no page refresh
- **8/8 pipeline tests** pass with zero database or API key needed

---

## 🖥️ Fresh Machine Setup (Start Here)

> **Already have Python 3.11+, Node.js 18+, PostgreSQL 16, and Neo4j 5?**
> Skip to [Quick Start](#-quick-start--manual-no-docker).

All commands below are copy-paste ready for **Windows PowerShell**.

---

### Step 1 — Install Python 3.13

```powershell
# Check if Python is already installed
python --version
# If you see "Python 3.11" or higher → skip this step

# Install via winget (built into Windows 10/11)
winget install Python.Python.3.13

# Close and reopen PowerShell, then verify:
python --version    # Expected: Python 3.13.x
pip --version       # Expected: pip 24.x
```

> **No winget?** Download from https://www.python.org/downloads/ — tick **"Add Python to PATH"** during install.

---

### Step 2 — Install Node.js 20 LTS

```powershell
# Check if Node.js is already installed
node --version
# If you see "v18" or higher → skip this step

# Install Node.js 20 LTS via winget
winget install OpenJS.NodeJS.LTS

# Close and reopen PowerShell, then verify:
node --version    # Expected: v20.x.x
npm --version     # Expected: 10.x.x
```

> **No winget?** Download the LTS installer from https://nodejs.org/en/download

---

### Step 3 — Install PostgreSQL 16

```powershell
# Check if PostgreSQL is already installed
psql --version
# If you see "psql (PostgreSQL) 16.x" → skip this step

# Install via winget
winget install PostgreSQL.PostgreSQL.16
# Set superuser password to: postgres   (remember this)

# Verify after install (PostgreSQL runs as a Windows service automatically):
psql -U postgres -c "SELECT version();"
# Expected: PostgreSQL 16.x ...
```

> **No winget?** Download from https://www.postgresql.org/download/windows/ — use the interactive installer, set password to `postgres`.

---

### Step 4 — Install Neo4j 5

```powershell
# Easiest: Install Neo4j Desktop (free GUI)
# Download from: https://neo4j.com/download/
# Install it → Open → Create a local database → Start it
# Default bolt port: 7687
# Set the database password to: neo4j_dev_2026

# OR install Neo4j Community Server manually:
winget install Neo4j.Neo4j
# After install:
C:\neo4j\bin\neo4j.bat console
# Open http://localhost:7474 → login neo4j/neo4j → set password to: neo4j_dev_2026
```

> Verify Neo4j is running: open **http://localhost:7474** in your browser.

---

### Step 5 — Get a Gemini API Key (Free)

1. Go to **https://aistudio.google.com/app/apikey**
2. Click **"Create API Key"**
3. Copy the key — you will paste it into `backend/.env` in the next step.

> Free tier: **60 requests/minute** — more than enough for development and demo.

---

## 🚀 Quick Start — Manual (No Docker)

> Docker is available but can fail on some machines. **The manual path below always works.**

### 1. Clone the Repository

```powershell
git clone https://github.com/SanjayS-007/sahayak360-mvp.git
cd sahayak360-mvp
```

---

### 2. Backend Setup

Run these commands in PowerShell from the repo root:

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate
# You will see (venv) at the start of your prompt — that means it worked

# Upgrade pip
python -m pip install --upgrade pip

# Install ALL Python dependencies in one command
pip install -r requirements.txt
```

The `requirements.txt` installs:
```
fastapi  uvicorn  pydantic  pydantic-settings  pandas  numpy
google-generativeai  opencv-python-headless  neo4j  sqlalchemy
asyncpg  python-jose  passlib  websockets  python-multipart  pillow  httpx  python-dotenv
```

```powershell
# Open backend/.env and replace the Gemini key placeholder
notepad .env
# Find:    GEMINI_API_KEY=test_key_placeholder
# Replace: GEMINI_API_KEY=AIza...your_actual_key_here
# Save and close
```

```powershell
# Create the PostgreSQL database and user
psql -U postgres -c "CREATE USER sahayak WITH PASSWORD 'sahayak_dev_2026';"
psql -U postgres -c "CREATE DATABASE sahayak360 OWNER sahayak;"
# Enter your postgres superuser password when prompted

# Create all tables
python -c "import asyncio; from db.postgres import init_db; asyncio.run(init_db())"

# Load demo data (users, sample events, tickets)
psql -U sahayak -d sahayak360 -f ..\scripts\seed_postgres.sql
# Password: sahayak_dev_2026

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

**Verify in a new PowerShell tab:**
```powershell
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"sahayak-360-api","version":"1.0.0"}
```

---

### 3. Frontend Setup

Open a **new PowerShell tab** (keep the backend running):

```powershell
cd sahayak360-mvp\frontend

# Install ALL Node.js dependencies (takes 2-3 minutes first time — normal)
npm install

# Create local environment file
copy .env.local.example .env.local
# Default: NEXT_PUBLIC_API_URL=http://localhost:8000  ← already correct, no changes needed

# Start the frontend
npm run dev
```

**Expected output:**
```
▲ Next.js 14.x.x
- Local:  http://localhost:3000
- Ready in 2.1s
```

Open **http://localhost:3000** in your browser.

---

### 4. Seed the Neo4j Knowledge Graph

1. Open **http://localhost:7474**
2. Login: `neo4j` / `neo4j_dev_2026`
3. Click the file/folder icon → paste the entire contents of `scripts/seed_neo4j.cypher`
4. Press **Ctrl+Enter** to run

This loads: 8 Knowledge Components, 5 prerequisite chains, 5 demo students.

---

### ✅ Verify All Services Are Running

| Service | URL | Expected Response |
|---------|-----|-------------------|
| **Frontend** | http://localhost:3000 | Login page |
| **Backend API** | http://localhost:8000/health | `{"status":"healthy"}` |
| **Swagger UI** | http://localhost:8000/docs | Interactive API docs |
| **Neo4j Browser** | http://localhost:7474 | Graph database UI |

---

## 🌐 Live Demo

> **No setup required. Open and log in.**

| URL | |
|---|---|
| **Frontend** | [https://sahayak360-mvp.vercel.app](https://sahayak360-mvp.vercel.app) |
| **API Health** | [https://sahayak360-api.onrender.com/health](https://sahayak360-api.onrender.com/health) |
| **Swagger Docs** | [https://sahayak360-api.onrender.com/docs](https://sahayak360-api.onrender.com/docs) |

> **Note:** The API runs on Render's free tier. If it hasn't been accessed in a while, the first request may take ~15 seconds to cold-start. Subsequent calls are instant.

## 👤 Demo Login Accounts

| Role | Name | Email | Password |
|------|------|-------|----------|
| **Student** | Aarav Patel | `student1@school.com` | `Demo@2026Secure` |
| **Teacher** | Ms. Priya Sharma | `teacher1@school.com` | `Demo@2026Secure` |
| **Admin** | Dr. Suresh Menon | `admin1@school.com` | `Demo@2026Secure` |

### What to Try (Demo Walkthrough)

**As Teacher (Ms. Priya Sharma):**
1. Go to `/teacher/dashboard` — see live risk heatmap for Class 9-A (34% at-risk)
2. Go to `/teacher/students` — browse all 13 students with mastery bars per KC
3. Go to `/teacher/interventions` — see 302 open intervention tickets
4. Dispatch a quiz: `POST /api/quiz/dispatch` with `student_id: STU-2001` — shows up on student's screen in ≤10 seconds

**As Student (Aarav Patel):**
1. Go to `/student/dashboard` — see personal mastery across 7 Knowledge Components
2. Go to `/student/practice` — pick a KC, get Gemini-generated questions by difficulty
3. Go to `/student/quiz` — pending quizzes auto-appear; no page refresh needed
4. Go to `/student/leaderboard` — class XP rankings
5. Go to `/student/flashcards` — AI-generated revision cards per KC

**As Admin (Dr. Suresh Menon):**
1. Go to `/admin/dashboard` — institution overview: 3 teachers · 18 students · 106 events · 419 interventions
2. Go to `/admin/analytics` — effectiveness tracking, teacher workload, risk heatmap by section
3. Go to `/admin/teachers` — click any teacher → detailed profile with student count, avg mastery, ticket breakdown

---

## 🧪 Running Tests

> Tests run with **zero database, zero Gemini API key, zero Docker** — just Python.

```powershell
cd backend
.\venv\Scripts\activate
python test_pipeline.py
```

**Expected output:**
```
=== SAHAYAK 360 — Pipeline Integration Tests ===

TEST 1: StructuredIngestRequest validation ... PASS
TEST 2: AssessmentEventAST construction ..... PASS
TEST 3: Pandas cross-field validation ....... PASS
TEST 4: Threshold evaluator ................. PASS
TEST 5: Bayesian Knowledge Tracing (BKT) .... PASS
TEST 6: ABC Risk scorer ..................... PASS
TEST 7: MTSS engine ......................... PASS
TEST 8: Ticket lifecycle state machine ...... PASS

=== 8/8 TESTS PASSED (0.31s) ===
```

---

## 🐳 Docker (Optional)

> Docker is provided as a convenience option only. **If docker-compose gives you errors, use the manual setup above.**

```powershell
# Prerequisites: Docker Desktop must be installed and running
# Download from: https://www.docker.com/products/docker-desktop/

# Verify Docker is running
docker --version
docker compose version

# Build and start full stack (first run takes ~5 minutes)
docker compose up --build
```

**Common docker-compose errors and fixes:**

| Error Message | Fix |
|---------------|-----|
| `Cannot connect to the Docker daemon` | Open **Docker Desktop** app and wait for the whale icon to stop animating |
| `port is already in use: 5432` | PostgreSQL is already running locally. Either stop it: `net stop postgresql-x64-16` or edit `docker-compose.yml` to map `5433:5432` |
| `port is already in use: 7474` | Neo4j is already running locally. Stop it or change port in `docker-compose.yml` |
| `no configuration file provided` | Run `docker compose up` from the repo root (`sahayak360-mvp/`), not from inside `backend/` |
| Frontend is blank after startup | Wait 60 seconds — Next.js first compile inside Docker is slow |
| `Error: ENOENT requirements.txt` | Run from repo root, not subdirectory |

**Recommended hybrid approach** (databases in Docker, app runs locally):
```powershell
# Start only the databases in Docker
docker compose up -d db neo4j

# Then run backend + frontend manually (faster dev experience)
cd backend ; .\venv\Scripts\activate ; uvicorn main:app --reload --port 8000
cd frontend ; npm run dev
```

---

## ⚙️ Environment Variables

### `backend/.env` — committed with dev defaults (private repo)

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://sahayak:sahayak_dev_2026@localhost:5432/sahayak360

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_dev_2026

# ⚠ ONLY LINE YOU MUST CHANGE
# Get your free key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=test_key_placeholder

# JWT Auth
JWT_SECRET=dev_secret_key_2026
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000
```

**What works WITHOUT a Gemini key:**
- ✅ Structured JSON ingestion (full 10-step pipeline)
- ✅ All 8 pipeline tests
- ✅ Dashboard, mastery, quiz, risk scoring
- ❌ Freetext / Voice ingestion
- ❌ Vision / photo ingestion
- ❌ NL-to-Cypher queries

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   BROWSER (Next.js 14 — App Router)                  │
│                                                                       │
│  /student/dashboard    /student/practice    /student/quiz             │
│  /student/leaderboard  /student/flashcards  /student/goals            │
│  /teacher/dashboard    /teacher/students    /teacher/interventions     │
│  /teacher/alerts       /teacher/knowledge-graph  /teacher/query       │
│  /admin/dashboard      /admin/analytics     /admin/teachers/[id]      │
│                                                                       │
│  Zustand state · Axios HTTP client · Recharts · shadcn/ui · Tailwind  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ REST (JWT Bearer) + HTTP Polling
┌──────────────────────────────▼──────────────────────────────────────┐
│                        FASTAPI BACKEND                                │
│   /api/auth  /api/ingest  /api/practice  /api/quiz  /api/dashboard   │
│   /api/admin/analytics    /api/query                                  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              INGESTION ORCHESTRATOR (10 Steps)               │    │
│  │  RouteGovernor → PandasValidator → GapDetector              │    │
│  │  → BKT MasteryUpdater → ABC RiskScorer → MTSSEngine         │    │
│  │  → TicketLifecycle → DB Persist → MasteryUpsert             │    │
│  │  → Neo4j Sync                                               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  GeminiClient (LLM+Vision) · OpenCV Preprocessor · Quiz Engine       │
└──────────┬─────────────────────────┬──────────────────┬─────────────┘
           │                         │                  │
  ┌────────▼────────┐   ┌────────────▼──────┐   ┌──────▼─────────────┐
  │  PostgreSQL 16   │   │    Neo4j 5          │   │  Google Gemini     │
  │  Users           │   │  Knowledge DAG      │   │  1.5 Flash API     │
  │  AssessmentEvents│   │  KC nodes           │   │                    │
  │  MasteryRecords  │   │  PREREQUISITE_OF    │   │  freetext → AST    │
  │  Tickets         │   │  MASTERED edges     │   │  vision  → AST     │
  │  QuizSessions    │   │  prerequisite chain │   │  quiz generation   │
  └─────────────────┘   └───────────────────┘   │  practice Qs       │
                                                  └────────────────────┘
```

### Deployment Architecture

```
GitHub (main branch)
        │
        ├──── Vercel ──────── Next.js 14 frontend
        │                     Auto-deploy on push · Global CDN
        │
        └──── Render ──────── FastAPI backend (Python 3.13)
                              PostgreSQL 16 (Render managed)
                              Gemini API (Google Cloud)
```

### Data Flow: Quiz Dispatch

```
Teacher clicks "Send Quiz"
        │
        ▼
POST /api/quiz/dispatch
        │  Gemini generates N questions for target KC
        │  Questions stored in QuizSession (status=pending)
        ▼
PostgreSQL: QuizSession created
        │
        │  (student app polls /quiz/sessions?status=pending every 10s)
        │
        ▼
Student sees new quiz card → clicks "Start Quiz"
        │
        ▼
GET /api/quiz/{session_id}  →  questions returned (no answers)
        │
        ▼
Student submits → POST /api/quiz/submit
        │  BKT mastery update for each KC
        │  QuizSession status → completed
        ▼
Score + mastery delta returned to student
```

---

## ✨ Complete Feature Set

### For Teachers — Diagnosis & Action Without Extra Burden

| Feature | What It Does | Key Consideration Met |
|---|---|---|
| **Risk Heatmap** | Live per-student risk score across the class. Color-coded: green / amber / red. | Early warning |
| **Student Deep-Dive** | Per-student KC mastery bars, Bloom's level breakdown, prerequisite gap trace | Actionable insights |
| **Quiz Dispatch** | One click → Gemini generates 3–10 adaptive questions → student sees them in ≤10s | Timely feedback |
| **Intervention Tickets** | Auto-raised on every MTSS Tier 2+ event. Tracks status: open → in-progress → resolved | Low teacher burden |
| **Knowledge Graph View** | Neo4j-powered prerequisite chains — see WHY a student is struggling | Actionable insights |
| **Alerts** | Teacher-facing alerts for high-urgency tickets and critical student events | Timely feedback |
| **NL Query** | Ask questions in plain English: *"Which students in 9-A failed fractions twice?"* | Classroom integration |

### For Students — Personalized, Motivated Learning

| Feature | What It Does |
|---|---|
| **Adaptive Practice** | Gemini generates questions at basic / intermediate / advanced difficulty, matching current mastery |
| **Live Quizzes** | Teacher-dispatched quizzes appear automatically (HTTP polling every 10s). No reload needed. |
| **Mastery Dashboard** | Real-time mastery bars across all 7 Knowledge Components with trend arrows |
| **Flashcards** | AI-generated revision cards per KC — available offline after first load |
| **Goals & XP** | XP earned on every practice submission. Gamified progress visible on leaderboard. |
| **Leaderboard** | Class-wide XP rankings — healthy competition within sections |
| **Prerequisites View** | Visual map showing which KCs unlock after mastering current ones |
| **Analytics** | Personal performance over time — correct rate, mastery growth, XP history |

### For Admins & School Leaders — Institution-Wide Intelligence

| Feature | What It Does | Key Consideration Met |
|---|---|---|
| **Institution Overview** | Real-time counts: teachers, students, assessment events, intervention tickets | Decision support |
| **Risk Heatmap (Admin)** | Section-level risk %: e.g., 9-A=34% at-risk, 9-B=26% at-risk | Early warning |
| **Teacher Workload** | Per-teacher: open tickets, urgent tickets, class section — spot overloaded teachers instantly | Actionability |
| **Effectiveness Tracking** | Per-intervention-type: total created, resolution rate, estimated improvement | Decision support |
| **Teacher Profile Detail** | Per-teacher stats: students assigned, avg class mastery, ticket resolution rate | Interoperability |
| **Teachers Directory** | Full teacher list with section assignment and profile link | Privacy and reliability |

---

## 🧠 The Intelligence Engine — How It Works

### 10-Step Cognitive Pipeline

Every assessment submission (from any channel) runs through this pipeline:

```
Step 1  │ ROUTE          → Fast lane (structured JSON) or Slow lane (AI-parsed)
Step 2  │ VALIDATE       → Pandas cross-field math + anomaly detection
Step 3  │ GAP DETECT     → Per-KC threshold check (default 60%)
Step 4  │ BKT MASTERY    → Bayesian Knowledge Tracing update per KC
          │                  P(mastery|correct) = P(L) + (1-P(L)) * P(G)  [guess correction]
          │                  P(mastery|wrong)   = P(L) * (1-P(S)) / normalizer  [slip correction]
Step 5  │ RISK SCORE     → ABC composite score
          │                  Risk = 0.50 × Academic + 0.25 × Behavioral + 0.25 × Cognitive
Step 6  │ MTSS PLAN      → Tier 1 (monitor) / 2 (small group) / 2+ (specialist) / 3 (intensive)
Step 7  │ TICKETS        → Intervention ticket raised with 5-state lifecycle
Step 8  │ PERSIST EVENT  → PostgreSQL async upsert (assessment_events)
Step 9  │ UPSERT MASTERY → Per-student per-KC mastery record updated
Step 10 │ NEO4J SYNC     → Knowledge DAG edge update + prerequisite chain propagation
```

### Bayesian Knowledge Tracing (BKT)

Unlike raw percentages, BKT models **learning as a probability**:

- `P(L₀)` — prior probability student already knows the KC
- `P(T)` — probability of transitioning from not-knowing to knowing after practice
- `P(G)` — guess probability (student answers correctly without knowing)
- `P(S)` — slip probability (student answers incorrectly despite knowing)

This means a student who gets 3/5 right on hard questions may have **higher mastery** than one who gets 5/5 right on easy ones. That nuance matters.

### Neo4j Prerequisite Graph

```
ALG-LINEAR-EQ  ──PREREQUISITE_OF──►  ALG-QUAD-EQ
                                           │
                                    PREREQUISITE_OF
                                           │
                                           ▼
GEO-TRIANGLES  ──PREREQUISITE_OF──►  TRIG-BASIC
```

When Aarav fails TRIG-BASIC, the system traces back to the root gap: `ALG-LINEAR-EQ`. The intervention targets the root, not the symptom. **This is the difference between remediation that works and remediation that doesn't.**

### MTSS Tiers — Graduated Response

| Tier | Risk Score | Intervention |
|---|---|---|
| **Tier 1** | 0–40 | Universal support. Monitor. Standard classroom instruction. |
| **Tier 2** | 40–65 | Small-group targeted support. Weekly check-in. Adaptive practice assigned. |
| **Tier 2+** | 65–80 | Specialist referral. Bi-weekly assessment. Customized remediation plan. |
| **Tier 3** | 80–100 | Intensive 1-on-1 support. Daily monitoring. Parent notification. |

---

## 📡 API Reference

Full interactive docs at **[https://sahayak360-api.onrender.com/docs](https://sahayak360-api.onrender.com/docs)**

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user — `{email, password, full_name, role}` |
| `POST` | `/api/auth/login` | Login → returns `{access_token, user_id, role, full_name}` |
| `GET`  | `/api/auth/me` | Get current user from JWT |

### Assessment Ingestion
| Method | Endpoint | Description | Latency |
|--------|----------|-------------|---------|
| `POST` | `/api/ingest/structured` | Direct JSON → 10-step pipeline | ~50ms |
| `POST` | `/api/ingest/freetext` | Natural language → Gemini → AST → pipeline | ~1.5s |
| `POST` | `/api/ingest/vision` | Answer sheet photo → OpenCV → Gemini Vision → pipeline | ~3s |

**Minimal structured ingestion body:**
```json
{
  "teacher_id": "TCH-1001",
  "student_id": "STU-2001",
  "class_section": "9-A",
  "subject": "mathematics",
  "department_id": "DEPT-MATH",
  "assessment_type": "formative",
  "max_score": 30,
  "total_obtained": 12,
  "items": [
    {
      "question_id": "Q1",
      "knowledge_component_id": "ALG-LINEAR-EQ",
      "knowledge_component_name": "Linear Equations",
      "max_marks": 10,
      "obtained_marks": 3
    }
  ]
}
```

### Practice (Student-Facing)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/practice/available-kcs` | List all available KCs with difficulty levels |
| `POST` | `/api/practice/generate` | `{kc_id, count}` → Gemini generates adaptive questions |
| `POST` | `/api/practice/submit` | `{kc_id, difficulty, answers[]}` → score + mastery update + XP |

### Quiz (Teacher → Student)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/quiz/dispatch` | Teacher dispatches quiz: `{student_id, target_kc_ids[], num_questions}` |
| `GET`  | `/api/quiz/sessions?status=pending` | Student polls for pending quizzes (every 10s) |
| `GET`  | `/api/quiz/{session_id}` | Fetch full session with questions (correct answers stripped) |
| `POST` | `/api/quiz/submit` | `{session_id, responses[]}` → score + mastery update |

### Dashboards
| Method | Endpoint | Auth | Returns |
|--------|----------|------|---------|
| `GET`  | `/api/dashboard/teacher/overview` | teacher | Student list with risk scores |
| `GET`  | `/api/dashboard/teacher/students` | teacher | Detailed per-student mastery |
| `GET`  | `/api/dashboard/student/mastery` | student | KC mastery bars + XP |
| `GET`  | `/api/dashboard/admin/overview` | admin | `{total_teachers, total_students, total_events, active_interventions}` |
| `GET`  | `/api/dashboard/admin/teachers` | admin | Teacher list with section assignments |

### Admin Analytics
| Method | Endpoint | Auth | Returns |
|--------|----------|------|---------|
| `GET`  | `/api/admin/analytics/effectiveness` | admin | Intervention effectiveness by type + resolution rates |
| `GET`  | `/api/admin/analytics/teacher-workload` | admin | Per-teacher open/urgent ticket counts |
| `GET`  | `/api/admin/analytics/risk-heatmap` | admin | Per-section student count + risk percentage |
| `GET`  | `/api/admin/analytics/teacher/{teacher_id}` | admin | Full teacher profile: mastery, tickets, students |

## 🛠️ Full Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend framework | FastAPI | 0.111+ | Async REST API |
| ASGI server | Uvicorn | 0.30+ | Production-grade server |
| Language | Python | 3.13 | Backend + pipeline |
| Validation | Pydantic V2 | 2.7+ | AST schema + settings |
| ORM | SQLAlchemy async | 2.0+ | PostgreSQL access |
| DB driver | asyncpg | 0.29+ | High-performance Postgres |
| Graph DB | Neo4j async | 5.22+ | Knowledge prerequisite DAG |
| AI / LLM | Google Gemini 1.5 Flash | 0.7+ | Quiz gen, NL ingest, vision |
| Computer Vision | OpenCV headless + Pillow | 4.10+ | Answer sheet scanning |
| Data processing | Pandas + NumPy | 2.2+ / 1.26+ | Cross-field validation |
| Auth | python-jose + passlib (bcrypt) | — | JWT + password hashing |
| Frontend | Next.js 14 (App Router) | 14.2+ | SSR + client UI |
| Frontend language | TypeScript | 5.5 | Type-safe frontend |
| Styling | Tailwind CSS + shadcn/ui | 3.4 | Rapid, accessible UI |
| Charts | Recharts | 2.12 | Mastery bars, heatmaps |
| State | Zustand | 4.5 | Lightweight global state |
| HTTP client | Axios | 1.7 | API calls from browser |
| Hosting (frontend) | Vercel | — | Auto-deploy, global CDN |
| Hosting (backend) | Render | — | Managed PostgreSQL + FastAPI |

---

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| `(venv) not showing` / `ModuleNotFoundError` | Run `.\venv\Scripts\activate` before any python command |
| `database 'sahayak360' does not exist` | Run the `CREATE USER` and `CREATE DATABASE` steps from [Backend Setup](#2-backend-setup) |
| `ServiceUnavailable: bolt://localhost:7687` | Neo4j is not running — open Neo4j Desktop and click Start |
| `GEMINI_API_KEY not configured` | Edit `backend/.env`, replace `test_key_placeholder` with your real key from [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| `npm install` hangs | Run `npm cache clean --force` then retry |
| Port 8000 already in use | `netstat -ano \| findstr :8000` → `taskkill /PID <number> /F` |
| Port 3000 already in use | `npm run dev -- --port 3001` |
| `psql is not recognized` | PostgreSQL bin not in PATH — add `C:\Program Files\PostgreSQL\16\bin` to system PATH |
| Render API cold start slow | First request after inactivity takes ~15s — expected on free tier |

---

## 🗺️ Roadmap

### Near-Term
- [ ] Behavioral risk from attendance + submission rate (UDISE API integration)
- [ ] SMS / WhatsApp parent alerts on CRITICAL tier (Twilio / Meta API)
- [ ] Resolved ticket effectiveness tracking — close the feedback loop
- [ ] Teacher-to-teacher ticket handoff and escalation flow

### Medium-Term
- [ ] Hindi, Tamil, Telugu, Kannada UI (next-intl slots already wired in codebase)
- [ ] Offline PWA sync queue for low-connectivity rural schools
- [ ] Google Classroom / Moodle / DigiLocker import
- [ ] Longitudinal mastery trend graphs (30-day, term, annual)
- [ ] Student reading level and vocabulary KC support (not just Math)

### Long-Term
- [ ] Teacher mobile app (React Native) — scan and dispatch from classroom
- [ ] District-level admin view — aggregate risk across 50+ schools
- [ ] National curriculum KC graph — NCERT-aligned KC taxonomy
- [ ] Predictive dropout risk model (LSTM on longitudinal BKT sequences)
- [ ] Integration with NIPUN Bharat and FLN assessment frameworks

---

## 📁 Project Structure

```
sahayak-360/
├── backend/
│   ├── main.py                    # FastAPI app entry, all routes registered
│   ├── config.py                  # Pydantic Settings — all env vars
│   ├── requirements.txt           # Python dependencies
│   ├── test_pipeline.py           # 8 tests — no DB or API key needed
│   ├── seed_demo_data.py          # Demo data seeder with per-KC student profiles
│   ├── api/
│   │   ├── routes_auth.py         # Login, register, me
│   │   ├── routes_ingest.py       # Structured / freetext / vision ingest
│   │   ├── routes_practice.py     # available-kcs, generate, submit
│   │   ├── routes_quiz.py         # dispatch, sessions, detail, submit
│   │   ├── routes_dashboard.py    # Teacher, student, admin dashboards
│   │   └── routes_admin_analytics.py  # Effectiveness, workload, heatmap, teacher detail
│   ├── core/
│   │   ├── ast_schema.py          # Frozen AST v2.0 (Pydantic V2)
│   │   ├── mastery_updater.py     # BKT bayesian_update()
│   │   ├── risk_scorer.py         # ABC composite scorer (50/25/25)
│   │   ├── mtss_engine.py         # MTSS Tier 1/2/2+/3 + action plans
│   │   ├── gap_detector.py        # Per-KC threshold analysis
│   │   └── ticket_lifecycle.py    # 5-state intervention lifecycle
│   ├── db/                        # SQLAlchemy async ORM + Neo4j driver
│   ├── llm/                       # Gemini client + prompts (quiz, NL, vision)
│   ├── services/                  # Ingestion orchestrator (10-step pipeline)
│   └── vision/                    # OpenCV preprocessor + answer extractor
│
├── frontend/src/app/
│   ├── (auth)/login/              # Login page
│   ├── (auth)/register/           # Registration
│   ├── student/
│   │   ├── dashboard/             # Mastery bars, XP, recent activity
│   │   ├── practice/              # KC selector + Gemini adaptive questions
│   │   ├── quiz/                  # HTTP-polled teacher-dispatched quizzes
│   │   ├── analytics/             # Personal performance history
│   │   ├── flashcards/            # AI revision cards per KC
│   │   ├── goals/                 # XP goals and streaks
│   │   ├── leaderboard/           # Class XP rankings
│   │   └── prerequisites/         # KC dependency visual map
│   ├── teacher/
│   │   ├── dashboard/             # Class risk heatmap
│   │   ├── students/              # Per-student mastery breakdown
│   │   ├── input/                 # Assessment ingestion (JSON/NL/Vision)
│   │   ├── interventions/         # Ticket management
│   │   ├── alerts/                # High-urgency notifications
│   │   ├── knowledge-graph/       # Neo4j prerequisite visualizer
│   │   └── query/                 # NL query interface
│   └── admin/
│       ├── dashboard/             # Institution overview + risk summary
│       ├── analytics/             # Effectiveness, workload, heatmap
│       └── teachers/
│           ├── page.tsx           # Teachers directory
│           └── [id]/page.tsx      # Teacher profile detail
│
├── scripts/
│   ├── seed_postgres.sql          # Demo users + events + tickets
│   └── seed_neo4j.cypher          # 8 KCs + prerequisite chains
│
├── render.yaml                    # Render deployment config
└── docker-compose.yml             # Optional full-stack containers
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Sahayak** (सहायक) means *helper* in Hindi.

Built for India's 250 million school students and the teachers who serve them.

The two problems this platform addresses — learning gaps with timely feedback, and school-level early intervention — are not data problems. They are *visibility* problems. Sahayak 360 makes the invisible visible.

[![Live Demo](https://img.shields.io/badge/Try_It_Now-sahayak360--mvp.vercel.app-22c55e?style=for-the-badge&logo=vercel)](https://sahayak360-mvp.vercel.app)

*"Diagnose early. Intervene intelligently. Leave no student behind."*

</div>
