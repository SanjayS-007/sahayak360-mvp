<div align="center">

# 🎓 SAHAYAK 360

### AI-Powered Educational Analytics & Intervention Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5-008CC1?style=for-the-badge&logo=neo4j)](https://neo4j.com)
[![Gemini](https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Sahayak 360** is a full-stack, AI-driven educational intelligence platform that ingests student assessment data through structured, natural language, and vision channels — then runs a 10-step cognitive pipeline to detect learning gaps, compute Bayesian mastery scores, assign risk tiers, generate MTSS intervention plans, and dispatch adaptive micro-quizzes in real time.

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Docs](#-api-reference) · [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

### 📥 Multi-Channel Assessment Ingestion
| Channel | Description |
|---------|-------------|
| **Structured** | JSON form submission from SwipePWA — fastest path |
| **Freetext** | Teacher narrates in natural language → Gemini parses to AST |
| **Vision/OCR** | Scan answer sheets → OpenCV preprocess + Gemini Vision → AST |

### 🧠 10-Step Cognitive Pipeline
Each assessment event triggers a fully automated backend pipeline:

```
1. Route          → Fast lane (structured) or Slow lane (AI-parsed)
2. Validate       → Pandas cross-field math checks + anomaly detection  
3. Gap Detection  → Threshold evaluator per Knowledge Component
4. Mastery Update → Bayesian Knowledge Tracing (BKT) per KC
5. Risk Scoring   → ABC composite score (Academic 50% + Behavioral 25% + Cognitive 25%)
6. MTSS Plan      → Multi-Tiered System of Support — Tier 1/2/3 assignment
7. Tickets        → Intervention ticket factory with state machine lifecycle
8. Persist Event  → PostgreSQL async write
9. Upsert Mastery → Mastery record updates in PostgreSQL
10. Neo4j Sync    → Knowledge DAG update (prerequisite chain propagation)
```

### 📊 Role-Based Dashboards
- **Teacher** — Class risk overview, struggling KC heatmap, student roster with mastery trends
- **Student** — Personal mastery by KC, gap recommendations, quiz history  
- **Admin** — Institution-wide teacher/student counts, active interventions

### ⚡ Real-Time Quiz Engine (MCP)
- Teacher triggers micro-test for a student or class
- Gemini generates contextual questions per Knowledge Component
- WebSocket delivers quiz directly to student's browser in real time
- Submission scores BKT mastery deltas and closes the intervention loop

### 🔍 NL-to-Cypher Query Interface
- Teachers ask natural language questions about learning gaps
- Gemini converts to safe read-only Cypher queries
- Neo4j knowledge DAG answers prerequisite chain queries

### 🛡️ Security
- JWT-based auth (HS256, configurable expiry)  
- Role-based route guards (`teacher` / `student` / `admin`)
- WRITE_KEYWORDS blocked in NL-to-Cypher safety layer
- Pydantic V2 strict schema validation at every ingestion boundary

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 14)                    │
│  /login  /register  /teacher/*  /student/*  /admin/dashboard    │
│  Zustand auth store │ Axios API client │ Recharts │ shadcn/ui    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST + WebSocket
┌──────────────────────────────▼──────────────────────────────────┐
│                         BACKEND (FastAPI)                         │
│                                                                   │
│  /api/auth    /api/ingest    /api/dashboard                      │
│  /api/query   /api/quiz      WebSocket /ws/student/{id}          │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              INGESTION ORCHESTRATOR (10 Steps)           │    │
│  │  AST Schema → Pandas Validator → Threshold Evaluator    │    │
│  │  → BKT Mastery → ABC Risk → MTSS Plan → Tickets         │    │
│  │  → Persist Event → Upsert Mastery → Neo4j Sync          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐    │
│  │  Gemini    │  │  OpenCV    │  │  MCP Quiz Dispatcher    │    │
│  │  (LLM)     │  │  (Vision)  │  │  + WS Delivery Engine  │    │
│  └────────────┘  └────────────┘  └────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼─────────────────────┐
          ▼                    ▼                       ▼
  ┌───────────────┐   ┌───────────────┐   ┌──────────────────┐
  │  PostgreSQL   │   │    Neo4j      │   │  Google Gemini   │
  │  (Async)      │   │  Knowledge    │   │  1.5 Flash       │
  │  Events       │   │  DAG          │   │  (LLM + Vision)  │
  │  Mastery      │   │  Prerequisites│   │                  │
  │  Tickets      │   │  Student KCs  │   │                  │
  └───────────────┘   └───────────────┘   └──────────────────┘
```

---

## 📁 Project Structure

```
sahayak-360/
├── backend/
│   ├── main.py                    # FastAPI app entry point + lifespan
│   ├── config.py                  # Pydantic Settings (env vars)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── api/
│   │   ├── routes_auth.py         # JWT login/register/me
│   │   ├── routes_ingest.py       # 3 ingestion channels
│   │   ├── routes_dashboard.py    # Teacher/Student/Admin analytics
│   │   ├── routes_quiz.py         # MCP dispatch + submission
│   │   ├── routes_query.py        # NL-to-Cypher query interface
│   │   └── routes_websocket.py    # Real-time WS manager
│   ├── auth/
│   │   ├── jwt_handler.py         # Token create/verify
│   │   ├── password.py            # bcrypt hash/verify
│   │   └── dependencies.py        # get_current_user FastAPI dep
│   ├── core/
│   │   ├── ast_schema.py          # Frozen AST schema (v2.0)
│   │   ├── rehydration_governor.py # Fast/Slow lane routing
│   │   ├── pandas_validator.py    # Cross-field math checks
│   │   ├── threshold_evaluator.py # Gap detection engine
│   │   ├── mastery_updater.py     # BKT Bayesian updater
│   │   ├── risk_scorer.py         # ABC composite risk
│   │   ├── mtss_engine.py         # MTSS Tier plan builder
│   │   ├── ticket_lifecycle.py    # Intervention state machine
│   │   └── knowledge_dag.py       # Neo4j Cypher + DAG queries
│   ├── db/
│   │   ├── models.py              # SQLAlchemy async ORM models
│   │   ├── postgres.py            # Async engine + session factory
│   │   └── neo4j_driver.py        # Neo4j async driver singleton
│   ├── llm/
│   │   ├── gemini_client.py       # Singleton Gemini API wrapper
│   │   ├── freetext_parser.py     # NL → AST via Gemini
│   │   ├── quiz_generator.py      # KC-aware question generation
│   │   └── nl_to_cypher.py        # NL → safe Cypher
│   ├── mcp/
│   │   └── quiz_dispatcher.py     # MCP pipeline + WS delivery
│   ├── services/
│   │   ├── ingestion_orchestrator.py  # 10-step master pipeline
│   │   └── dashboard_analytics.py    # Aggregated analytics
│   └── vision/
│       ├── extractor.py           # OpenCV + Gemini Vision → AST
│       └── opencv_preprocessor.py # Image enhancement pipeline
│
├── frontend/
│   ├── next.config.mjs
│   ├── package.json
│   └── src/
│       ├── app/
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   └── register/page.tsx
│       │   ├── teacher/
│       │   │   ├── dashboard/page.tsx
│       │   │   ├── input/page.tsx    # 3-tab input (structured/freetext/vision)
│       │   │   ├── query/page.tsx    # NL query interface
│       │   │   └── students/page.tsx # Student roster + profiles
│       │   ├── student/
│       │   │   ├── dashboard/page.tsx
│       │   │   └── quiz/page.tsx     # Real-time quiz UI
│       │   └── admin/
│       │       └── dashboard/page.tsx
│       ├── components/
│       │   ├── shared/app-shell.tsx  # Role-based layout wrapper
│       │   ├── charts/              # Recharts wrappers
│       │   └── ui/                  # shadcn/ui primitives
│       ├── lib/
│       │   ├── api.ts               # Axios API client (all endpoints)
│       │   └── utils.ts
│       ├── store/
│       │   └── auth-store.ts        # Zustand auth state
│       └── types/index.ts           # Shared TypeScript types
│
├── scripts/
│   ├── seed_postgres.sql            # Demo users, events, tickets
│   └── seed_neo4j.cypher            # Knowledge graph seed
├── docs/
├── docker-compose.yml
└── .env.example
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 16** (or Docker)
- **Neo4j 5 Community** (or Docker)
- **Google Gemini API Key** — [Get one free](https://aistudio.google.com/app/apikey)

### Option A: Docker Compose (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/SanjayS-007/sahayak360-mvp.git
cd sahayak360-mvp

# 2. Copy and configure environment
cp .env.example .env
# Edit .env — set GEMINI_API_KEY and JWT_SECRET

# 3. Start everything
docker-compose up --build

# 4. Seed the database (first run only)
docker-compose exec backend python -c "
from db.postgres import engine; from db.models import Base; import asyncio
asyncio.run(engine.begin().__aenter__().__anext__().run_sync(Base.metadata.create_all))"

psql -U sahayak -d sahayak360 -f scripts/seed_postgres.sql
# In Neo4j Browser (localhost:7474): run scripts/seed_neo4j.cypher
```

- **Frontend** → http://localhost:3000  
- **Backend API** → http://localhost:8000  
- **Swagger Docs** → http://localhost:8000/docs  
- **Neo4j Browser** → http://localhost:7474  

---

### Option B: Manual Setup

#### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (uses uv if available, else pip)
pip install -r requirements.txt
# OR with uv (faster):
uv pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env — see Environment Variables section below

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Development server
npm run dev

# Production build
npm run build && npm start
```

#### 3. Seed the Database

```bash
# PostgreSQL — creates demo users, events, tickets
psql -U <your_user> -d sahayak360 -f scripts/seed_postgres.sql

# Neo4j — creates knowledge graph with 8 KCs + prerequisites
# Open Neo4j Browser at http://localhost:7474
# Paste and run the contents of scripts/seed_neo4j.cypher
```

---

## ⚙️ Environment Variables

Create `backend/.env` (copy from `.env.example`):

```env
# ─── PostgreSQL ───────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://sahayak:yourpassword@localhost:5432/sahayak360

# ─── Neo4j ────────────────────────────────────────────────────
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword

# ─── Google Gemini AI ─────────────────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here   # Get free at aistudio.google.com

# ─── JWT Authentication ───────────────────────────────────────
JWT_SECRET=change_this_to_a_secure_random_string_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=1440   # 24 hours

# ─── CORS ─────────────────────────────────────────────────────
CORS_ORIGINS=http://localhost:3000
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 👤 Demo Accounts (after seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@sahayak.edu | demo1234 |
| Teacher | teacher@sahayak.edu | demo1234 |
| Student | student@sahayak.edu | demo1234 |

---

## 📡 API Reference

Full interactive docs at **http://localhost:8000/docs**

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login → JWT token |
| `GET`  | `/api/auth/me` | Get current user profile |

### Ingestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ingest/structured` | Fast lane — JSON assessment data |
| `POST` | `/api/ingest/freetext` | Slow lane — natural language input |
| `POST` | `/api/ingest/vision` | Vision — upload answer sheet image |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dashboard/teacher/overview?class_section=8-A` | Class risk summary |
| `GET` | `/api/dashboard/teacher/students?class_section=8-A` | Student roster + mastery |
| `GET` | `/api/dashboard/student/mastery` | Student's own KC mastery |
| `GET` | `/api/dashboard/admin/overview` | Institution-wide stats |

### Quiz (MCP)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/quiz/dispatch` | Dispatch micro-test to student |
| `POST` | `/api/quiz/submit` | Submit answers → mastery update |
| `WS`   | `/ws/student/{student_id}` | Real-time quiz delivery |

### Query
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query/ask` | NL question → Cypher → answer |
| `GET`  | `/api/query/student/{id}/insights` | AI insights for student |
| `GET`  | `/api/query/class/{section}/patterns` | Class-wide gap patterns |

---

## 🧪 Running Tests

```bash
cd backend

# Core pipeline integration test (no DB required)
python test_pipeline.py

# Expected output:
# TEST 1: StructuredIngestRequest validation ... PASS
# TEST 2: AssessmentEventAST construction ..... PASS
# TEST 3: Pandas cross-field validation ....... PASS
# TEST 4: Threshold evaluator ................. PASS
# TEST 5: Bayesian Knowledge Tracing (BKT) .... PASS
# TEST 6: ABC Risk scorer ..................... PASS
# TEST 7: MTSS engine ......................... PASS
# TEST 8: Ticket lifecycle state machine ...... PASS
```

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.111 + Uvicorn |
| Language | Python 3.13 |
| Validation | Pydantic V2 + pydantic-settings |
| Database ORM | SQLAlchemy 2.0 async |
| PostgreSQL driver | asyncpg 0.31 |
| Graph DB | Neo4j 5 (async driver) |
| AI/LLM | Google Gemini 1.5 Flash |
| Vision | OpenCV 4.13 headless + Pillow |
| Data processing | Pandas 2.2 + NumPy |
| Auth | python-jose (JWT) + passlib (bcrypt) |
| Real-time | WebSockets (native FastAPI) |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript 5.5 |
| Styling | Tailwind CSS 3.4 |
| UI Components | shadcn/ui (Radix + CVA) |
| Charts | Recharts 2.12 |
| State | Zustand 4.5 |
| HTTP | Axios 1.7 |
| i18n | next-intl 3.15 |
| Animations | Framer Motion 11 |
| Notifications | Sonner 1.5 |
| Icons | Lucide React |

### Infrastructure
| Layer | Technology |
|-------|-----------|
| Container | Docker + Docker Compose |
| PostgreSQL | postgres:16-alpine |
| Graph DB | neo4j:5-community |

---

## 🔬 Core Algorithm Details

### Bayesian Knowledge Tracing (BKT)
```
P(L_n | correct) = P(correct|L) × P(L) / P(correct)

Parameters:
  p_learn   = 0.10  (probability of learning from attempt)
  p_guess   = 0.20  (probability of guessing correctly)
  p_slip    = 0.10  (probability of slipping despite mastery)
  p_transit = 0.05  (learning transfer rate)

Mastery threshold: > 0.80 = mastered
```

### ABC Risk Composite
```
Composite = 0.50 × Academic + 0.25 × Behavioral + 0.25 × Cognitive

Tiers:
  LOW      composite < 35
  MODERATE composite 35–54
  HIGH     composite 55–74
  CRITICAL composite ≥ 75
```

### MTSS Tier Mapping
```
LOW risk      → Tier 1 (Universal support, extended practice)
MODERATE risk → Tier 2 (Targeted small-group, peer tutoring)
HIGH risk     → Tier 2+ (Prerequisite review, parent contact)
CRITICAL risk → Tier 3 (Intensive 1:1, specialist referral)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'feat: add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ for educators and students everywhere

**Sahayak** (सहायक) means *helper* in Hindi

</div>
