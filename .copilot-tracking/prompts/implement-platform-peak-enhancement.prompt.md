---
mode: agent
model: Claude Sonnet 4
---

<!-- markdownlint-disable-file -->

# Implementation Prompt: Sahayak 360 — Peak Platform Enhancement

## Context

You are implementing a comprehensive enhancement of the Sahayak 360 educational platform. The platform already has powerful backend engines (ABC Risk Scorer, MTSS Engine, BKT Mastery, Ticket Lifecycle, Knowledge DAG, NL-to-Cypher, Adaptive Quiz Generation) that are built and running but NOT exposed in the frontend. Your job is to surface these capabilities through polished UI/UX.

**Challenge Statements Being Solved:**
1. Learning Gaps & Timely Feedback — for teachers and students in large classrooms
2. School Decision-Making & Early Intervention — for school leaders, administrators, teachers

**Key Principles:**
- LOW teacher burden (1-click actions, auto-generated plans)
- TIMELY feedback (real-time WebSocket, immediate quiz dispatch)
- ACTIONABLE insights (not just numbers — severity labels, recommendations, AI narratives)
- CLOSED-LOOP tracking (detect → act → verify → measure effectiveness)

## Implementation Instructions

### Step 1: Create Changes Tracking File

You WILL create `20260604-platform-peak-enhancement-changes.md` in #file:../changes/ if it does not exist.

### Step 2: Execute Implementation

You WILL follow #file:../../.github/instructions/task-implementation.instructions.md
You WILL systematically implement #file:../plans/20260604-platform-peak-enhancement-plan.instructions.md task-by-task
You WILL follow ALL project standards and conventions

**Implementation Order** (respect dependencies):

```
BACKEND FIRST (Phase 1.1 → 1.4):
1. Create backend/api/routes_alerts.py with all alert + ticket + risk + MTSS endpoints
2. Register router in backend/main.py
3. Test endpoints respond correctly

FRONTEND CORE (Phase 1.5 → 1.9):
4. Add alertsApi functions to frontend/src/lib/api.ts
5. Update sidebar.tsx with new navigation links
6. Build /teacher/alerts page
7. Build /teacher/interventions page
8. Enhance /teacher/students/[id] page with Risk Radar + MTSS + Root Cause + Timeline
9. Build quiz dispatch modal component

AI LAYER (Phase 2):
10. Add AI insights to student detail page (use EXISTING endpoint)
11. Add class patterns to teacher dashboard (use EXISTING endpoint)
12. Enhance AI query page with rich results

ADMIN (Phase 3):
13. Create backend/api/routes_admin_analytics.py
14. Build /admin/analytics page
15. Enhance admin dashboard

STUDENT (Phase 4):
16. Build /student/goals page with mastery cards + badges
17. Add practice mode endpoint + frontend integration
18. Enhance student dashboard with AI tips

POLISH (Phase 5 — apply throughout):
19. Create skeleton.tsx component, apply everywhere
20. Add stagger animations + animated counters
21. Apply severity color system consistently
22. Add risk pulse + alert banner
23. Mobile bottom navigation
24. Final teacher dashboard enhancement
```

**CRITICAL**: If ${input:phaseStop:true} is true, you WILL stop after each Phase for user review.
**CRITICAL**: If ${input:taskStop:false} is true, you WILL stop after each Task for user review.

### Technical Guidelines

**Backend patterns (match existing code style)**:
- Use FastAPI `APIRouter()` with `Depends(get_current_user)` for auth
- Use `async/await` with `AsyncSession` for all DB queries
- Use `select()` from SQLAlchemy for queries
- Import from `db.models`, `core/*`, `auth.dependencies`
- Return Pydantic models as response

**Frontend patterns (match existing code style)**:
- Use `"use client"` directive for all pages
- Use `useState`/`useEffect` for data fetching (no React Query — match existing)
- Use `toast` from `sonner` for notifications
- Use `AppShell` wrapper with `requiredRole` prop
- Use existing UI components: Card, CardHeader, CardTitle, CardContent, Badge, Button, Input, Progress
- Use Recharts for all charts (already installed)
- Use lucide-react for all icons
- Use Tailwind CSS for all styling (no custom CSS files except globals.css)

**API client pattern** (match existing in `frontend/src/lib/api.ts`):
```typescript
export const alertsApi = {
  getAlerts: (classSection: string) =>
    api.get(`/alerts/teacher?class_section=${classSection}`),
  getTickets: (params: Record<string, string>) =>
    api.get("/alerts/tickets", { params }),
  transitionTicket: (ticketId: string, data: { new_status: string; note?: string }) =>
    api.patch(`/alerts/tickets/${ticketId}/transition`, data),
  getStudentRisk: (studentId: string) =>
    api.get(`/alerts/student-risk/${studentId}`),
  getStudentMTSS: (studentId: string) =>
    api.get(`/alerts/student-mtss/${studentId}`),
};
```

### Step 3: Cleanup

When ALL Phases are checked off (`[x]`) and completed you WILL do the following:

1. You WILL provide a markdown style link and a summary of all changes from #file:../changes/20260604-platform-peak-enhancement-changes.md to the user:

   - You WILL keep the overall summary brief
   - You WILL add spacing around any lists
   - You WILL wrap any reference to a file in a markdown style link

2. You WILL provide markdown style links to .copilot-tracking/plans/20260604-platform-peak-enhancement-plan.instructions.md, .copilot-tracking/details/20260604-platform-peak-enhancement-details.md, and .copilot-tracking/research/20260604-platform-enhancement-research.md documents. You WILL recommend cleaning these files up as well.
3. **MANDATORY**: You WILL attempt to delete .copilot-tracking/prompts/implement-platform-peak-enhancement.prompt.md

## Success Criteria

- [ ] Changes tracking file created
- [ ] All Phase 1 tasks implemented (Early Warning + Interventions)
- [ ] All Phase 2 tasks implemented (AI Intelligence Layer)
- [ ] All Phase 3 tasks implemented (Admin Decision Support)
- [ ] All Phase 4 tasks implemented (Student Empowerment)
- [ ] All Phase 5 tasks implemented (UI Polish)
- [ ] All plan items implemented with working code
- [ ] All detailed specifications satisfied
- [ ] Project conventions followed (existing patterns maintained)
- [ ] Changes file updated continuously
- [ ] Both challenge statements directly addressed with visible features
- [ ] Demo flow completable in 5 minutes
