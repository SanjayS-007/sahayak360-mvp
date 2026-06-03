# Eraser.io Architecture — Technical System Design

> Copy everything between the ``` marks below and paste into [eraser.io](https://app.eraser.io) → New Diagram → Cloud Architecture

```
title Sahayak 360 — Technical System Architecture

// ============================================================
// CLIENT LAYER
// ============================================================

Client Layer [icon: globe] {
  Next.js Frontend [icon: monitor, label: "Next.js 14 (App Router)"]
  Teacher UI [icon: layout, label: "Dashboard + Input + Query"]
  Student UI [icon: user, label: "Dashboard + Real-Time Quiz"]
  Admin UI [icon: shield, label: "Institution Overview"]
  WebSocket Client [icon: radio, label: "WS Auto-Reconnect Hook"]
}

// ============================================================
// API GATEWAY LAYER
// ============================================================

API Layer [icon: server] {
  FastAPI Server [icon: zap, label: "FastAPI + Uvicorn ASGI"]
  Auth Routes [icon: lock, label: "/api/auth (JWT HS256)"]
  Ingest Routes [icon: upload, label: "/api/ingest (3 channels)"]
  Dashboard Routes [icon: bar-chart, label: "/api/dashboard"]
  Quiz Routes [icon: help-circle, label: "/api/quiz (MCP)"]
  Query Routes [icon: search, label: "/api/query (NL→Cypher)"]
  WS Manager [icon: radio, label: "/ws/student/{id}"]
}

// ============================================================
// INGESTION & PARSING LAYER
// ============================================================

Ingestion Layer [icon: layers] {
  Rehydration Governor [icon: git-branch, label: "Fast/Slow Lane Router"]
  Freetext Parser [icon: type, label: "Gemini → AST JSON"]
  Vision Extractor [icon: camera, label: "OpenCV + Gemini Vision"]
  Pandas Validator [icon: check-square, label: "Cross-Field Math Checks"]
}

// ============================================================
// CORE PIPELINE (10 Steps — Pure Business Logic)
// ============================================================

Core Pipeline [icon: cpu] {
  Threshold Evaluator [icon: sliders, label: "Gap Detection (pct < 0.60)"]
  BKT Engine [icon: trending-up, label: "Bayesian Knowledge Tracing"]
  ABC Risk Scorer [icon: alert-triangle, label: "Composite: 0.5A + 0.25B + 0.25C"]
  MTSS Engine [icon: target, label: "Tier 1/2/2+/3 Plan Builder"]
  Ticket Factory [icon: clipboard-list, label: "5-State Intervention FSM"]
}

// ============================================================
// AI / LLM SERVICES
// ============================================================

AI Services [icon: brain] {
  Gemini Client [icon: sparkles, label: "Google Gemini 1.5 Flash"]
  Quiz Generator [icon: help-circle, label: "KC-Aware Question Gen"]
  NL to Cypher [icon: code, label: "NL → Read-Only Cypher"]
  Safety Guard [icon: shield, label: "WRITE_KEYWORDS Blocklist"]
}

// ============================================================
// DATA LAYER
// ============================================================

PostgreSQL [icon: database, label: "PostgreSQL 16 (asyncpg)"] {
  Users Table [icon: users, label: "users (UUID, role, bcrypt)"]
  Events Table [icon: file-text, label: "assessment_events (JSONB)"]
  Mastery Table [icon: trending-up, label: "mastery_records (per KC)"]
  Tickets Table [icon: clipboard, label: "tickets (5-state FSM)"]
}

Neo4j [icon: share-2, label: "Neo4j 5 (Knowledge DAG)"] {
  KC Nodes [icon: hexagon, label: "KnowledgeComponent nodes"]
  Student Nodes [icon: user, label: "Student nodes"]
  Prereq Edges [icon: arrow-right, label: "PREREQUISITE_OF relations"]
  Mastery Edges [icon: check, label: "MASTERED {level} edges"]
}

// ============================================================
// INFRASTRUCTURE
// ============================================================

Infrastructure [icon: cloud] {
  Docker Compose [icon: box, label: "Multi-Container Orchestration"]
  Uvicorn Workers [icon: activity, label: "ASGI Workers (async I/O)"]
}

// ============================================================
// CONNECTIONS — Client to API
// ============================================================

Next.js Frontend > FastAPI Server: REST (Axios)
WebSocket Client > WS Manager: WSS (real-time quiz)
Teacher UI > Ingest Routes: POST scores/text/image
Teacher UI > Query Routes: NL questions
Student UI > Dashboard Routes: GET mastery
Admin UI > Dashboard Routes: GET institution stats

// ============================================================
// CONNECTIONS — API to Ingestion
// ============================================================

Ingest Routes > Rehydration Governor: Route channel
Auth Routes > FastAPI Server: JWT verify middleware
Rehydration Governor > Pandas Validator: Fast lane (structured)
Rehydration Governor > Freetext Parser: Slow lane (NL)
Rehydration Governor > Vision Extractor: Slow lane (image)
Freetext Parser > Pandas Validator: Parsed AST
Vision Extractor > Pandas Validator: Extracted AST

// ============================================================
// CONNECTIONS — Ingestion to Core Pipeline
// ============================================================

Pandas Validator > Threshold Evaluator: Validated scores
Threshold Evaluator > BKT Engine: Gap results
BKT Engine > ABC Risk Scorer: Updated mastery
ABC Risk Scorer > MTSS Engine: Risk tier
MTSS Engine > Ticket Factory: Intervention plan

// ============================================================
// CONNECTIONS — Core Pipeline to Data Layer
// ============================================================

Ticket Factory > Events Table: Persist event
BKT Engine > Mastery Table: Upsert mastery
Ticket Factory > Tickets Table: Create tickets
BKT Engine > Mastery Edges: Sync mastery level
Threshold Evaluator > KC Nodes: Gap propagation
ABC Risk Scorer > Student Nodes: Risk annotation

// ============================================================
// CONNECTIONS — AI Services
// ============================================================

Freetext Parser > Gemini Client: Parse NL → JSON
Vision Extractor > Gemini Client: OCR + extraction
Quiz Routes > Quiz Generator: Generate questions
Quiz Generator > Gemini Client: KC-context prompt
Query Routes > NL to Cypher: Translate question
NL to Cypher > Safety Guard: Validate query
NL to Cypher > Gemini Client: NL → Cypher
Safety Guard > Neo4j: Execute read-only Cypher

// ============================================================
// CONNECTIONS — Quiz Real-Time Flow
// ============================================================

Quiz Generator > WS Manager: Push quiz payload
WS Manager > WebSocket Client: Deliver to student
Quiz Routes > BKT Engine: Score submission → mastery delta

// ============================================================
// CONNECTIONS — Dashboard Reads
// ============================================================

Dashboard Routes > Mastery Table: Aggregate mastery
Dashboard Routes > Tickets Table: Active interventions
Dashboard Routes > Events Table: Recent assessments
Query Routes > Neo4j: Prerequisite chain traversal
```

---

## Technical Workflow Summary

```
REQUEST FLOW:
  Teacher Input → FastAPI → RehydrationGovernor
    ├─ Structured JSON ──→ PandasValidator (fast, ~50ms)
    ├─ Freetext/Voice ──→ Gemini Parse → PandasValidator (~1.5s)
    └─ Image Upload ────→ OpenCV → Gemini Vision → PandasValidator (~3s)

PIPELINE FLOW (sequential, deterministic):
  PandasValidator → ThresholdEvaluator → BKT → RiskScorer → MTSS → Tickets
    └─ Steps 8-10: async persist to PostgreSQL + Neo4j

REAL-TIME FLOW:
  Teacher dispatch → Gemini generates quiz → WS push → Student answers → BKT update

QUERY FLOW:
  Teacher NL question → Gemini → Cypher → Safety check → Neo4j → Response
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Async everywhere (asyncpg, neo4j async) | Non-blocking I/O for concurrent student requests |
| Pure `core/` layer (no I/O) | Fully unit-testable without mocks |
| Fast/Slow lane split | Structured data skips LLM, saves cost + latency |
| BKT per KC (not per student) | Granular mastery tracking at topic level |
| 5-state ticket FSM | Tracks intervention lifecycle without ambiguity |
| Write-keyword guard on Cypher | Prevents NL injection from modifying graph |
| WebSocket per student | Instant quiz delivery without polling |
