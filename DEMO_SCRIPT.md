# Sahayak 360 — Complete Demo Walkthrough Script

> **Total target time:** 8–10 minutes  
> **Order:** Teacher → Student → Admin  
> **Demo URL:** https://sahayak360-mvp.vercel.app  
> **API Docs:** https://sahayak360-api.onrender.com/docs

---

## BEFORE YOU START — MANDATORY CHECKLIST

Do every single item below BEFORE pressing record. Skipping any of these will ruin your recording.

### 1. Wake Up the Backend (Do this 5 minutes early)
The backend runs on Render's free tier and goes to sleep after 15 minutes of inactivity. If you record while it is sleeping, every API call will fail or take 30 seconds.

1. Open a new browser tab
2. Go to: `https://sahayak360-api.onrender.com/health`
3. Wait until you see: `{"status":"ok","database":"connected"}`
4. If the page is blank or loading for more than 10 seconds — just wait. It is waking up.
5. Once you see the response, close that tab

### 2. Pre-Warm the App (Do this 3 minutes early)
1. Open `https://sahayak360-mvp.vercel.app`
2. Click the **Ms. Priya Sharma — Teacher** card to log in
3. Wait for the Teacher Dashboard to fully load (all 4 stat cards visible)
4. Click **Students** in the sidebar — wait for student list to load
5. Click back to **Dashboard**
6. Now click logout or go back to the home page
7. Click the **Aarav Patel — Student** card
8. Wait for student dashboard to load
9. Click **Quiz** in the sidebar — wait for it to load
10. Go back to home page
11. Click **Dr. Suresh Menon — Admin** card
12. Wait for admin dashboard to load
13. Go back to home page — you are now ready

**Why do this?** The app fetches data on first load. Pre-warming fills the caches so there are no loading spinners during recording.

### 3. Browser Setup
- Browser: **Google Chrome**
- Zoom level: Press `Ctrl + Shift + −` until it shows **90%** (or `Ctrl + 0` to reset to 100%, then one `Ctrl + −`)
- Full screen: Press **F11**
- Close all other tabs except the app
- Turn off browser notifications: Click the bell icon in bottom right of Windows → turn on **Do Not Disturb**
- Turn off any desktop notification software (Teams, Slack, Outlook)
- Plug in your laptop charger (prevents throttling)

### 4. Recording Software
- **Option A (recommended):** OBS Studio — free at obsproject.com. Use "Display Capture" source, set output to 1080p
- **Option B (quick):** Windows built-in — press `Win + G` → click the record button (circle icon)
- **Option C (simplest):** Loom — browser extension, records screen + camera

### 5. Audio Tips
- Speak clearly and at a pace slower than your normal speaking speed
- Keep your mic 20–30 cm from your mouth
- Do a 15-second audio test recording before starting the real one
- Silence your phone completely (not vibrate — completely silent)

### 6. Things to Have Open and Ready
- This script (on your phone, or second monitor, or printed)
- The app URL in Chrome, on the home/login page showing the Judge Preview panel
- Password written somewhere for quick reference: `Demo@2026Secure`

### 7. Do a Full Dry Run First
Go through the entire demo once without recording. Know exactly where every button is. Time yourself. Your first real recording should be your second time through the flow.

---

## OPENING — INTRODUCTION (0:00 – 0:45)

### What to Show on Screen
Keep the browser on the Sahayak 360 home page (`https://sahayak360-mvp.vercel.app`).
The page shows the login form and the **"JUDGE PREVIEW — SELECT A DEMO ACCOUNT"** panel with 3 cards.

### What to Say
> "Hi. I'm going to walk you through Sahayak 360 — an AI-powered adaptive learning and early intervention system built for Indian government schools.
>
> The system solves two problems that every school in India faces right now.
>
> First — learning gaps go undetected. A student fails a math exam. The teacher knows the score but not the specific concept that broke down, and not the root cause behind it. The student gets told to 'study more.' Nothing changes.
>
> Second — there is no early warning system. At-risk students are identified only at annual results — 8 to 10 months after the problem started. By then, it is too late.
>
> Sahayak 360 fixes both. A teacher submits an assessment in any format — structured JSON, a plain text description, or a photograph of an answer sheet. Within 4 seconds, the system identifies the root knowledge gap, dispatches a targeted quiz to the student, raises an intervention ticket for the teacher, and updates the admin's risk heatmap. All simultaneously. Zero extra work.
>
> Let me show you. I'll walk through three roles — teacher first, then student, then admin."

### Action
> *(Do not click anything yet. Let the screen rest on the home page during the intro.)*  
> *(After the last line, pause for 2 seconds, then move to Step 1.)*

---

## PART 1 — TEACHER DEMO (0:45 – 4:30)

**Who:** Ms. Priya Sharma — Class 9-A, Mathematics, 13 students  
**Story:** It is Monday morning. She wants to check her class, look at a struggling student, submit a test result, and manage her intervention tickets.

---

### Step 1 — Login as Teacher (0:45 – 1:00)

**What to do:**
1. On the home page, look at the **"JUDGE PREVIEW"** panel
2. Click the first card — **"Ms. Priya Sharma — Teacher | Class 9-A · Mathematics · 13 students"**
3. You will be automatically logged in and redirected to the Teacher Dashboard

**What to say:**
> "The app has a judge preview panel right on the home page. I'll click Ms. Priya Sharma's card to log in as a teacher — no typing needed."

**What to watch for:** The page should redirect to `/teacher/dashboard`. You will see a loading spinner briefly, then the dashboard with 4 stat cards appears.

---

### Step 2 — Teacher Dashboard (1:00 – 1:45)

**What to do:**
1. Wait for the dashboard to fully load — 4 cards in a row should appear
2. **Slowly move your mouse** across each stat card from left to right:
   - **Total Students** (should show 13)
   - **Class Avg Mastery** (should show a percentage like 56%)
   - **At-Risk Students** (shows count of high + critical risk students)
   - **Open Tickets** (should show a number like 302+)
3. Scroll down slowly to show the rest of the dashboard — there may be a class analytics section, student risk distribution, or AI-generated patterns section
4. Pause on any risk or alert section for 2 seconds

**What to say (while moving mouse across stat cards):**
> "This is the teacher dashboard. The moment Ms. Priya logs in, she sees four key numbers.
>
> Total students — 13. Class average mastery — let's say around 56 percent. At-risk students — those are the ones the system has flagged for intervention. And open tickets — over three hundred intervention tickets waiting for action.
>
> All of this is calculated live from assessment data. She didn't compile a single spreadsheet."

> *(Scroll down slowly)*
>
> "Below the cards, she can see the class-level risk distribution and any AI-detected patterns in her class — which topics are trending downward, which students are declining fastest."

---

### Step 3 — Students Page (1:45 – 2:30)

**What to do:**
1. Click **"Students"** in the left sidebar
2. Wait for the student list to load — you will see cards for each student, each with a colored left border (green for low risk, amber for high, red for critical)
3. Move your mouse slowly over 2–3 student cards to show the mastery bar inside each card
4. Find **Aarav Patel** — he has a red border (critical risk, 14% mastery)
5. Click on Aarav Patel's card
6. Wait for the student detail page to load

**What to say (on student list):**
> "The Students page lists all 13 of her students. Each card is color-coded — green border means low risk, amber means moderate, red means high or critical. The bar inside each card is the student's overall mastery percentage.
>
> Let me click on Aarav Patel — he has a red border, which means the system has flagged him as critical."

**What to do on Aarav's detail page:**
1. Wait for the page to load — it shows a radar chart, area chart, gaps, strengths, and KC breakdown
2. **Point to the radar chart** — it shows per-KC mastery in a web shape
3. **Scroll down to "Gaps" section** — shows specific KCs where Aarav is below threshold with exact percentages
4. **Look for "MTSS" badge** — it will say something like "Tier 3" or "Critical"
5. **Look for the "Dispatch Micro-Test" button** — it should be visible near the gaps section or at the top right

**What to say (on Aarav's detail page):**
> "Aarav's detail page. Look at this radar chart — it shows his mastery across every knowledge component. The closer a point is to the outer edge, the better his mastery. Most of his points are pulled toward the center — which means critical gaps everywhere.
>
> Scrolling down to the Gaps section — Linear Equations at 31 percent, Coordinate Geometry at 15 percent, Quadratic Equations at 10 percent.
>
> Here is what makes Sahayak 360 different. A traditional system would say 'Aarav failed Quadratic Equations — give him more Quadratic practice.' That is the wrong answer. The system traces the prerequisite graph in Neo4j and finds the actual root cause — Linear Equations at 31 percent. Quadratics and Coordinate Geometry failed because Linear Equations was never mastered. Fix that one, and the rest improve.
>
> His MTSS tier is Tier 3 — Crisis. That means immediate escalation and multi-agency support, not just extra homework."

---

### Step 4 — Dispatch a Quiz from Student Detail (2:30 – 3:00)

**What to do:**
1. Still on Aarav's detail page
2. Find the **"Dispatch Micro-Test"** button — it should be near the gaps list or in the top-right area
3. If there are KC checkboxes or a gap to click on — click on **"Linear Equations"** gap first to select it
4. Then click **"Dispatch Micro-Test"** button
5. Wait for the green toast notification to appear: **"Micro-test dispatched! Student will receive it in real-time."**

> **Note:** If there is no dispatch button on this page, click the **"Interventions"** page in the sidebar instead and skip directly to Step 5. Some builds may have the dispatch flow on a different page.

**What to say:**
> "Right from this page, Ms. Priya can dispatch a targeted micro-test. I'm selecting the Linear Equations gap — the root cause — and clicking Dispatch.
>
> *(wait for toast notification)*
>
> Done. The quiz was just created by Gemini AI — 5 questions on Linear Equations, calibrated to Aarav's current mastery level of 31 percent. It will appear on his device within 10 seconds through HTTP polling. The teacher didn't write a single question."

---

### Step 5 — Input Page (Assessment Ingest) (3:00 – 3:45)

**What to do:**
1. Click **"Input"** in the left sidebar (it may be labeled "Input Assessment Data" or similar)
2. You will see the page heading "Input Assessment Data" with 3 tabs:
   - **Structured Input** (Upload icon)
   - **Natural Language** (MessageSquare icon)
   - **Scan Image** (Camera icon)
3. Click the **"Natural Language"** tab (second tab)
4. A text area appears — click inside it
5. Type (or paste) this text slowly so viewers can read it:
   ```
   Aarav got 2 out of 10 in fractions and 5 out of 10 in algebra
   ```
6. Click the **Submit** / **Process** / **Analyze** button
7. Wait for the result to appear — it should show something like: event_id, gaps_detected, tickets_raised, mastery_updates

**What to say (showing 3 tabs):**
> "The Input page is where Ms. Priya submits assessment data. Three channels — Structured Input for JSON data from Google Forms or Excel, Natural Language for plain text, and Scan Image for photographs of answer sheets.
>
> Let me use Natural Language — the most accessible channel for most government school teachers."

> *(Click Natural Language tab, start typing)*
>
> "She types: 'Aarav got 2 out of 10 in fractions and 5 out of 10 in algebra.' That is it. She doesn't fill any form, choose any KC ID, or run any calculation. She just writes what she observed."

> *(Click submit, wait)*
>
> "In under 4 seconds — the 10-step pipeline runs. Gemini AI parses the text into structured data. Gap detection runs. BKT mastery is updated using Bayesian Knowledge Tracing. Risk score is recalculated. MTSS tier is assigned. An intervention ticket is raised. All data is persisted to PostgreSQL and Neo4j. All simultaneously."

**Pro tip:** While waiting for the result, count silently: "one thousand one, one thousand two..." — this fills dead air and shows viewers the system is actually processing in real-time.

---

### Step 6 — Interventions Page (Ticket Kanban Board) (3:45 – 4:30)

**What to do:**
1. Click **"Interventions"** in the left sidebar
2. The page loads a Kanban-style board with columns: **Open**, **In Progress**, **Awaiting Evidence**, **Resolved**
3. Scroll horizontally if needed to show all 4 columns
4. Find a ticket in the **Open** column — click on it to expand/open it
5. Show the ticket details: student name, KC gap, MTSS tier, ticket type (micro_test_dispatch / remediation_plan / parent_meeting)
6. Find the action buttons at the bottom of the ticket — **"Assign"** and **"Start"** should be visible
7. Click **"Start"** on one ticket to move it to **In Progress**
8. Watch the ticket card move from the Open column to In Progress column

**What to say (showing the kanban board):**
> "The Interventions page. This is the teacher's action board. Every ticket was raised automatically by the system — she did not create a single one manually.
>
> There are four stages: Open — the system just raised it. In Progress — the teacher is working on it. Awaiting Evidence — waiting for a re-test or observation to confirm improvement. Resolved — the gap has closed.
>
> Let me open this ticket."

> *(Click ticket to expand)*
>
> "Look at what a ticket contains. Student: Aarav Patel. Knowledge gap: Linear Equations at 31 percent. MTSS Tier: Tier 2 Plus — Intensive. Recommended intervention: Micro-Test Dispatch with peer tutoring follow-up.
>
> The teacher knows exactly what to do. Not a vague alert — a specific action plan."

> *(Click Start button)*
>
> "I'll move it to In Progress. The system tracks the full lifecycle — when was it raised, who acted on it, how long did resolution take. This data feeds the Admin's effectiveness analytics that we'll see in a moment."

---

### Teacher Demo Transition (4:30)

**What to say:**
> "That is the teacher experience. Now let me switch to Aarav — the student who just received that quiz we dispatched a minute ago. He's on his own device right now."

**What to do:** Go back to `https://sahayak360-mvp.vercel.app` — click the back button or navigate to the home page.

---

## PART 2 — STUDENT DEMO (4:30 – 6:30)

**Who:** Aarav Patel — Class 9-A, 14% overall mastery, Tier 3 (Critical), at-risk  
**Story:** He just received a quiz from his teacher. He also wants to practice on his own and check his analytics.

---

### Step 7 — Login as Student (4:30 – 4:40)

**What to do:**
1. On the home page, click the **"Aarav Patel — Student | Class 9-A · Mastery 14% · At risk"** card
2. Wait for student dashboard to load

**What to say:**
> "Logging in as Aarav. He's on his phone or school computer."

---

### Step 8 — Student Dashboard (4:40 – 5:10)

**What to do:**
1. Wait for the page to load — heading is **"My Progress"**
2. Point to the three summary cards:
   - **Overall Mastery** — shows the percentage with a progress bar below it
   - **Trend** — shows trending up or down arrow
   - **Assessment Count** — total number of assessments taken
3. Scroll down to show:
   - **Gaps section** — KCs where mastery is low (Linear Equations, Coordinate Geometry, etc.)
   - **Strengths section** — KCs where mastery is good

**What to say:**
> "Aarav's dashboard — called 'My Progress'. Three summary cards at the top: Overall Mastery at 14 percent with a progress bar. Trend — which direction is his mastery moving. Assessment count — how many times he's been assessed.
>
> Scrolling down — here are his gaps. Linear Equations, Quadratic Equations, Coordinate Geometry — all highlighted in red or amber. And his strengths below — the topics where he's doing well.
>
> He can see exactly where he stands, without waiting for a parent-teacher meeting or an exam result."

---

### Step 9 — Quiz Page — Taking the Dispatched Quiz (5:10 – 5:55)

**What to do:**
1. Click **"Quiz"** in the left sidebar
2. The page loads with a heading and a pending quiz list
3. There should be a pending session from the teacher (QZ-XXXXXXXX) — it shows the KC name (Linear Equations) and number of questions (5)
4. If the quiz from Step 4 is not visible yet, click the **Refresh** button (circular arrow icon) or wait 10 seconds — the page polls automatically every 10 seconds
5. Once the quiz card appears, click **"Start Quiz"** button
6. The quiz questions load one by one
7. Answer question 1: Pick **any option** (does not matter which is correct for demo purposes)
8. Click **"Next"** to go to question 2
9. Answer questions 2 and 3 similarly
10. On question 4 or 5 — pause and show the timer in the top right corner
11. After answering all questions, click **"Submit"**
12. Wait for the results screen to appear

**What to say (on quiz page, before starting):**
> "The Quiz page. Aarav's app has been polling the server every 10 seconds in the background. The quiz that Ms. Priya dispatched 3 minutes ago is already here — showing the knowledge component it targets: Linear Equations. 5 questions."

> *(Click Start Quiz)*
>
> "Let me start the quiz."

> *(Answering questions — talk through one question)*
>
> "Every question is AI-generated by Gemini 1.5 Flash — not pulled from a static question bank. Each question is calibrated to Aarav's current mastery level of 31 percent on Linear Equations. You can see a timer counting down in the corner. He has 10 minutes to complete this."

> *(After submitting all answers)*
>
> "Submitting..."

> *(On results screen)*
>
> "Instant result. Score shown. Mastery updated — if he scored poorly, the mastery drops slightly, the BKT engine reflects the new observation. If he scored well, it increases.
>
> And most importantly — for every question he got wrong, he sees the correct answer and an explanation. Not just a red X. He learns in the moment, right here."

---

### Step 10 — Practice Page (5:55 – 6:15)

**What to do:**
1. Click **"Practice"** in the left sidebar
2. The page shows available KCs to practice with mastery percentages next to each
3. Click on **Linear Equations** (or whichever KC is showing a low mastery percentage)
4. A difficulty is selected automatically, or you may see difficulty options — choose **Basic** if available
5. Click **"Generate"** or **"Start Practice"**
6. Wait for 5 practice questions to load (Gemini generates them)
7. You do NOT need to answer all 5 — show the first question on screen for a few seconds
8. Describe what you see — question text, 4 options (A/B/C/D format)

**What to say:**
> "Beyond teacher-dispatched quizzes, Aarav can also practice on his own at any time. The Practice page shows all available knowledge components with his current mastery percentage next to each one.
>
> I'll click Linear Equations — his biggest gap — and hit Generate.
>
> *(wait for questions to load)*
>
> Five new questions. Generated fresh right now by Gemini AI — not from a pre-made question bank. The difficulty is automatically set based on his 31 percent mastery on this KC. He gets explanations after each submission. And every practice session updates his BKT mastery, so the dashboard reflects his latest performance in real-time."

---

### Step 11 — Analytics Page (6:15 – 6:30)

**What to do:**
1. Click **"Analytics"** in the left sidebar
2. The page loads with: Radar chart (KC mastery spider web), Area chart (mastery trend over time), Bar chart (domain-level mastery), Gaps section, Strengths section
3. Move your mouse slowly over the radar chart
4. Then point to the trend area chart

**What to say:**
> "The Analytics page gives Aarav a complete view of his learning trajectory. The radar chart shows mastery per knowledge component — he can immediately see where he's weakest.
>
> The area chart below shows his mastery trend over time — is he improving or declining? These charts update after every single practice session and quiz. He never has to wait for exam results to know where he stands.
>
> This is data that used to be locked in a teacher's register. Now it is on his screen."

---

### Student Demo Transition (6:30)

**What to say:**
> "That is the student experience — targeted, real-time, and actionable. Now let me go up to the school level — Dr. Suresh Menon, the principal."

**What to do:** Go back to the home page.

---

## PART 3 — ADMIN DEMO (6:30 – 8:30)

**Who:** Dr. Suresh Menon — School Principal, 3 teachers, 18 students, full school visibility  
**Story:** It is before a Parent-Teacher Meeting. He wants to understand the school-wide situation before the meeting.

---

### Step 12 — Login as Admin (6:30 – 6:40)

**What to do:**
1. On the home page, click **"Dr. Suresh Menon — Admin | 3 teachers · 18 students · Full access"** card
2. Wait for admin dashboard to load — heading is **"Admin Overview"**

**What to say:**
> "Logging in as Dr. Suresh Menon, the school principal."

---

### Step 13 — Admin Dashboard (6:40 – 7:15)

**What to do:**
1. Wait for the dashboard to load — 4 stat cards across the top
2. Point to each card slowly:
   - **Teachers** — shows 3
   - **Students** — shows 18
   - **Total Events** — shows 106 (assessment events ingested)
   - **Active Interventions** — shows total open tickets across all teachers
3. Scroll down — there should be a teacher workload section showing bars or numbers per teacher
4. There may also be a risk heatmap preview or section comparison showing which sections are at risk
5. Find any **"View Analytics"** or **"Go to Analytics"** link/button — hover over it but do not click yet

**What to say:**
> "Admin Overview. Four numbers that tell Dr. Menon everything before he even looks at a single student.
>
> 3 teachers. 18 students. 106 assessment events — every test, every quiz, every input Ms. Priya submitted is tracked here. Active interventions — the total open tickets across all three teachers right now.
>
> He didn't collect any of this. Every teacher action flows up automatically."

> *(Scroll down)*
>
> "Scrolling down, he can see a summary of teacher workload and risk distribution at a glance. But let me go to the full analytics page to show the real decision-support data."

---

### Step 14 — Analytics Page — Risk Heatmap (7:15 – 7:40)

**What to do:**
1. Click **"Analytics"** in the left sidebar
2. Wait for the page to load — it has multiple sections/charts
3. Find the **Risk Distribution** section — it is a Pie Chart with 4 colors: green (Low), amber (Moderate), orange (High), red (Critical)
4. Find the **Section Comparison** or **Risk Heatmap** section — it shows per-section risk percentages (9-A, 9-B, 9-C)
5. Hover your mouse over the pie chart segments
6. Then point to the per-section numbers

**What to say (on risk pie chart):**
> "The Risk Distribution chart. Four segments: Low risk — green. Moderate — amber. High — orange. Critical — red. This is the school-wide student risk profile at this exact moment.
>
> Dr. Menon doesn't need to wait for exam season to know that some students are in critical territory. The system tells him right now."

> *(Point to section comparison)*
>
> "And here is the section comparison — or risk heatmap. Section 9-A has the highest proportion of at-risk students. This section needs attention before the others. If he allocates an additional support teacher, it should go to 9-A."

---

### Step 15 — Analytics Page — Teacher Workload (7:40 – 8:00)

**What to do:**
1. On the same Analytics page, scroll down to find the **Teacher Workload** bar chart or table
2. It should show 3 bars or rows — one per teacher:
   - Ms. Priya Sharma: high number of students and high tickets
   - Mr. Rajesh Kumar: fewer students, fewer tickets
   - Ms. Anita Desai: students present but 0 tickets
3. Move your mouse across the 3 bars/rows

**What to say:**
> "Teacher workload. Three bars — one for each teacher.
>
> Ms. Priya Sharma — the heaviest load. High number of open tickets. She is stretched thin. Across the room, Ms. Anita Desai has students but zero tickets. That is a red flag — either she is not using the system, or she has a very different student cohort.
>
> This visibility is completely new. Before this system, a principal had no way to see teacher workload distribution. Now it is a bar chart."

---

### Step 16 — Analytics Page — Intervention Effectiveness (8:00 – 8:20)

**What to do:**
1. On the same Analytics page, scroll to find the **Intervention Effectiveness** bar chart
2. It shows intervention types on the X-axis (Micro Test, Remediation, Peer Tutor, Parent Meeting) and effectiveness/count on Y-axis
3. Move your mouse over the bars

**What to say:**
> "Intervention effectiveness. Which strategies actually work for this cohort?
>
> Micro-tests are being dispatched most frequently. The chart shows estimated improvement percentages per intervention type.
>
> If parent meetings show low effectiveness, Dr. Menon can stop mandating them and switch resources to what is actually working. This is evidence-based school management — not gut feeling."

---

### Step 17 — Teachers Page — Drilldown (8:20 – 8:30)

**What to do:**
1. Click **"Teachers"** in the left sidebar
2. Wait for the teacher list to load — 3 teacher cards
3. Click on **Ms. Priya Sharma's** card
4. Wait for her teacher detail page to load — it shows her students list, per-student mastery, open ticket count per student

**What to say:**
> "The Teachers page. Three teachers. Let me drill into Ms. Priya Sharma."

> *(Click her card)*
>
> "Her full profile. Dr. Menon can see every student she is responsible for, their individual mastery percentages, how many open tickets per student. He can see that Aarav has 5 open tickets and is at the lowest mastery.
>
> From school-wide view — all the way down to a specific student's KC gap — in three clicks. That is the depth of visibility Sahayak 360 gives an administrator."

---

## CLOSING (8:30 – 9:00)

### What to Show on Screen
Navigate to `https://sahayak360-api.onrender.com/docs` — the Swagger UI opens showing all API endpoints grouped by category.

### What to Say
> "Everything you just saw is backed by a live production API. FastAPI on Python 3.13, running on Render. PostgreSQL 16 for all transactional data. Neo4j 5 for the knowledge graph that powers root cause detection. Google Gemini 1.5 Flash for quiz generation, NL parsing, and vision OCR.
>
> The system is fully documented with OpenAPI. Any school management system, any government LMS, can integrate with a single POST request.
>
> Sahayak 360 — from a teacher photographing an answer sheet to a principal making an evidence-based resource decision — in one platform, in under 4 seconds per student.
>
> Thank you."

### Final Action
> *(Stay on the API docs page for 3 seconds, then stop recording)*

---

## FULL TIMING REFERENCE

| Time | Section | Page | Action |
|------|---------|------|--------|
| 0:00 | Opening | Home page | Speak intro, do not click |
| 0:45 | Teacher login | Home page | Click Ms. Priya Sharma card |
| 1:00 | Teacher dashboard | /teacher/dashboard | Show 4 stat cards, scroll |
| 1:45 | Students page | /teacher/students | Show student list, click Aarav |
| 2:00 | Student detail | /teacher/students/[id] | Show radar chart, gaps, MTSS tier |
| 2:30 | Dispatch quiz | Same page | Click Dispatch Micro-Test on Linear Equations gap |
| 3:00 | Input page | /teacher/input | Click Natural Language tab, type text, submit |
| 3:45 | Interventions | /teacher/interventions | Show kanban, open a ticket, click Start |
| 4:30 | Transition | Home page | Navigate back |
| 4:40 | Student login | Home page | Click Aarav Patel card |
| 4:50 | Student dashboard | /student/dashboard | Show My Progress, gaps, strengths |
| 5:10 | Quiz page | /student/quiz | Show pending quiz, take it, submit, see results |
| 5:55 | Practice page | /student/practice | Select Linear Equations, generate questions |
| 6:15 | Analytics page | /student/analytics | Show radar chart, trend area chart |
| 6:30 | Transition | Home page | Navigate back |
| 6:40 | Admin login | Home page | Click Dr. Suresh Menon card |
| 6:50 | Admin dashboard | /admin/dashboard | Show 4 KPI cards, scroll |
| 7:15 | Analytics — heatmap | /admin/analytics | Show risk pie chart, section comparison |
| 7:40 | Analytics — workload | Same page | Scroll to teacher workload chart |
| 8:00 | Analytics — effectiveness | Same page | Scroll to intervention effectiveness chart |
| 8:20 | Teachers drilldown | /admin/teachers | Click Ms. Priya, show student list |
| 8:30 | Closing | API docs | Show Swagger UI, speak closing |
| 9:00 | Stop recording | — | Done |

---

## TEXT TO PASTE IN THE NATURAL LANGUAGE DEMO

Copy this exactly when you reach the Input page in Step 5:

```
Aarav got 2 out of 10 in fractions and 5 out of 10 in algebra
```

---

## RECOVERY SCRIPTS — WHAT TO SAY IF THINGS GO WRONG

### If a page shows a loading spinner for more than 5 seconds
> "The backend is processing — it's doing a live database query across PostgreSQL and Neo4j, so give it just a moment..."
> *(Stay calm, do not apologize. Let it load.)*

### If a page shows an error message (like "Failed to load")
> "Let me refresh this quickly."
> *(Press F5 to reload the page, then re-login using the Judge Preview panel)*

### If the quiz from Teacher demo does not appear on the Student quiz page
> "The system polls every 10 seconds — let me refresh manually."
> *(Click the Refresh button on the Quiz page, or press F5)*
> "There it is."

### If you click the wrong sidebar item
> "Let me go back to..."
> *(Just click the correct sidebar item. Do not apologize. Keep going.)*

### If you lose your place in the script
> "Let me show you something I think is particularly interesting here..."
> *(Look at this document, find where you are, continue from there)*

### If the backend is clearly down (every page errors)
> "The Render backend may have gone to sleep — I'll wake it up and we can continue."
> *(Open a new tab: https://sahayak360-api.onrender.com/health — wait for OK response — come back and refresh)*

---

## KEY THINGS TO EMPHASIZE THROUGHOUT

These are the 5 core differentiators. Mention at least 3 of them during your recording:

1. **Root cause, not symptom** — The system traces Neo4j prerequisite graph. It does not just say "failed Quadratics." It finds that Linear Equations is the root cause.

2. **Zero extra teacher work** — Three input channels. The teacher photographs or types. The system does everything else. The 10-step pipeline runs automatically.

3. **Under 4 seconds** — Assessment submitted → student gets quiz + teacher gets ticket + admin sees heatmap. All in one pipeline, under 4 seconds.

4. **BKT over raw scores** — Bayesian Knowledge Tracing is more accurate than raw percentage. A student who guesses correctly has lower true mastery than one who answers correctly without guessing. BKT accounts for this.

5. **Evidence-based admin decisions** — The admin does not rely on gut feeling. The effectiveness chart shows which interventions actually resolve gaps. The workload chart shows distribution problems. Data drives decisions.

---

## SCRIPT FOR WHEN SOMEONE ASKS "WHY NOT JUST USE EXCEL OR GOOGLE FORMS?"

> "Google Forms gives you a score. Sahayak 360 gives you a Bayesian probability of mastery per knowledge component, traces the prerequisite chain to find the root cause, classifies the student into an MTSS intervention tier, generates a targeted quiz for them, and notifies the teacher and admin — all from the same input. The forms just gave you a number. This gives you an action."

---

## THINGS NOT TO SAY

- Do NOT say "hopefully this works" — it sounds unprepared
- Do NOT say "sorry for the loading time" — it draws attention to it
- Do NOT say "as you can see" repeatedly — find varied phrases
- Do NOT read numbers off the screen robotically — describe what the numbers mean
- Do NOT rush through the navigation — slow and deliberate looks more confident than fast and frantic

---

*Demo prepared for Sahayak 360 — SIH 2025. Live at https://sahayak360-mvp.vercel.app*
