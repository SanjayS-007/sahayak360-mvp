# Eraser.io Architecture — Layman / Non-Technical View

> Copy everything between the ``` marks below and paste into [eraser.io](https://app.eraser.io) → New Diagram → Cloud Architecture

```
title Sahayak 360 — How It Works (Step by Step)

// ============================================================
// PHASE 1: DATA ENTRY — How assessments get into the system
// ============================================================

Phase 1: Assessment Entry [icon: clipboard] {
  Teacher App [icon: monitor, label: "Teacher's Computer / Phone"]
  Structured Form [icon: file-text, label: "Type scores in a form"]
  Voice Input [icon: mic, label: "Speak or type freely"]
  Photo Upload [icon: camera, label: "Take photo of answer sheet"]
}

// ============================================================
// PHASE 2: UNDERSTANDING — AI reads and understands the data
// ============================================================

Phase 2: AI Understanding [icon: cpu] {
  Smart Reader [icon: brain, label: "Gemini AI reads input"]
  Image Scanner [icon: scan, label: "Scans handwritten sheets"]
  Data Cleaner [icon: check-circle, label: "Checks for mistakes"]
}

// ============================================================
// PHASE 3: ANALYSIS — Finding what each student struggles with
// ============================================================

Phase 3: Student Analysis [icon: bar-chart-2] {
  Gap Finder [icon: search, label: "Finds weak topics"]
  Mastery Score [icon: trending-up, label: "Calculates how well student knows each topic"]
  Risk Calculator [icon: alert-triangle, label: "How at-risk is this student?"]
}

// ============================================================
// PHASE 4: ACTION — Deciding what help each student needs
// ============================================================

Phase 4: Intervention Planning [icon: target] {
  Support Tier [icon: layers, label: "Assigns Tier 1 / 2 / 3 support level"]
  Action Tickets [icon: clipboard-list, label: "Creates specific help tasks"]
  Quiz Generator [icon: help-circle, label: "Creates practice questions"]
}

// ============================================================
// PHASE 5: DELIVERY — Getting help to students in real time
// ============================================================

Phase 5: Real-Time Delivery [icon: send] {
  Live Quiz [icon: zap, label: "Sends quiz to student's screen instantly"]
  Teacher Dashboard [icon: layout, label: "Teacher sees class overview"]
  Student Dashboard [icon: user, label: "Student sees their progress"]
}

// ============================================================
// PHASE 6: KNOWLEDGE MAP — Connecting topics and prerequisites
// ============================================================

Phase 6: Knowledge Connections [icon: git-branch] {
  Topic Map [icon: map, label: "Shows which topics depend on others"]
  Prerequisite Alert [icon: alert-circle, label: "Warns if foundation topics are weak"]
}

// ============================================================
// FLOW: How data moves through the system
// ============================================================

// Phase 1 → Phase 2
Teacher App > Structured Form
Teacher App > Voice Input
Teacher App > Photo Upload
Structured Form > Data Cleaner: Direct path (fast)
Voice Input > Smart Reader: AI interprets
Photo Upload > Image Scanner: Scans image
Image Scanner > Smart Reader: Extracts text
Smart Reader > Data Cleaner: Standardized data

// Phase 2 → Phase 3
Data Cleaner > Gap Finder: Clean scores
Gap Finder > Mastery Score: Per-topic results
Mastery Score > Risk Calculator: Overall picture

// Phase 3 → Phase 4
Risk Calculator > Support Tier: Risk level decides tier
Support Tier > Action Tickets: Creates help tasks
Support Tier > Quiz Generator: Targets weak topics

// Phase 4 → Phase 5
Quiz Generator > Live Quiz: Pushes instantly
Action Tickets > Teacher Dashboard: Tasks to review
Risk Calculator > Teacher Dashboard: Risk overview
Mastery Score > Student Dashboard: Progress bars

// Phase 3 → Phase 6
Gap Finder > Topic Map: Maps gaps to prerequisites
Topic Map > Prerequisite Alert: Finds root causes
Prerequisite Alert > Support Tier: Informs intervention
```

---

## How to Read This Diagram

| Phase | What Happens | Who Benefits |
|-------|-------------|-------------|
| **Phase 1** | Teacher enters student marks — by typing, speaking, or photographing answer sheets | Teacher (saves time) |
| **Phase 2** | AI reads the input, scans images, checks for errors | System (ensures accuracy) |
| **Phase 3** | System finds which topics each student is weak in, scores their mastery, and calculates risk | Teacher + Student |
| **Phase 4** | Decides support level (mild → intensive) and creates specific action items | School leadership |
| **Phase 5** | Delivers practice quizzes to students live, shows dashboards to all users | Everyone |
| **Phase 6** | Maps topic dependencies — if a student is weak in fractions, checks if they know division first | Teacher + Student |
