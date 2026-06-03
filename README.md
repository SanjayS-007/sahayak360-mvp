<div align="center">

# 🎓 SAHAYAK 360

### AI-Powered Educational Analytics & Intervention Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-008CC1?style=for-the-badge&logo=neo4j)](https://neo4j.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini_1.5_Flash-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Tests](https://img.shields.io/badge/Pipeline_Tests-8%2F8_PASS-brightgreen?style=for-the-badge)](#-running-tests)
[![Status](https://img.shields.io/badge/Status-MVP_Ready-blue?style=for-the-badge)](#)

---

**Sahayak 360** is a full-stack, production-ready educational intelligence platform that ingests student assessments via **structured JSON**, **natural language**, or **scanned answer sheet images** — then runs a deterministic **10-step cognitive pipeline** to detect knowledge gaps, compute Bayesian mastery scores, assign MTSS intervention tiers, generate adaptive micro-quizzes via Gemini AI, and deliver them in real time over WebSocket.

[Quick Start](#-quick-start) · [Team Onboarding](#-team-setup--onboarding) · [Architecture](#-architecture) · [API Docs](#-api-reference) · [Pipeline Deep Dive](#-10-step-pipeline-deep-dive) · [Data Models](#-data-models) · [Env Variables](#-environment-variables) · [Tests](#-running-tests)

</div>

---

## ✨ Features

### 📥 Multi-Channel Assessment Ingestion
| Channel | Endpoint | Processing | Latency |
|---------|----------|-----------|---------|
| **Structured JSON** | `POST /api/ingest/structured` | Direct AST validation + Pandas | ~50ms |
| **Freetext / Voice** | `POST /api/ingest/freetext` | Gemini 1.5 Flash → AST parse | ~1.5s |
| **Vision / OCR** | `POST /api/ingest/vision` | OpenCV preprocess → Gemini Vision → AST | ~3s |

All three channels funnel into the **same deterministic 10-step pipeline**.

### 🧠 10-Step Cognitive Pipeline
```
1. Route          → Fast lane (structured) or Slow lane (AI-parsed)
2. Validate       → Pandas cross-field math checks + anomaly detection
3. Gap Detection  → Per-KC threshold evaluation (configurable cutoffs)
4. Mastery Update → Bayesian Knowledge Tracing (BKT) per Knowledge Component
5. Risk Scoring   → ABC composite (Academic 50% + Behavioral 25% + Cognitive 25%)
6. MTSS Plan      → Tier 1 / 2 / 2+ / 3 assignment + intervention steps
7. Tickets        → Intervention ticket factory with 5-state lifecycle
8. Persist Event  → PostgreSQL async upsert
9. Upsert Mastery → Per-student per-KC mastery record
10. Neo4j Sync    → Knowledge DAG update + prerequisite chain propagation
```

### 📊 Role-Based Dashboards
| Role | Features |
|------|----------|
| **Teacher** | Class risk heatmap, KC mastery overview, student roster with trend sparklines |
| **Student** | Personal KC mastery bars, gap list, quiz history, MTSS tier badge |
| **Admin** | Institution stats: teacher/student counts, tier distribution, active tickets |

### ⚡ Real-Time Quiz Engine (MCP)
- Teacher triggers a micro-test from the dashboard
- Gemini generates contextual questions per failing Knowledge Component
- MCP Quiz Dispatcher pushes questions over WebSocket to the student browser
- Student answers in real time; submissions rerun BKT mastery deltas

### 🔍 NL-to-Cypher Query Interface
- Teacher asks: *"Which students in 8-A are weak in fractions and missing prerequisite division?"*
- Gemini converts to safe read-only Cypher with write-keyword guard
- Neo4j traverses the knowledge DAG and returns prerequisite chain insights

### 🛡️ Security
- JWT HS256 auth with configurable expiry
- Role-based route guards: `teacher` / `student` / `admin`
- WRITE_KEYWORDS blocklist in NL-to-Cypher safety layer
- Pydantic V2 strict validation at every ingestion boundary
- bcrypt password hashing (passlib)

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    BROWSER (Next.js 14)                           │
│  /login /register /teacher/* /student/* /admin/dashboard          │
│  Zustand + Axios + Recharts + shadcn/ui + Tailwind CSS            │
└─────────────────────────┬────────────────────────────────────────┘
                          │ REST + WebSocket
┌─────────────────────────▼────────────────────────────────────────┐
│                      FASTAPI BACKEND                               │
│                                                                    │
│  /api/auth  /api/ingest  /api/dashboard  /api/quiz  /api/query   │
│  WebSocket  /ws/student/{id}                                      │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │            INGESTION ORCHESTRATOR (10 Steps)              │    │
│  │  RehydrationGovernor → PandasValidator → Threshold        │    │
│  │  → BKT MasteryUpdater → ABC RiskScorer → MTSSEngine      │    │
│  │  → TicketLifecycle → DB Persist → Neo4j Sync             │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  GeminiClient (LLM+Vision)  OpenCV Preprocessor  WS Manager      │
└──────────┬──────────────────────┬──────────────────┬─────────────┘
           │                      │                  │
  ┌────────▼────────┐  ┌──────────▼──────┐  ┌───────▼────────────┐
  │  PostgreSQL 16   │  │    Neo4j 5       │  │  Google Gemini     │
  │  assessment_events  │  Knowledge DAG   │  │  1.5 Flash API     │
  │  mastery_records │  │  PREREQUISITE_OF │  │  freetext→AST      │
  │  tickets/users   │  │  MASTERED edges  │  │  vision→AST        │
  └─────────────────┘  └──────────────────┘  │  quiz generation   │
                                              │  NL→Cypher         │
                                              └────────────────────┘
```

---

## 📁 Project Structure

```
sahayak-360/
├── backend/
│   ├── main.py                          # App entry point, lifespan, all routes registered
│   ├── config.py                        # Pydantic Settings — all env vars
│   ├── requirements.txt                 # Python deps (pip / uv compatible)
│   ├── Dockerfile
│   ├── .env                             # ⚠ Dev credentials (private repo — team use)
│   ├── test_pipeline.py                 # Integration tests — 8 stages, no DB required
│   │
│   ├── api/                             # Thin route controllers
│   │   ├── routes_auth.py               # /register /login /me
│   │   ├── routes_ingest.py             # /structured /freetext /vision
│   │   ├── routes_dashboard.py          # teacher/student/admin analytics
│   │   ├── routes_quiz.py               # /dispatch /submit
│   │   ├── routes_query.py              # /ask /student/{id}/insights
│   │   └── routes_websocket.py          # WS connection registry
│   │
│   ├── core/                            # Pure business logic — fully testable, no I/O
│   │   ├── ast_schema.py                # Frozen AST v2.0 schema
│   │   ├── rehydration_governor.py      # Fast/Slow lane routing
│   │   ├── pandas_validator.py          # Cross-field math checks
│   │   ├── threshold_evaluator.py       # Per-KC gap detection
│   │   ├── mastery_updater.py           # BKT bayesian_update()
│   │   ├── risk_scorer.py               # ABC composite scorer
│   │   ├── mtss_engine.py               # MTSS tier + intervention plan
│   │   ├── ticket_lifecycle.py          # 5-state intervention ticket FSM
│   │   └── knowledge_dag.py             # Neo4j Cypher + DAG propagation
│   │
│   ├── db/
│   │   ├── models.py                    # SQLAlchemy async ORM
│   │   ├── postgres.py                  # Async engine + session factory
│   │   └── neo4j_driver.py             # Async Neo4j driver singleton
│   │
│   ├── llm/
│   │   ├── gemini_client.py             # Singleton Gemini wrapper
│   │   ├── freetext_parser.py           # NL → AST via Gemini
│   │   ├── quiz_generator.py            # KC-aware quiz generation
│   │   ├── nl_to_cypher.py              # NL → safe read-only Cypher
│   │   └── prompts/                     # Prompt templates (.txt)
│   │       ├── freetext_to_ast.txt
│   │       ├── quiz_generation.txt
│   │       ├── nl_to_cypher.txt
│   │       └── vision_extraction.txt
│   │
│   ├── mcp/
│   │   └── quiz_dispatcher.py           # MCP pipeline: generate → push WS
│   │
│   ├── services/
│   │   ├── ingestion_orchestrator.py    # Master 10-step pipeline
│   │   └── dashboard_analytics.py       # Analytics aggregators
│   │
│   └── vision/
│       ├── opencv_preprocessor.py       # Grayscale → denoise → threshold → deskew
│       └── extractor.py                 # OpenCV + Gemini Vision → AST
│
├── frontend/
│   ├── next.config.mjs
│   ├── package.json / tsconfig.json / tailwind.config.ts
│   ├── Dockerfile
│   ├── .env.local.example
│   ├── messages/en.json                 # i18n strings
│   └── src/
│       ├── app/
│       │   ├── (auth)/login/            register/
│       │   ├── teacher/dashboard/       input/  query/  students/
│       │   ├── student/dashboard/       quiz/
│       │   └── admin/dashboard/
│       ├── components/
│       │   ├── shared/  app-shell  header  sidebar
│       │   ├── dashboard/  mastery-chart  risk-chart
│       │   └── ui/  button  card  badge  input  progress
│       ├── hooks/use-websocket.ts       # Typed WS hook (auto-reconnect)
│       ├── store/  auth-store  dashboard-store  (Zustand)
│       ├── lib/api.ts                   # Axios — all 17 endpoints typed
│       ├── types/index.ts               # Shared TS types (mirrors Pydantic)
│       └── middleware.ts                # Auth redirect middleware
│
├── scripts/
│   ├── seed_postgres.sql                # Demo users + sample events/tickets
│   └── seed_neo4j.cypher               # 8 KCs + prerequisite relationships
│
├── docker-compose.yml                   # Full stack: API + UI + PG + Neo4j
├── .env.example                         # Safe env template (no real secrets)
└── .gitignore
```

---

## 🚀 Quick Start

### Prerequisites
| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11+ | 3.13 recommended |
| Node.js | 18+ | 20 LTS recommended |
| PostgreSQL | 16 | or via Docker |
| Neo4j | 5 Community | or via Docker |
| Docker + Compose | 24+ | Optional (easiest path) |
| Gemini API Key | — | [Get free key →](https://aistudio.google.com/app/apikey) |

### Option A — Docker Compose (Full Stack)

```bash
git clone https://github.com/SanjayS-007/sahayak360-mvp.git
cd sahayak360-mvp

# .env is pre-filled for local dev — only update GEMINI_API_KEY
# backend/.env  →  GEMINI_API_KEY=your_key_here

docker-compose up --build

# First run: seed databases
docker-compose exec backend python -c "
import asyncio; from db.postgres import init_db; asyncio.run(init_db())"
docker-compose exec db psql -U sahayak -d sahayak360 -f /scripts/seed_postgres.sql
# Neo4j Browser → http://localhost:7474 → run scripts/seed_neo4j.cypher
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Neo4j Browser | http://localhost:7474 |

### Option B — Manual (Development)

**Backend:**
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install uv
uv pip install -r requirements.txt

# Create PostgreSQL DB
psql -U postgres -c "CREATE USER sahayak WITH PASSWORD 'sahayak_dev_2026';"
psql -U postgres -c "CREATE DATABASE sahayak360 OWNER sahayak;"
python -c "import asyncio; from db.postgres import init_db; asyncio.run(init_db())"
psql -U sahayak -d sahayak360 -f ../scripts/seed_postgres.sql

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.local.example .env.local   # default: NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev          # → http://localhost:3000
```

**Neo4j seed:**
```
Open http://localhost:7474 → authenticate → paste + run scripts/seed_neo4j.cypher
```

---

## 👥 Team Setup & Onboarding

> **Private repo** — `backend/.env` is committed with dev credentials so the team can start in minutes.

### 5-Minute New Member Setup

```bash
# 1. Clone
git clone https://github.com/SanjayS-007/sahayak360-mvp.git
cd sahayak360-mvp

# 2. Start databases (Docker)
docker-compose up -d db neo4j

# 3. Backend
cd backend
python -m venv venv && .\venv\Scripts\activate    # Windows
# source venv/bin/activate                         # Mac/Linux
pip install uv && uv pip install -r requirements.txt

python -c "import asyncio; from db.postgres import init_db; asyncio.run(init_db())"
psql -U sahayak -d sahayak360 -f ../scripts/seed_postgres.sql

uvicorn main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend && npm install && npm run dev

# 5. Verify
curl http://localhost:8000/health
# → {"status":"healthy","service":"sahayak-360-api","version":"1.0.0"}

# 6. Run pipeline tests
cd backend && python test_pipeline.py
# → 8/8 PASS
```

### Only Thing You Must Change

Open `backend/.env` and replace:
```env
GEMINI_API_KEY=test_key_placeholder
```
with your own key from https://aistudio.google.com/app/apikey

Everything else works out of the box locally.

---

## ⚙️ Environment Variables

### `backend/.env` (committed — dev defaults pre-filled)

| Variable | Dev Default | Description |
|----------|-------------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://sahayak:sahayak_dev_2026@localhost:5432/sahayak360` | Async PostgreSQL DSN |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j bolt URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `neo4j_dev_2026` | Neo4j password |
| `GEMINI_API_KEY` | `test_key_placeholder` | **Replace with your key** |
| `JWT_SECRET` | `dev_secret_key_2026` | JWT signing secret (change in prod) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRY_MINUTES` | `1440` | Token lifetime (24 hours) |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

### `frontend/.env.local`

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL |

> **Production checklist:**
> - [ ] Generate strong `JWT_SECRET`: `openssl rand -hex 32`
> - [ ] Set `CORS_ORIGINS` to your production domain
> - [ ] Use a managed PostgreSQL (RDS, Supabase, Neon)
> - [ ] Use managed Neo4j Aura or self-hosted with auth enabled
> - [ ] Rotate Gemini API key and restrict to your IP/domain

---

## 👤 Demo Accounts (after seeding)

| Role | Email | Password | Can Access |
|------|-------|----------|-----------|
| Admin | `admin@sahayak.edu` | `demo1234` | `/admin/dashboard` |
| Teacher | `teacher@sahayak.edu` | `demo1234` | All `/teacher/*` routes |
| Student | `student@sahayak.edu` | `demo1234` | `/student/*` + quiz WS |

---

## 📡 API Reference

Full interactive docs at **http://localhost:8000/docs** (Swagger UI) and **http://localhost:8000/redoc**

### Auth
| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | `{email, password, name, role}` | Register new user |
| `POST` | `/api/auth/login` | `{email, password}` | Returns JWT bearer token |
| `GET` | `/api/auth/me` | — | Current user profile |

### Ingestion
| Method | Endpoint | Auth | Body | Description |
|--------|----------|------|------|-------------|
| `POST` | `/api/ingest/structured` | Bearer | `StructuredIngestRequest` | Fast-lane JSON |
| `POST` | `/api/ingest/freetext` | Bearer | `{text: string}` | NL → pipeline |
| `POST` | `/api/ingest/vision` | Bearer | `multipart/form-data` (image) | Scan → pipeline |

**`StructuredIngestRequest` schema:**
```json
{
  "student_id": "STU001",
  "class_section": "8-A",
  "assessment_type": "formative",
  "channel": "swipe_pwa",
  "scores": [
    {
      "question_id": "Q1",
      "knowledge_component_id": "KC_FRACTIONS",
      "knowledge_component_name": "Fractions",
      "obtained_marks": 3,
      "max_marks": 10
    }
  ]
}
```

### Dashboard
| Method | Endpoint | Auth | Params | Description |
|--------|----------|------|--------|-------------|
| `GET` | `/api/dashboard/teacher/overview` | Bearer (teacher) | `?class_section=8-A` | Class risk summary |
| `GET` | `/api/dashboard/teacher/students` | Bearer (teacher) | `?class_section=8-A` | Student roster + mastery |
| `GET` | `/api/dashboard/student/mastery` | Bearer (student) | — | Personal KC mastery |
| `GET` | `/api/dashboard/admin/overview` | Bearer (admin) | — | Institution stats |

### Quiz (MCP)
| Method | Endpoint | Auth | Body | Description |
|--------|----------|------|------|-------------|
| `POST` | `/api/quiz/dispatch` | Bearer (teacher) | `{student_id, kc_ids[]}` | Generate + dispatch |
| `POST` | `/api/quiz/submit` | Bearer (student) | `{quiz_id, answers[]}` | Submit → mastery update |
| `WS` | `/ws/student/{student_id}` | Bearer (query param) | — | Real-time quiz channel |

### Query (NL-to-Cypher)
| Method | Endpoint | Auth | Body | Description |
|--------|----------|------|------|-------------|
| `POST` | `/api/query/ask` | Bearer (teacher) | `{question: string}` | NL → Cypher → answer |
| `GET` | `/api/query/student/{id}/insights` | Bearer | — | AI student insights |
| `GET` | `/api/query/class/{section}/patterns` | Bearer | — | Class gap patterns |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

---

## 🔬 10-Step Pipeline Deep Dive

### Step 1 — RehydrationGovernor
Inspects `channel` on the inbound event. `swipe_pwa` / `api_direct` → **Fast lane** (skip LLM). `freetext` / `voice` / `vision` → **Slow lane** (Gemini parse → AST).

### Step 2 — PandasValidator
Builds a DataFrame from `scores[]`. Checks:
- `obtained_marks <= max_marks` for every row
- `total_obtained_marks == sum(score.obtained_marks)`
- No null KC IDs
Raises `ValidationError` with structured diff on failure.

### Step 3 — ThresholdEvaluator
```
pct  = obtained_marks / max_marks
gap  = True  if pct < GAP_THRESHOLD (default 0.60)
```

### Step 4 — MasteryUpdater (BKT)
```
BKT Parameters:  P_LEARN=0.10  P_GUESS=0.20  P_SLIP=0.10

is_correct = (obtained_marks / max_marks) >= 0.60

if is_correct:
    posterior = P_KNOWN*(1-P_SLIP) / [P_KNOWN*(1-P_SLIP) + (1-P_KNOWN)*P_GUESS]
else:
    posterior = P_KNOWN*P_SLIP / [P_KNOWN*P_SLIP + (1-P_KNOWN)*(1-P_GUESS)]

new_mastery = posterior + (1 - posterior) * P_LEARN
```
Mastery threshold: `> 0.80 = mastered`

### Step 5 — RiskScorer (ABC)
```
Academic  (0.50) = gap_count / total_kcs * 100
Cognitive (0.25) = prerequisite_gap_depth * 10
Behavioral(0.25) = 0  [Phase 2: attendance/submission rate]
Composite = 0.50*A + 0.25*B + 0.25*C

Tiers:  LOW <35  |  MODERATE 35-54  |  HIGH 55-74  |  CRITICAL ≥75
```

### Step 6 — MTSSEngine
Maps tier to a structured intervention plan dict with concrete action lists (practice activities, referral flags, parent notification flags).

### Step 7 — TicketLifecycle
Creates `InterventionTicket` for each HIGH/CRITICAL gap:
```
States: OPEN → IN_PROGRESS → RESOLVED → CLOSED
                           ↘ ESCALATED
```

### Steps 8–10 — Persistence
```
8:  INSERT INTO assessment_events (event + scores JSON)
9:  UPSERT INTO mastery_records (student_id, kc_id) SET mastery = new_value
10: MERGE (s:Student)-[:MASTERED {level}]->(kc:KnowledgeComponent)
    + walk prerequisite chain to flag upstream KCs as at-risk
```

---

## 🗄️ Data Models

### PostgreSQL (SQLAlchemy Async ORM — `backend/db/models.py`)
```
users                   assessment_events
├── id (UUID PK)        ├── id (UUID PK)
├── email (UNIQUE)      ├── student_id
├── name                ├── class_section
├── role (ENUM)         ├── assessment_type (ENUM)
├── class_section       ├── channel
└── hashed_password     ├── raw_scores (JSONB)
                        ├── gap_results (JSONB)
mastery_records         ├── risk_score (FLOAT)
├── id (UUID PK)        ├── risk_tier
├── student_id          └── created_at
├── kc_id
├── kc_name             tickets
├── mastery (FLOAT)     ├── id (UUID PK)
└── updated_at          ├── student_id / kc_id / tier
                        ├── state (OPEN→RESOLVED)
                        ├── actions (JSONB)
                        └── created_at
```

### Neo4j Graph Schema
```
Nodes:
  (:KnowledgeComponent {id, name, subject, grade})
  (:Student {id, name, class_section})

Relationships:
  (:KnowledgeComponent)-[:PREREQUISITE_OF]->(:KnowledgeComponent)
  (:Student)-[:MASTERED {level: float, updated_at}]->(:KnowledgeComponent)
  (:Student)-[:STRUGGLING_WITH {since: datetime}]->(:KnowledgeComponent)
```

### AST Schema (`backend/core/ast_schema.py`)
```python
AssessmentEventAST:
  event_id: str            # "DEPT-MATH-8A-20260603-001"
  student_id / class_section / assessment_type / channel
  scores: List[ScoreItem]
  metadata: EventMetadata

ScoreItem:
  question_id / knowledge_component_id / knowledge_component_name
  obtained_marks / max_marks

EventMetadata:
  teacher_id / subject / total_marks / obtained_marks / duration_minutes
```

---

## 🧪 Running Tests

```bash
cd backend
python test_pipeline.py
```

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

=== 8/8 TESTS PASSED ===
```

| Test | Module | Key Assertion |
|------|--------|---------------|
| 1 | `ast_schema.py` | `StructuredIngestRequest` validates correctly |
| 2 | `ast_schema.py` | `AssessmentEventAST` constructs from scores |
| 3 | `pandas_validator.py` | Cross-field math passes; bad data raises |
| 4 | `threshold_evaluator.py` | 30% score → gap detected |
| 5 | `mastery_updater.py` | BKT update increases mastery on correct answer |
| 6 | `risk_scorer.py` | ABC composite maps to correct tier |
| 7 | `mtss_engine.py` | Tier 3 plan has `specialist_referral: true` |
| 8 | `ticket_lifecycle.py` | OPEN → IN_PROGRESS transition is valid |

No database or Gemini API key needed to run these tests.

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | FastAPI | 0.111+ |
| Server | Uvicorn (ASGI) | 0.30+ |
| Language | Python | 3.13 |
| Validation | Pydantic V2 + pydantic-settings | 2.7+ |
| ORM | SQLAlchemy async | 2.0+ |
| PostgreSQL driver | asyncpg | 0.31 |
| Graph DB | Neo4j async driver | 5.22+ |
| AI / LLM | Google Generative AI (Gemini 1.5 Flash) | 0.7+ |
| Vision | OpenCV headless + Pillow | 4.10+ / 10.3+ |
| Data processing | Pandas + NumPy | 2.2+ / 1.26+ |
| Auth | python-jose + passlib (bcrypt) | 3.3+ / 1.7+ |
| Real-time | WebSockets (FastAPI native) | 12+ |

### Frontend
| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 14.2+ |
| Language | TypeScript | 5.5 |
| Styling | Tailwind CSS | 3.4 |
| UI Components | shadcn/ui (Radix + CVA) | — |
| Charts | Recharts | 2.12 |
| State | Zustand | 4.5 |
| HTTP Client | Axios | 1.7 |
| i18n | next-intl | 3.15 |
| Animations | Framer Motion | 11 |
| Notifications | Sonner | 1.5 |

### Infrastructure
| Layer | Technology |
|-------|-----------|
| Containers | Docker + Docker Compose |
| PostgreSQL | postgres:16-alpine |
| Graph DB | neo4j:5-community |
| Package mgr | uv (Python), npm (Node) |

---

## 🔄 Development Workflow

```bash
# Feature branch workflow
git checkout -b feature/your-feature-name

# Always test before committing
cd backend && python test_pipeline.py

# Conventional Commits
git commit -m "feat: add prerequisite gap depth to cognitive risk"
git commit -m "fix: BKT prior clamped to [0.01, 0.99]"
git commit -m "docs: update API reference"
git commit -m "refactor: extract threshold config to settings"

git push origin feature/your-feature-name
# → open Pull Request targeting main
```

| Branch | Purpose |
|--------|---------|
| `main` | Stable, deployable |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `chore/*` | Tooling, deps, CI |

---

## 🚧 Roadmap

- [ ] Behavioral risk component (attendance + submission rate data)
- [ ] SMS / WhatsApp parent alerts on CRITICAL tier
- [ ] Multi-language UI — Hindi, Tamil, Telugu (next-intl slots ready)
- [ ] Offline PWA sync queue for low-connectivity schools
- [ ] Google Classroom / Moodle event import
- [ ] Longitudinal mastery trend graphs per student
- [ ] Neo4j betweenness centrality for critical KC detection
- [ ] Teacher mobile app (React Native)

---

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Run tests: `cd backend && python test_pipeline.py`
4. Commit (Conventional Commits): `git commit -m 'feat: description'`
5. Push + open a Pull Request targeting `main`

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ for educators and students everywhere

**Sahayak** (सहायक) means *helper* in Hindi

*"Every student can learn — given the right support at the right time."*

</div>
