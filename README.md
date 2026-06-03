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
[![Tests](https://img.shields.io/badge/Pipeline_Tests-8%2F8_PASS-brightgreen?style=for-the-badge)](#-running-tests)

---

**Sahayak 360** ingests student assessments via **structured JSON**, **natural language**, or **scanned answer sheet photos** and within 4 seconds runs a **10-step cognitive pipeline** — detecting learning gaps, computing Bayesian mastery, assigning MTSS intervention tiers, generating adaptive quizzes via Gemini AI, and delivering them in real time over WebSocket.

[Fresh Machine Setup](#-fresh-machine-setup-start-here) · [Quick Start (Manual)](#-quick-start--manual-no-docker) · [Docker (Optional)](#-docker-optional) · [Architecture](#-architecture) · [API Docs](#-api-reference) · [Tests](#-running-tests)

</div>

---

## ⚡ What It Does in 4 Seconds

```
Teacher photographs answer sheet   →   4 seconds   →   "STU-01: CRITICAL risk"
                                                       + Adaptive quiz dispatched
                                                         to student's screen NOW
```

- **3 input channels:** typed JSON, natural language, photo of answer sheet
- **BKT (Bayesian Knowledge Tracing):** mastery as probability, not just percentage
- **Neo4j knowledge graph:** finds ROOT prerequisite gaps, not just symptoms
- **MTSS Tier 1/2/3** intervention plans generated automatically
- **WebSocket delivery:** quiz appears on student's device within 5 seconds of teacher click
- **8/8 pipeline tests pass** with zero database or API key needed

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

## 👤 Demo Login Accounts

| Role | Email | Password | Access |
|------|-------|----------|--------|
| **Teacher** | `teacher@sahayak.edu` | `demo1234` | Class dashboard, ingest, query, quiz dispatch |
| **Student** | `student@sahayak.edu` | `demo1234` | Personal mastery, real-time quiz |
| **Admin** | `admin@sahayak.edu` | `demo1234` | Institution overview |

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
  │  assessment_events│  │  Knowledge DAG   │  │  1.5 Flash API     │
  │  mastery_records │  │  PREREQUISITE_OF │  │  freetext→AST      │
  │  tickets / users │  │  MASTERED edges  │  │  vision→AST        │
  └─────────────────┘  └──────────────────┘  │  quiz generation   │
                                              └────────────────────┘
```

---

## ✨ Features

### 📥 Multi-Channel Ingestion
| Channel | Endpoint | Processing | Latency |
|---------|----------|-----------|---------|
| Structured JSON | `POST /api/ingest/structured` | Direct AST validation | ~50ms |
| Freetext / Voice | `POST /api/ingest/freetext` | Gemini 1.5 Flash → AST | ~1.5s |
| Vision / OCR | `POST /api/ingest/vision` | OpenCV → Gemini Vision → AST | ~3s |

### 🧠 10-Step Pipeline
```
Step 1:  Route          → Fast lane (JSON) or Slow lane (AI-parsed)
Step 2:  Validate       → Pandas cross-field math + anomaly detection
Step 3:  Gap Detection  → Per-KC threshold (default 60%)
Step 4:  Mastery Update → BKT bayesian_update() per Knowledge Component
Step 5:  Risk Scoring   → ABC composite: 50% Academic + 25% Behavioral + 25% Cognitive
Step 6:  MTSS Plan      → Tier 1/2/2+/3 assignment + structured intervention actions
Step 7:  Tickets        → Intervention tickets with 5-state lifecycle
Step 8:  Persist Event  → PostgreSQL async upsert
Step 9:  Upsert Mastery → Per-student per-KC mastery record
Step 10: Neo4j Sync     → Knowledge DAG update + prerequisite chain propagation
```

---

## 📡 API Reference

Full interactive docs at **http://localhost:8000/docs**

### Auth
| Method | Endpoint | Body |
|--------|----------|------|
| `POST` | `/api/auth/register` | `{email, password, name, role}` |
| `POST` | `/api/auth/login` | `{email, password}` → returns JWT |
| `GET` | `/api/auth/me` | — |

### Ingestion — Minimal body example
```json
{
  "teacher_id": "TCH-01",
  "student_id": "STU-01",
  "class_section": "8-A",
  "subject": "mathematics",
  "department_id": "DEPT-MATH",
  "assessment_type": "formative",
  "max_score": 30,
  "total_obtained": 12,
  "items": [
    {
      "question_id": "Q1",
      "knowledge_component_id": "KC-MATH-FRAC-01",
      "knowledge_component_name": "Basic Fractions",
      "max_marks": 10,
      "obtained_marks": 3
    }
  ]
}
```

### Dashboard
| Endpoint | Auth | Returns |
|----------|------|---------|
| `GET /api/dashboard/teacher/overview?class_section=8-A` | teacher | Risk heatmap |
| `GET /api/dashboard/student/mastery` | student | KC mastery bars |
| `GET /api/dashboard/admin/overview` | admin | Institution stats |

### Quiz (WebSocket)
| Method | Endpoint | Notes |
|--------|----------|-------|
| `POST` | `/api/quiz/dispatch` | `{student_id, kc_ids[], num_questions}` |
| `POST` | `/api/quiz/submit` | `{session_id, responses[]}` |
| `WS` | `/ws/student/{id}?token=JWT` | Real-time quiz delivery |

---

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| `(venv) not showing` — ModuleNotFoundError | Run `.\venv\Scripts\activate` before any python command |
| `database 'sahayak360' does not exist` | Run steps in [Backend Setup](#2-backend-setup) from `psql -U postgres -c "CREATE USER..."` |
| `ServiceUnavailable: bolt://localhost:7687` | Neo4j is not running — open Neo4j Desktop and click Start |
| `GEMINI_API_KEY not configured` | Edit `backend/.env`, replace `test_key_placeholder` with your real key |
| `npm install` hangs | Run `npm cache clean --force` then retry |
| Port 8000 already in use | `netstat -ano \| findstr :8000` → `taskkill /PID <number> /F` |
| Port 3000 already in use | `npm run dev -- --port 3001` |
| `psql is not recognized` | PostgreSQL bin folder not in PATH — restart PowerShell after install, or add `C:\Program Files\PostgreSQL\16\bin` to system PATH |

---

## 📁 Project Structure

```
sahayak-360/
├── backend/
│   ├── main.py                    # FastAPI app entry, all routes registered
│   ├── config.py                  # Pydantic Settings — all env vars
│   ├── requirements.txt           # 18 Python dependencies
│   ├── .env                       # Dev credentials (private repo)
│   ├── test_pipeline.py           # 8 tests — no DB/API key needed
│   ├── api/                       # Route controllers (thin layer)
│   ├── core/                      # Pure business logic — fully testable
│   │   ├── ast_schema.py          # Frozen AST v2.0 (Pydantic V2)
│   │   ├── mastery_updater.py     # BKT bayesian_update()
│   │   ├── risk_scorer.py         # ABC composite scorer
│   │   ├── mtss_engine.py         # MTSS tier + intervention plans
│   │   └── ...
│   ├── db/                        # SQLAlchemy async ORM + Neo4j driver
│   ├── llm/                       # Gemini client + prompts
│   ├── mcp/quiz_dispatcher.py     # MCP pipeline: generate → PostgreSQL → WebSocket
│   ├── services/                  # Ingestion orchestrator (10 steps)
│   └── vision/                    # OpenCV preprocessor + extractor
│
├── frontend/
│   ├── package.json
│   ├── .env.local.example
│   └── src/app/
│       ├── (auth)/login/  register/
│       ├── teacher/dashboard/  input/  query/  students/
│       ├── student/dashboard/  quiz/
│       └── admin/dashboard/
│
├── scripts/
│   ├── seed_postgres.sql          # Demo users + events + tickets
│   └── seed_neo4j.cypher          # 8 KCs + prerequisite chains + 5 students
│
├── docs/
│   ├── eraser-architecture-layman.md
│   ├── eraser-architecture-technical.md
│   ├── presentation-complete.md   # 23-slide PPT script
│   └── technical-deep-dive-defense.md  # Judge Q&A preparation
│
└── docker-compose.yml             # Optional full-stack containers
```

---

## 🛠️ Full Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend framework | FastAPI | 0.111+ |
| ASGI server | Uvicorn | 0.30+ |
| Language | Python | 3.13 |
| Validation | Pydantic V2 + pydantic-settings | 2.7+ |
| ORM | SQLAlchemy async | 2.0+ |
| Relational DB driver | asyncpg | 0.29+ |
| Graph DB driver | Neo4j async | 5.22+ |
| AI / LLM | Google Generative AI (Gemini 1.5 Flash) | 0.7+ |
| Computer Vision | OpenCV headless + Pillow | 4.10+ |
| Data processing | Pandas + NumPy | 2.2+ / 1.26+ |
| Auth | python-jose + passlib (bcrypt) | — |
| Frontend framework | Next.js 14 (App Router) | 14.2+ |
| Frontend language | TypeScript | 5.5 |
| Styling | Tailwind CSS + shadcn/ui | 3.4 |
| Charts | Recharts | 2.12 |
| State | Zustand | 4.5 |
| HTTP client | Axios | 1.7 |
| Containers | Docker + Docker Compose | optional |

---

## 🚧 Roadmap

- [ ] Behavioral risk from attendance + submission rate
- [ ] SMS / WhatsApp parent alerts on CRITICAL tier
- [ ] Hindi, Tamil, Telugu UI (next-intl slots already wired)
- [ ] Offline PWA sync queue for low-connectivity schools
- [ ] Google Classroom / Moodle import
- [ ] Longitudinal mastery trend graphs
- [ ] Teacher mobile app (React Native)

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built for educators and students in India

**Sahayak** (सहायक) means *helper* in Hindi

*"Every student can learn — given the right support at the right time."*

</div>
