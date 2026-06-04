---
applyTo: ".copilot-tracking/changes/20260604-platform-peak-enhancement-changes.md"
---

<!-- markdownlint-disable-file -->

# Task Checklist: Sahayak 360 — Peak Platform Enhancement

## Overview

Transform Sahayak 360 from a monitoring dashboard into a complete AI-powered decision-support and intervention platform by surfacing 70%+ of hidden backend capabilities through innovative, judge-winning UI/UX that directly solves both challenge statements: (1) Learning Gaps & Timely Feedback and (2) School Decision-Making & Early Intervention.

## Objectives

- Surface ALL hidden backend engines (ABC Risk, MTSS, BKT, Tickets, DAG, NL-to-Cypher) through polished frontend interfaces
- Enable teachers to go from "detect gap" → "prescribe intervention" → "track outcome" in ≤3 clicks (LOW BURDEN)
- Deliver real-time, actionable feedback to students via WebSocket micro-tests within seconds of gap detection (TIMELY FEEDBACK)
- Provide school leaders with integrated decision-support connecting learning, attendance, assessments, and interventions (DECISION SUPPORT)
- Create a closed-loop Early Warning System where risk detection → intervention → effectiveness measurement is fully automated (EARLY WARNING)
- Peak the UI with animations, severity-coded visuals, skeletons, and staggered reveals that demonstrate production-grade polish

## Research Summary

### Project Files

- `backend/core/risk_scorer.py` — ABC composite risk scoring engine (Academic 50%, Behavioral 25%, Cognitive 25%)
- `backend/core/mtss_engine.py` — MTSS tier assignment + 7 intervention types auto-generated
- `backend/core/ticket_lifecycle.py` — 7-state intervention ticket state machine
- `backend/core/mastery_updater.py` — Bayesian Knowledge Tracing (BKT) with probabilistic mastery
- `backend/core/threshold_evaluator.py` — Gap severity classification (5 levels) + auto-recommendations
- `backend/core/knowledge_dag.py` — Neo4j prerequisite chains + root-cause propagation
- `backend/services/ingestion_orchestrator.py` — 10-step pipeline (Route→Validate→Gaps→BKT→Risk→MTSS→Tickets→Persist→Mastery→Neo4j)
- `backend/llm/quiz_generator.py` — Gemini adaptive quiz generation with difficulty calibration
- `backend/mcp/quiz_dispatcher.py` — WebSocket real-time quiz delivery pipeline
- `backend/api/routes_query.py` — NL-to-Cypher + AI student insights + class patterns (2 endpoints UNUSED)
- `frontend/src/lib/api.ts` — `queryApi.studentInsights()` and `queryApi.classPatterns()` defined but NEVER called
- `frontend/src/components/shared/sidebar.tsx` — Navigation config for all 3 roles

### External References

- #file:../research/20260604-platform-enhancement-research.md — Complete codebase analysis with algorithm details, gap analysis, and innovation specs

### Standards References

- Challenge Statement 1: Learning gaps and timely feedback (teachers, students in large classrooms)
- Challenge Statement 2: School decision-making and early intervention (leaders, administrators, teachers, students)
- Key Considerations: Low teacher burden, Timely feedback, Actionable insights, Classroom integration, Student progress, Early warning, Decision support, Privacy, Reliability

## Implementation Checklist

### [ ] Phase 1: Early Warning & Alert System (Challenge 1+2 Core)

> **Solves**: Early warning, Timely feedback, Low teacher burden
> **Impact**: Teachers see at-risk students BEFORE they fail, not after

- [ ] Task 1.1: Create backend alert computation endpoint
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1-55)

- [ ] Task 1.2: Create backend ticket management endpoints (list, transition, stats)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 56-120)

- [ ] Task 1.3: Create backend student risk breakdown endpoint
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 121-165)

- [ ] Task 1.4: Create backend MTSS plan endpoint (on-demand)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 166-210)

- [ ] Task 1.5: Build Teacher Alerts page (`/teacher/alerts`)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 211-295)

- [ ] Task 1.6: Build Intervention Command Center (`/teacher/interventions`)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 296-380)

- [ ] Task 1.7: Enhance Student Detail page with ABC Risk Radar + MTSS Actions + Root Cause Flow
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 381-485)

- [ ] Task 1.8: Add Quiz Dispatch capability (teacher sends micro-test in 1 click)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 486-545)

- [ ] Task 1.9: Update sidebar navigation with Alerts + Interventions links (with live badge counts)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 546-590)

### [ ] Phase 2: AI Intelligence Layer (Challenge 1 — Actionable Insights)

> **Solves**: Actionable insights, Student progress visibility, Decision support
> **Impact**: Every page becomes "smart" with AI-generated narratives and recommendations

- [ ] Task 2.1: Integrate AI Insights card on Student Detail page (uses existing `/query/student/{id}/insights`)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 591-640)

- [ ] Task 2.2: Add Class Patterns section to Teacher Dashboard (uses existing `/query/class/{section}/patterns`)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 641-690)

- [ ] Task 2.3: Enhance AI Query page with smart suggestions + rich result cards
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 691-745)

- [ ] Task 2.4: Add AI-generated intervention recommendations to MTSS cards
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 746-790)

### [ ] Phase 3: Admin Decision Support (Challenge 2 Core)

> **Solves**: Decision support, Early warning at scale, Interoperability
> **Impact**: School leaders get integrated views connecting learning + attendance + interventions

- [ ] Task 3.1: Create backend admin analytics endpoints (section comparison, effectiveness, heatmap)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 791-860)

- [ ] Task 3.2: Build Admin Analytics page (`/admin/analytics`) with risk heatmap + section comparison
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 861-945)

- [ ] Task 3.3: Add Intervention Effectiveness dashboard (which actions work?)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 946-1010)

- [ ] Task 3.4: Enhance Admin Overview with teacher workload + alert summary
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1011-1060)

### [ ] Phase 4: Student Empowerment & Self-Paced Learning (Challenge 1 — Student Progress)

> **Solves**: Student progress visibility, Timely feedback (self-service), Classroom integration
> **Impact**: Students become active participants in their learning journey, not passive recipients

- [ ] Task 4.1: Build Student Goals & Progress page (`/student/goals`)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1061-1130)

- [ ] Task 4.2: Add Practice Mode (self-triggered adaptive quiz from gaps)
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1131-1185)

- [ ] Task 4.3: Enhance Student Dashboard with AI study tips + active intervention status
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1186-1240)

- [ ] Task 4.4: Add mastery level badges and streak tracking
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1241-1290)

### [ ] Phase 5: UI Peak Polish & Production Readiness (Both Challenges — Reliability)

> **Solves**: Reliability, Privacy, Classroom integration (mobile-ready)
> **Impact**: Every interaction feels snappy, professional, and trustworthy

- [ ] Task 5.1: Implement skeleton loading states across all pages
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1291-1335)

- [ ] Task 5.2: Add staggered card entrance animations + animated counters
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1336-1385)

- [ ] Task 5.3: Apply consistent severity color system across entire app
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1386-1430)

- [ ] Task 5.4: Risk pulse animation for critical students + alert banner
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1431-1475)

- [ ] Task 5.5: Mobile-responsive bottom navigation + touch optimizations
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1476-1520)

- [ ] Task 5.6: Enhanced Teacher Dashboard with all new data surfaced
  - Details: .copilot-tracking/details/20260604-platform-peak-enhancement-details.md (Lines 1521-1580)

## Dependencies

- **Existing Infrastructure (NO new services needed)**:
  - PostgreSQL (Render) — all models already defined
  - Neo4j — knowledge graph already populated
  - Gemini 2.5 Flash API — already integrated
  - WebSocket — already deployed and working
  - Vercel (frontend) + Render (backend) — deployment pipelines active

- **New npm packages (frontend only)**:
  - `framer-motion` (16KB) — staggered animations, page transitions
  - None for charts — Recharts already installed

- **No new backend packages** — all computation uses existing engines

## Success Criteria

### Challenge 1: Learning Gaps & Timely Feedback
- [ ] Teacher identifies at-risk student within 5 seconds of opening dashboard (alert banner)
- [ ] Gap severity is visually obvious (color-coded, not just numbers)
- [ ] Teacher prescribes intervention in 1 click (MTSS action cards)
- [ ] Student receives micro-test via WebSocket within 10 seconds of dispatch
- [ ] Mastery updates in real-time after quiz completion
- [ ] Student sees their own gaps + AI-recommended next steps

### Challenge 2: School Decision-Making & Early Intervention
- [ ] Admin sees school-wide risk heatmap (section × subject) in single view
- [ ] Intervention effectiveness measured (which actions improve mastery?)
- [ ] Teacher workload visible (ticket distribution)
- [ ] Closed-loop tracking: detect → act → verify → close
- [ ] All sensitive data accessible only through JWT-authenticated endpoints
- [ ] NL query enables non-technical leaders to ask questions in plain English

### Production Quality
- [ ] All pages load in < 2 seconds
- [ ] Skeleton states shown during loading (no blank screens)
- [ ] Animations settle within 500ms
- [ ] Error states handled gracefully (toast notifications)
- [ ] Mobile-responsive (360px minimum)
- [ ] Full demo completable in 5 minutes using demo accounts
