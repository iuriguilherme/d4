# HYPPO Brainstorm: Hyper Personalized Planner and Organizer

**Document:** 001-planner-brainstorm.md
**Date:** 2026-03-27
**Status:** Foundation document — pre-implementation brainstorm
**Purpose:** Product roadmap and architecture decision foundation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Planning Methodology Catalogue](#2-planning-methodology-catalogue)
3. [User Archetype Definitions](#3-user-archetype-definitions)
4. [Adaptive Personalization Strategy](#4-adaptive-personalization-strategy)
5. [Feature Set: MVP to Fully Adapted](#5-feature-set-mvp-to-fully-adapted)
6. [Data Model Sketch](#6-data-model-sketch)
7. [Architecture Recommendations](#7-architecture-recommendations)
8. [Recommended Build Sequence](#8-recommended-build-sequence)
9. [Open Questions](#9-open-questions)

---

## 1. Executive Summary

HYPPO is a personal productivity web application for individuals who want a single tool that journals their past and plans their future. Its central differentiator is that it does not ask users to commit to a productivity methodology upfront — instead it begins as a minimal, frictionless interface and evolves its structure, terminology, and feature surface to mirror how each individual user actually works.

The problem HYPPO solves: most planner applications force users into a fixed paradigm (GTD, Bullet Journal, time-blocking) that may not match how they naturally think and plan. Users either abandon the tool because it feels like overhead, or they adapt themselves to the tool's model at the cost of friction. HYPPO inverts this: the tool adapts to the user.

**Core loop:**

```
User opens HYPPO → writes something (free-form)
         ↓
HYPPO observes what they wrote and how
         ↓
Over days/weeks, HYPPO infers archetype signals
         ↓
UI surfaces more of what this user actually uses
         ↓
Eventually HYPPO feels purpose-built for this user
```

**What makes this technically feasible:**
- The underlying data model is methodology-agnostic (entries, items, tags, time references)
- Methodology-specific views are rendered layers on top of the same data
- Behavioral signals (not questionnaires) drive personalization
- FastAPI backend keeps the data and logic clean and mobile-ready
- Flask/Quart web layer is thin — it renders views, it does not own data

**Target user:** An individual knowledge worker, student, or creative person who wants to build a personal productivity habit but has failed with rigid systems before.

---

## 2. Planning Methodology Catalogue

### 2.1 Getting Things Done (GTD) — David Allen

**Core philosophy:** The mind is for having ideas, not holding them. Capture everything external to the brain, process it into actionable next actions, organize by context, review regularly.

**Key components:**
- Capture (inbox — anything and everything)
- Clarify (is it actionable? what is the next action?)
- Organize (projects, contexts, someday/maybe, reference)
- Reflect (weekly review)
- Engage (actually do the work)

**Critical concept:** The "next action" — a single, physical, concrete action. Not "fix report" but "open Word and write the executive summary paragraph."

**Data structures implied:**
- Inbox (unprocessed items)
- Projects (multi-step outcomes)
- Next Actions (with contexts: @home, @computer, @phone)
- Waiting For list
- Someday/Maybe list
- Reference material (not actionable)
- Calendar (time-specific commitments only)
- Weekly Review template

**User profile it suits best:** People who are overwhelmed by many open loops, professionals managing many concurrent projects, people who think analytically and like clear taxonomies. Tends to reward those willing to invest time in the system itself.

**Signals a user might be GTD-oriented:**
- They create many short, concrete task items
- They prefix tasks with action verbs
- They use context tags (@work, @home)
- They frequently process an inbox to zero
- They do regular weekly reviews

---

### 2.2 Bullet Journal (BuJo) — Ryder Carroll

**Core philosophy:** An analog system adapted for the digital age. Rapid logging — quickly capturing thoughts, tasks, and events with minimal notation. Migration (deliberate re-evaluation of incomplete items) forces intentionality.

**Key components:**
- Rapid logging (bullets: task •, event ○, note —)
- Collections (Daily Log, Monthly Log, Future Log, custom)
- Index / table of contents
- Migration (monthly: moving unfinished tasks forward or striking them)
- Reflection (why did a task survive another month?)

**Data structures implied:**
- Daily log entries (ordered, dated, typed: task/event/note)
- Monthly log (overview of month + tasks for month)
- Future log (6-month horizon)
- Custom collections (habit trackers, book lists, project pages)
- Migration history (when an item moved, from where)

**User profile it suits best:** Creative, visual, analog-leaning people. People who like customization and feel ownership over their system. People who benefit from the reflective practice of migration. Journalers who also want task management.

**Signals a user might be BuJo-oriented:**
- They mix tasks, notes, and events freely in daily entries
- They care about the date heavily (every entry timestamped)
- They create many custom collections/lists
- They prefer a single chronological log over separate list views
- They revisit and annotate past entries

---

### 2.3 Time Blocking / Day Theming — Cal Newport

**Core philosophy:** Deep work requires defended time. Every minute of the workday should have a job assigned in advance. Themes (e.g., "Monday is admin day") reduce context-switching overhead.

**Key components:**
- Time blocks on a calendar (start time, end time, activity)
- Shutdown ritual (end-of-day review, next day plan)
- Weekly themes (optional: each day dedicated to a category)
- Overflow blocks (buffer time for the unexpected)

**Data structures implied:**
- Time blocks (start datetime, end datetime, activity label, category)
- Day template (reusable block patterns)
- Shutdown checklist
- Weekly theme map

**User profile it suits best:** People who do deep cognitive work (programmers, writers, researchers). People who feel fragmented by reactive work. People who already use calendar software heavily. Disciplined, structured personalities.

**Signals a user might be a time-blocker:**
- They add start/end times to tasks
- They plan tomorrow in advance (end of day entries)
- They create recurring blocks (lunch, exercise)
- They use duration estimates on tasks
- They view the day as a grid, not a list

---

### 2.4 Pomodoro Technique — Francesco Cirillo

**Core philosophy:** Work is done in focused 25-minute intervals (pomodoros) with short breaks. Interruptions are tracked and deferred. The technique builds focus muscle and makes estimates more accurate over time.

**Key components:**
- Pomodoro timer (25 min work / 5 min break / 15-30 min long break every 4)
- Today's task list (estimated in pomodoros)
- Interruption log
- Daily pomodoro count
- Historical tracking (how many pomodoros per task type)

**Data structures implied:**
- Task with pomodoro estimate and actual count
- Pomodoro session log (task, start time, completed/interrupted)
- Interruption record (internal/external, what it was)
- Daily summary (planned vs. actual pomodoros)

**User profile it suits best:** People who struggle with focus and procrastination. People who underestimate task duration. Students. Writers with word count resistance. Works well combined with other systems (GTD + Pomodoro is common).

**Signals a user might be Pomodoro-oriented:**
- They log time spent on tasks
- They note interruptions
- They return to the app during work sessions (check-ins)
- They use the app at regular short intervals throughout the day
- They care about "how long did this actually take?"

---

### 2.5 OKRs at Personal Scale — John Doerr

**Core philosophy:** Objectives (aspirational, qualitative) and Key Results (measurable, verifiable). Originally corporate but powerful for individuals setting meaningful goals. Cadence: quarterly objectives, weekly check-ins on key results.

**Key components:**
- Objectives (3-5 per quarter, inspiring, directional)
- Key Results (2-4 per objective, measurable, binary or scalar)
- Weekly confidence rating (0-100% chance of hitting KR)
- Quarterly retrospective
- Stretch goal culture (70% achievement = success)

**Data structures implied:**
- Objective (title, description, quarter, status)
- Key Result (title, metric type, start value, target value, current value, due date)
- Weekly check-in (objective, key result updates, blockers, confidence)
- Quarter retrospective (what worked, what didn't, carry-forward)

**User profile it suits best:** People with ambitious medium-term goals. People coming from corporate environments familiar with OKRs. People who want their daily work to connect to larger purpose. Goal-oriented over process-oriented.

**Signals a user might be OKR-oriented:**
- They write goals with measurable outcomes ("run 5km" not "get fit")
- They think in quarterly time horizons
- They do regular progress check-ins on goals
- They connect daily tasks to goals ("this is for Q2 Objective 1")
- They write retrospectives

---

### 2.6 Ivy Lee Method

**Core philosophy:** Radical simplicity and prioritization. At the end of each day, write the six most important things to accomplish tomorrow. Order them by priority. Work through them in order. Move unfinished items to the next day's list. Repeat.

**Key components:**
- End-of-day planning ritual (exactly 6 tasks, no more)
- Strict priority ordering (not just a list — an ordered list)
- Single-task focus (finish #1 before starting #2)
- Carryover mechanism

**Data structures implied:**
- Daily task list (exactly 6 slots, ordered 1-6)
- Task (title, date, status: done/carried-over)
- Carryover history (how many times this task has been moved)

**User profile it suits best:** People who are overwhelmed by long to-do lists. People who struggle with prioritization paralysis. People who want simplicity over sophistication. People who benefit from a physical/ritual aspect to planning.

**Signals a user might be Ivy-Lee-oriented:**
- They keep task lists short (rarely more than 6-8 items)
- They plan before bed or end of workday
- They work tasks in order rather than cherry-picking easy ones
- They frequently carryover the same items (surfacing what they are avoiding)

---

### 2.7 Full Focus Planner — Michael Hyatt

**Core philosophy:** Achievement without burnout requires aligning daily tasks to annual goals. The system connects the big picture (life goals, annual goals) to quarterly and daily execution. Ritual and reflection are as important as execution.

**Key components:**
- Annual big 3 (personal + professional)
- Quarterly goals (aligned to annual)
- Weekly preview (plan the week from goals)
- Daily big 3 (three priority tasks per day)
- Daily pages (schedule, task list, notes, evening reflection)
- Evening reflection (what went well, what to improve, gratitude)

**Data structures implied:**
- Life goal / Annual goal (title, description, category: personal/professional)
- Quarterly goal (title, linked to annual goal, due date, key milestones)
- Weekly big 3 (three tasks for the week)
- Daily big 3 (three tasks for the day)
- Daily schedule (time-blocked)
- Daily reflection (evening: gratitude, win, lesson)

**User profile it suits best:** High achievers who struggle with balance. People who want their daily activity to feel meaningful. Entrepreneurs and executives. People who value ritual and ceremony in their planning. Hyatt's audience is generally Christian/faith-adjacent but the system is secular.

**Signals a user might be Full-Focus-oriented:**
- They consistently use end-of-day reflection
- They link daily tasks to longer-horizon goals
- They track gratitude or wins
- They care about work-life balance themes
- They plan the week ahead every Sunday/Monday

---

### 2.8 Eat the Frog — Brian Tracy

**Core philosophy:** Identify the most important, most dreaded task (the "frog") and do it first thing in the morning before anything else. If you have two frogs, eat the ugliest one first. Procrastination is defeated by starting, not by motivation.

**Key components:**
- Nightly frog identification (what is tomorrow's most important/dreaded task?)
- Morning frog execution (do it before email, social, anything else)
- Prioritization framework (impact × resistance = frog score)

**Data structures implied:**
- Task (title, importance score, resistance score, date)
- Daily frog designation (which task is the frog for this day)
- Morning check-in (did you eat the frog? what got in the way?)

**User profile it suits best:** Chronic procrastinators. People who know what they should do but keep avoiding it. People who feel better with a single clear imperative rather than a list. Works well with any other system as a priority layer.

**Signals a user might be Frog-oriented:**
- They have recurring tasks that keep carrying over
- They do morning check-ins (app opens early in the day)
- They rate tasks by importance/urgency/resistance
- They frequently mark "hardest task done first" in reflections

---

### 2.9 PARA Method — Tiago Forte

**Core philosophy:** All information in life fits into four categories: Projects (outcomes with deadlines), Areas (ongoing responsibilities), Resources (reference for later use), Archives (inactive). This applies across every tool and app.

**Key components:**
- Projects (active, have a deadline or clear completion state)
- Areas of Responsibility (health, finances, relationships — no end date)
- Resources (topics of interest, reference material)
- Archives (completed projects, dormant resources)
- Cross-tool consistency (PARA applied in notes, files, tasks, email)

**Data structures implied:**
- Project (title, outcome, deadline, status, linked area)
- Area (title, description, ongoing responsibilities)
- Resource (title, content, type, linked project or area)
- Archive event (moved from where, moved to archive when, why)
- Note/entry (assigned to project, area, or resource)

**User profile it suits best:** Knowledge workers with large note-taking practices. People who use many tools and want coherence. People overwhelmed by information management, not just task management. Complements GTD well. Works well for writers and researchers.

**Signals a user might be PARA-oriented:**
- They create many notes/reference entries (not just tasks)
- They heavily categorize and tag content
- They frequently move items between categories
- They search their own notes frequently
- They capture information "for later" a lot

---

### 2.10 Weekly/Daily Reviews

**Core philosophy:** A meta-practice, not a standalone system. Regular structured reflection is the connective tissue between any planning methodology and actual life. Without review, any system degrades.

**Key components:**
- Daily review (5-10 min: what happened today, what's tomorrow)
- Weekly review (30-60 min: close open loops, plan week ahead, celebrate wins)
- Monthly review (bigger horizon check)
- Standard prompts (what went well, what was hard, what am I grateful for, what's my focus next week)

**Data structures implied:**
- Review entry (type: daily/weekly/monthly, date, structured prompts + answers)
- Review template (configurable prompts per review type)
- Streak tracking (how many consecutive review days/weeks)

**User profile it suits best:** Everyone — reviews are universally valuable. But users who are intrinsically reflective will use them more deeply. People working on self-improvement or habit formation find structured reviews essential.

**Signals a user regularly reviews:**
- Regular end-of-day app sessions (not just morning)
- They annotate past entries
- They answer structured prompts rather than free-writing
- They check habit completion and streaks

---

### 2.11 Methodology Cross-Reference

| Methodology    | Time Horizon  | Primary Object | Review Cadence | Complexity | Best For               |
|----------------|---------------|----------------|----------------|------------|------------------------|
| GTD            | Ongoing       | Next Action    | Weekly         | High       | Multi-project pros     |
| BuJo           | Daily/Monthly | Log Entry      | Migration      | Medium     | Creative/analog types  |
| Time Blocking  | Daily         | Time Block     | Daily          | Medium     | Deep work practitioners|
| Pomodoro       | Session       | Pomodoro       | Daily          | Low        | Focus/procrastination  |
| OKRs           | Quarterly     | Key Result     | Weekly         | Medium     | Goal-oriented people   |
| Ivy Lee        | Daily         | Task (×6)      | Daily          | Very Low   | Simplicity seekers     |
| Full Focus     | Annual→Daily  | Big 3          | Daily+Weekly   | High       | High achievers         |
| Eat the Frog   | Daily         | Frog Task      | Daily          | Very Low   | Procrastinators        |
| PARA           | Ongoing       | Note/Resource  | Project-based  | Medium     | Knowledge workers      |
| Weekly Review  | Weekly        | Review Entry   | Weekly         | Low        | Reflective types       |

---

## 3. User Archetype Definitions

Six primary archetypes cover the vast majority of individual planners. Most real users are blends, but one archetype tends to dominate.

---

### Archetype A: The List-Maker

**Who they are:** Highly task-oriented. Satisfaction comes from checking things off. They have lists everywhere — grocery lists, project lists, someday lists. They are not necessarily strategic thinkers but they are reliable executors.

**Planning style:** Multiple flat lists, quick capture, frequent completion. They care less about *why* something is on the list and more about the physical act of clearing it.

**Methodology affinity:** Ivy Lee, GTD (context lists only), BuJo (task rapid log)

**What they need from HYPPO:**
- Fast task entry (minimal friction to add an item)
- Clear checkbox / completion affordance
- Multiple list contexts (work, home, errands)
- Satisfying visual completion feedback

**Distinguishing behavioral signals:**
- Creates many short tasks per session (>5 items in one sitting)
- High completion rate (checks things off frequently)
- Rarely writes long-form entries or reflections
- Does not use time estimates or priorities
- Frequent use of recurring tasks

---

### Archetype B: The Time-Blocker

**Who they are:** Treats time as the primary resource. Their day is a schedule to be defended. They think in hours and half-hours. Calendar is their primary tool, to-do list is secondary.

**Planning style:** Plans tomorrow in detail today. Uses the app to draft their calendar, not just their task list. Cares about duration and sequencing.

**Methodology affinity:** Time Blocking, Pomodoro, Full Focus Planner

**What they need from HYPPO:**
- Day view with time grid
- Draggable/assignable time blocks
- Duration estimates on tasks
- Integration with external calendar (future)
- Shutdown ritual / tomorrow planning flow

**Distinguishing behavioral signals:**
- Adds times to tasks (or duration estimates)
- Opens app at the end of the workday to plan tomorrow
- Creates recurring time blocks (lunch, exercise, focus)
- Rarely uses tags or categories — uses time as the organizer
- Checks the schedule view more than the task list view

---

### Archetype C: The Reflective Journaler

**Who they are:** Process-oriented, introspective. The value of writing is in the thinking it produces, not just the record. They use their planner as much for emotional processing as for task management.

**Planning style:** Long-form daily entries, mood tracking, habit logs, gratitude lists. Planning is mixed into narrative rather than separate from it.

**Methodology affinity:** BuJo (journaling side), Full Focus (evening reflection), Weekly Reviews

**What they need from HYPPO:**
- Rich text daily entry (markdown or formatting)
- Mood tracking (daily emotional state)
- Habit streaks
- Reflection prompts (optional guided writing)
- Past entry browsing and search
- Privacy/lock features (this is personal writing)

**Distinguishing behavioral signals:**
- Long average entry length (>100 words per session)
- Regular daily usage (journals every day or near-daily)
- Uses mood/feeling tags
- Browses and re-reads past entries
- Rarely uses task-only views
- Uses the app in the evening (reflection time)

---

### Archetype D: The Goal-Tracker

**Who they are:** Motivated by outcomes, not process. They want to measure progress toward meaningful goals. They are willing to do daily work if they can see the trajectory clearly.

**Planning style:** Starts with goals, works backward to tasks. Regular progress check-ins. Quantified self elements (tracking metrics, not just tasks).

**Methodology affinity:** OKRs, Full Focus Planner, Eat the Frog (as prioritization)

**What they need from HYPPO:**
- Goal hierarchy (life goals → quarterly → weekly)
- Progress metrics (numeric or percentage)
- Task-to-goal linking (this task serves which goal?)
- Streak and consistency tracking
- Visual progress indicators (charts, rings, bars)
- Quarter/month review prompts

**Distinguishing behavioral signals:**
- Creates goals before creating tasks
- Links tasks to goals when available
- Uses the app to check/update metrics (not just write)
- Does regular reviews (weekly confidence ratings)
- Writes longer-horizon entries (monthly, quarterly)
- Uses percentage or numeric fields

---

### Archetype E: The Habit-Builder

**Who they are:** Focused on building or breaking specific behaviors. The app is a habit tracker first, planner second. Consistency and streaks are the primary motivators.

**Planning style:** Small set of daily habits with binary completion (done/not done). Minimal task management. The daily ritual of checking habits IS the planning.

**Methodology affinity:** Atomic Habits principles, BuJo habit trackers, any streaking system

**What they need from HYPPO:**
- Habit definitions (daily, weekly, N times per week)
- Binary or quantified check-in (did you do it? how many times/minutes?)
- Streak visualization
- Habit calendar (heatmap of consistency)
- Minimal friction check-in (home screen can be the habit board)
- Recovery mechanic (missing one day shouldn't kill motivation)

**Distinguishing behavioral signals:**
- Configures habits in first few sessions
- Daily usage is short but consistent (2-3 minutes)
- Opens app at the same time every day (morning or evening ritual)
- Does not create many tasks — habit check-ins are their core use
- Cares deeply about streaks, frustrated if streak breaks

---

### Archetype F: The Knowledge-Organizer

**Who they are:** Not primarily a task manager or a journaler — they are a note-taker who needs structure. They capture information, ideas, and reference material. Planning happens within a broader knowledge management practice.

**Planning style:** PARA-like structure. Heavy use of notes/reference. Projects have lots of associated information. Tags and search are critical features.

**Methodology affinity:** PARA, GTD (reference material side), Zettelkasten (adjacent)

**What they need from HYPPO:**
- Rich note/entry types (not just tasks)
- Hierarchical or tagged organization
- Full-text search across all content
- Linking between entries (note references another note)
- Project containers that hold tasks AND notes AND references
- Export capability (data portability is important to this type)

**Distinguishing behavioral signals:**
- Creates many notes and reference entries (not just tasks)
- Heavy use of tags and categories
- Frequent search behavior
- Entries are long and richly formatted
- Creates custom collections or notebooks
- Uses the app as a second brain, not just a to-do list

---

### Archetype Signal Summary

| Signal | List-Maker | Time-Blocker | Journaler | Goal-Tracker | Habit-Builder | Organizer |
|--------|-----------|--------------|-----------|--------------|---------------|-----------|
| Session frequency | Variable | End of day | Daily | Multiple/week | Daily | As needed |
| Session duration | Short | Medium | Long | Medium | Very short | Long |
| Entry type | Tasks | Time blocks | Free text | Goals/metrics | Habit checks | Notes/refs |
| Avg entry length | Short | Medium | Long | Medium-long | Very short | Long |
| Primary time of use | Morning | Evening | Evening | Any | Morning/eve | Any |
| Review behavior | Rarely | Daily shutdown | Nightly | Weekly | Streak check | On demand |
| Tag/category use | Moderate | Low | High | High | Low | Very high |
| Task completion rate | High | High | Low | Medium | N/A | Low |
| Time estimates used | No | Yes | No | Sometimes | No | No |

---

## 4. Adaptive Personalization Strategy

### 4.1 Core Principle

HYPPO does not ask "what kind of planner are you?" It watches how the user actually behaves over time and infers their archetype. Stated preferences are unreliable (users aspire to GTD but behave like list-makers). Behavior is truth.

The personalization system operates on three layers:

1. **Signal collection** — passive, continuous, non-intrusive
2. **Archetype inference** — probabilistic scoring updated on every session
3. **UI adaptation** — gradual surface changes based on confidence

---

### 4.2 Behavioral Signals and Their Meanings

The following signals are collected passively during normal app use:

**Signal: Average words per entry**
- < 10 words → task/list behavior (List-Maker, Ivy Lee)
- 10-50 words → structured capture (GTD, BuJo tasks + notes)
- 50-200 words → narrative planning (Journaler, Full Focus)
- > 200 words → deep reflection or knowledge capture (Journaler, Organizer)

**Signal: Session timing pattern**
- Consistent morning session only → Habit-Builder, Eat-the-Frog, Ivy Lee
- Consistent evening session only → Reflective Journaler, shutdown planner
- Both morning and evening → Full Focus, BuJo, high-engagement user
- Irregular throughout day → GTD user processing inbox, Pomodoro check-ins
- End-of-week spike → OKR weekly review user

**Signal: Session duration distribution**
- Mode < 3 minutes → Habit-Builder (daily check-in ritual)
- Mode 5-15 minutes → List-Maker, Time-Blocker (planning session)
- Mode > 20 minutes → Journaler, Organizer (deep work with the app)

**Signal: Feature usage frequency**
- Task creation rate (tasks per session)
  - High (>5/session) → List-Maker, GTD
  - Low (<2/session) → Journaler, Organizer, Habit-Builder
- Time field usage → Time-Blocker
- Goal creation → Goal-Tracker
- Habit check-in → Habit-Builder
- Tag usage → Organizer, GTD
- Search frequency → Organizer
- Review template completion → Full Focus, Weekly Review user

**Signal: Task completion patterns**
- High completion rate (>70%) → List-Maker (realistic lists), Ivy Lee
- Low completion rate (<40%) → Overplanning type (needs simplification), or Goal-Tracker (tasks are reference, not commitments)
- Carryover pattern (same tasks moving day to day) → Eat the Frog candidate (avoidance behavior)
- Pomodoro-length work sessions → Pomodoro type

**Signal: Entry type mix**
- >80% tasks → List-Maker
- >50% free text notes → Journaler or Organizer
- Mix of tasks + notes + goals → Full Focus, BuJo
- Predominantly habit completions → Habit-Builder
- Goals with linked tasks → Goal-Tracker

**Signal: Retrospective/review behavior**
- Uses end-of-day prompts consistently → BuJo, Full Focus, Weekly Review
- Annotates past entries → BuJo, Journaler
- Does weekly reviews → OKR, Full Focus, GTD
- Never reviews → pure List-Maker or Habit-Builder

**Signal: Planning horizon in entries**
- Tasks due today/tomorrow → List-Maker, Time-Blocker
- Tasks due this week → Standard planner
- Tasks with no due date → GTD Someday/Maybe, Organizer
- Goals with Q+/annual horizon → Goal-Tracker, OKR, Full Focus

---

### 4.3 Archetype Scoring Model

Each user has a score vector across archetypes, updated after each session:

```
archetype_scores = {
    "list_maker": 0.0,
    "time_blocker": 0.0,
    "journaler": 0.0,
    "goal_tracker": 0.0,
    "habit_builder": 0.0,
    "organizer": 0.0
}
```

Scores are floating-point weights summing to 1.0 (normalized probability distribution). After each session, signals update the raw scores, and they are re-normalized.

**Scoring rules (examples):**

```python
# Signal: user created 7 tasks in one session
list_maker_score += 0.3
time_blocker_score += 0.05

# Signal: user wrote a 300-word entry
journaler_score += 0.4
organizer_score += 0.2

# Signal: user completed a habit check-in
habit_builder_score += 0.5

# Signal: user linked a task to a goal
goal_tracker_score += 0.4
list_maker_score -= 0.1  # negative evidence for pure list-making

# Signal: user opened app at 7:00am and spent 2 minutes
habit_builder_score += 0.2
morning_planner_flag = True

# Signal: user added a time estimate to a task
time_blocker_score += 0.3
```

Scores accumulate over time with a decay factor (recent behavior weighted more than old behavior). After 30 days, the system begins making confident UI adaptations.

---

### 4.4 UI Adaptation Mechanics

Adaptation is gradual. The goal is that the user never consciously notices the app is changing — it just feels increasingly natural.

**Phase 0: Days 1-7 (Universal Baseline)**
- Clean, minimal interface
- Single "capture" input (free text, type a thing)
- Automatic type inference (does this look like a task? a note?)
- All views available but not prominently featured
- No suggestions, no prompts, no nudges

**Phase 1: Days 7-14 (Soft Signals)**
- System has collected enough data for tentative signals
- If a signal is strong (one archetype >40% score), begin subtle surface changes:
  - List-Maker signal: task list view becomes default home
  - Journaler signal: daily log view becomes default home
  - Habit-Builder signal: habit board nudge ("want to track a habit?")
- Features that have never been used are moved to a "More" menu
- No features are hidden entirely at this stage — just de-emphasized

**Phase 2: Days 14-30 (Growing Confidence)**
- Archetype score(s) have enough data for meaningful differentiation
- UI vocabulary begins shifting:
  - List-Maker: "Tasks" and "Lists" language dominates
  - Time-Blocker: "Schedule" and "Blocks" language
  - Journaler: "Journal" and "Entries" language
  - Goal-Tracker: "Goals" and "Progress" language
  - Habit-Builder: habits board is promoted to primary navigation
  - Organizer: search and tags become primary navigation affordances
- Relevant methodology-specific views are promoted
- Suggestion layer begins: "You haven't reviewed last week yet" (for review-users)

**Phase 3: Days 30+ (Settled Profile)**
- Dominant archetype(s) identified (top 1-2 archetypes)
- Interface has adapted to feel purpose-built
- Unused features are in an "explore" section, not deleted
- Active "insight" prompts based on behavior patterns:
  - "You've carried this task for 5 days — is it really important?"
  - "You haven't reviewed your goals this week"
  - "Your journaling streak is 14 days — keep going"
- User can always override the adaptation ("reset to default" or "I want to try a different style")

---

### 4.5 When to Lock vs. Keep Adapting

The profile should never be fully locked — people change, life phases change. Strategy:

- **Soft lock at 30 days**: UI is settled, but the scoring model continues running
- **Recalibration window**: If behavior shifts significantly (>2 SD from established pattern) for 2+ weeks, trigger a "your planning style seems to be changing — would you like to update your experience?" prompt
- **Seasonal adjustment**: Some users change style in January (resolutions) vs. summer (relaxed mode). The system should track this cyclically, not fight it.
- **User control**: Settings allow users to manually select or override their adaptation. The stated choice is recorded alongside the inferred one.

---

## 5. Feature Set: MVP to Fully Adapted

### 5.1 MVP Feature Set (What Gets Built First)

The MVP must be useful to every archetype on day 1 without committing to any. It must be genuinely usable as a minimal planner even without personalization.

**MVP Core Features:**

**1. Universal Capture**
- Single input field: type anything
- System infers type (task vs. note vs. event) from content heuristics
- User can override the inferred type
- No required fields except content

**2. Daily Log**
- Chronological list of today's entries
- Mix of tasks, notes, events
- Date navigation (yesterday / today / tomorrow)

**3. Tasks**
- Task creation (title, optional due date)
- Checkbox completion
- Basic list view
- No projects, no contexts yet

**4. Simple Journal Entry**
- Free-text entry with date
- Optional mood/energy indicator (1-5)
- Markdown basic formatting (bold, italic, lists)

**5. Habits (Basic)**
- Define up to 5 daily habits
- Daily check-in (done/not done)
- Simple streak counter

**6. User Account**
- Email/password authentication
- Single-user model (no sharing/teams)
- Data export (JSON)

**7. Settings**
- Theme (light/dark)
- Timezone
- Notification preferences (stub for later)

---

### 5.2 Archetype-Adapted Feature Sets

Once an archetype is identified, the following feature layers are progressively surfaced:

**List-Maker Adaptations:**
- Multiple named lists (Work Tasks, Home, Errands, Someday)
- Context tags (@home, @work, @phone)
- Quick-add keyboard shortcut (no mouse required)
- Bulk complete / bulk archive
- Recurring tasks
- Satisfying completion animation

**Time-Blocker Adaptations:**
- Day view with time grid (hourly or 30-min)
- Drag-to-create time blocks
- Duration field on tasks
- Time block templates (reusable day structure)
- Shutdown ritual flow (daily planning wizard for tomorrow)
- Calendar export/sync (iCal)

**Reflective Journaler Adaptations:**
- Full rich-text editor per entry
- Structured reflection templates (optional: "what went well, what was hard, what am I grateful for")
- Mood tracking with visual history (calendar heatmap by mood)
- Habit calendar (monthly view)
- Entry tagging and search
- Private/encrypted entries option
- Past entry browser with date navigation

**Goal-Tracker Adaptations:**
- Goal hierarchy (life → annual → quarterly → weekly)
- Numeric metrics on goals (start, target, current)
- Goal progress visualization (bar, ring, trend chart)
- Task-to-goal linking
- Weekly review with goal check-in
- Quarter retrospective template
- OKR-style confidence ratings

**Habit-Builder Adaptations:**
- Habit board as home screen
- Quantified habits (not just binary — "20 minutes of exercise")
- Habit streak visualization (fire icon, calendar heatmap)
- Habit stacking (link habits together)
- Recovery/grace day mechanic
- Habit check-in notification (push, when mobile is available)
- Habit history and trends

**Knowledge-Organizer Adaptations:**
- PARA structure (Projects / Areas / Resources / Archive)
- Rich notes with formatting, images, links
- Full-text search with filters
- Bidirectional note linking
- Tag taxonomy management
- Project containers (tasks + notes + goals in one view)
- Multiple export formats (Markdown, JSON)
- Inbox processing workflow (GTD-inspired)

---

### 5.3 Full Feature Surface (Post-Adaptation)

The complete feature set of a fully-adapted HYPPO instance includes everything above, organized by the user's dominant archetype. No single user should ever see all features simultaneously — the adaptation ensures the UI remains clean.

**Features never in MVP but available when appropriate:**
- Pomodoro timer
- Calendar integration (read/write)
- Reminders and notifications
- Recurring review templates
- Multi-device sync (foundation laid in FastAPI from day 1)
- Data import (from common formats: Markdown, CSV, Todoist JSON)
- API access for power users

---

## 6. Data Model Sketch

### 6.1 Design Principles

The data model must be:
- **Methodology-agnostic at the core** — the same entities serve all archetypes
- **Extensible without migrations** — metadata/attributes stored flexibly for archetype-specific fields
- **Temporally aware** — every entity has a relationship to time (when it was, when it's for)
- **User-scoped** — every entity belongs to exactly one user
- **Portable** — the schema should map cleanly to a JSON export

### 6.2 Core Entities

**User**
```
id: UUID
email: str (unique)
password_hash: str
created_at: datetime
timezone: str
preferences: JSON  # UI preferences, notification settings
archetype_scores: JSON  # {list_maker: 0.2, journaler: 0.6, ...}
archetype_settled_at: datetime | null  # when Phase 3 was reached
```

**Entry** (the universal base entity)
```
id: UUID
user_id: UUID (FK → User)
type: Enum(task, note, event, habit_checkin, goal, time_block, review)
content: str  # the primary text content
content_rich: JSON | null  # structured rich-text (for formatted entries)
created_at: datetime
updated_at: datetime
entry_date: date  # the logical date this entry belongs to (may differ from created_at)
attributes: JSON  # flexible key-value store for type-specific fields
tags: str[]  # array of tag strings
parent_id: UUID | null  # FK → Entry (for hierarchy: goal → task, project → note)
```

The `attributes` JSON field stores type-specific data without schema changes:

```python
# Task attributes
{"due_date": "2026-04-01", "completed": True, "completed_at": "...",
 "duration_minutes": 25, "context": "@work", "goal_id": "uuid..."}

# Time block attributes
{"start_time": "09:00", "end_time": "10:30", "block_type": "deep_work"}

# Habit check-in attributes
{"habit_id": "uuid...", "value": 1, "target": 1, "unit": "times"}

# Goal attributes
{"horizon": "quarterly", "metric_type": "numeric", "start_value": 0,
 "target_value": 100, "current_value": 43, "due_date": "2026-06-30"}

# Review attributes
{"review_type": "weekly", "prompts": [...], "responses": {...}}

# Mood/energy attributes
{"mood": 4, "energy": 3, "emotion_tags": ["focused", "tired"]}
```

**Habit** (definition, separate from check-ins)
```
id: UUID
user_id: UUID (FK → User)
name: str
description: str | null
frequency: Enum(daily, weekdays, N_per_week, custom)
frequency_config: JSON  # {days_per_week: 5, specific_days: ["Mon", "Wed"]}
target_value: float  # default 1 (binary done/not done)
unit: str | null  # "minutes", "pages", "km"
created_at: datetime
archived_at: datetime | null
color: str | null  # for visual differentiation
icon: str | null
```

**Tag** (materialized for search performance)
```
id: UUID
user_id: UUID (FK → User)
name: str (unique per user)
color: str | null
category: str | null  # auto-classified: context, project, topic, mood
usage_count: int  # denormalized for sort/suggest
```

**BehaviorEvent** (for the personalization engine)
```
id: UUID
user_id: UUID (FK → User)
event_type: str  # "entry_created", "task_completed", "habit_checked", "feature_opened"
event_data: JSON  # context data for the event
occurred_at: datetime
session_id: UUID  # groups events within a single app session
```

**Session** (aggregated session analytics)
```
id: UUID
user_id: UUID (FK → User)
started_at: datetime
ended_at: datetime | null
duration_seconds: int | null
entry_count: int
task_count: int
word_count: int
features_used: str[]  # list of feature names accessed
```

---

### 6.3 Methodology-to-Entity Mapping

| Methodology | Uses Entry.type | Key Attributes | Parent/Child |
|-------------|----------------|----------------|--------------|
| GTD | task, note | context, project_id, next_action | project → task |
| BuJo | task, note, event | bullet_type, migrated_from | none (flat log) |
| Time Blocking | time_block, task | start_time, end_time, block_type | block → task |
| Pomodoro | task | pomodoro_estimate, pomodoro_actual | none |
| OKRs | goal, note | horizon, metric_type, kr_id | objective → key_result |
| Ivy Lee | task | priority_rank (1-6), date | none |
| Full Focus | goal, task, review | big_3, annual_goal_id | annual → quarterly → daily |
| PARA | note, task | para_category (P/A/R/A) | area → project → resource |
| Weekly Review | review | review_type, prompts, responses | none |

---

### 6.4 Schema Flexibility Strategy

The `attributes: JSON` field on Entry and the separate entity tables give enough flexibility without going full EAV (Entity-Attribute-Value), which becomes unmaintainable.

**Query pattern for flexible attributes (PostgreSQL):**
```sql
-- Find all tasks with @work context
SELECT * FROM entries
WHERE user_id = $1
AND type = 'task'
AND attributes->>'context' = '@work';

-- GIN index for JSON field performance
CREATE INDEX idx_entry_attributes ON entries USING gin(attributes);
```

**For SQLite (development):** JSON functions work similarly. The GIN index becomes a computed column in SQLite.

---

## 7. Architecture Recommendations

### 7.1 Overall System Design

```
┌─────────────────────────────────────────────┐
│              Web Browser                     │
│  (HTML + HTMX / minimal JavaScript)         │
└──────────────────┬──────────────────────────┘
                   │ HTTP (SSR HTML responses)
┌──────────────────▼──────────────────────────┐
│           Flask / Quart Web Layer            │
│  - Session management                        │
│  - Server-side template rendering (Jinja2)  │
│  - Calls FastAPI via HTTP                   │
│  - No direct DB access                      │
│  - Handles auth cookie → JWT exchange       │
└──────────────────┬──────────────────────────┘
                   │ Internal HTTP (REST/JSON)
┌──────────────────▼──────────────────────────┐
│              FastAPI API Layer               │
│  - All business logic                       │
│  - Data validation (Pydantic)               │
│  - Auth (JWT tokens)                        │
│  - Personalization engine                   │
│  - Clean REST API (future mobile clients)   │
└──────────────────┬──────────────────────────┘
                   │ ORM / SQL
┌──────────────────▼──────────────────────────┐
│              Database                        │
│  PostgreSQL (prod) / SQLite (dev)           │
│  SQLAlchemy ORM                             │
└─────────────────────────────────────────────┘
```

**Future mobile clients connect directly to FastAPI**, bypassing Flask entirely. The Flask layer is purely a web rendering concern.

---

### 7.2 FastAPI Layer Design

**Versioning strategy:** URL path versioning (`/api/v1/...`). Simple, explicit, compatible with all clients. Version in URL is more mobile-client-friendly than header-based versioning.

**Authentication approach:**
- JWT tokens (access + refresh)
- Access token: short-lived (15 minutes)
- Refresh token: long-lived (30 days), stored HttpOnly cookie
- Flask layer: stores JWT in server-side session, exchanges for API calls
- Mobile clients: store JWT in secure storage (keychain/keystore)

**REST design principles:**
```
POST   /api/v1/entries          # create entry
GET    /api/v1/entries          # list entries (with filters)
GET    /api/v1/entries/{id}     # get single entry
PATCH  /api/v1/entries/{id}     # partial update
DELETE /api/v1/entries/{id}     # soft delete

POST   /api/v1/habits           # define habit
GET    /api/v1/habits           # list habits
POST   /api/v1/habits/{id}/checkin  # log check-in for today

GET    /api/v1/analytics/behavior   # current archetype scores
GET    /api/v1/analytics/summary    # week/month summary stats

POST   /api/v1/auth/token       # login (get JWT)
POST   /api/v1/auth/refresh     # refresh access token
DELETE /api/v1/auth/token       # logout
```

**Why REST over GraphQL:**
- Mobile clients need predictable, simple API endpoints
- The data model is not deeply nested/relational (GraphQL's strength)
- GraphQL adds complexity that is not warranted at this scale
- REST is more cacheable (GET endpoints)
- The team is Python-first; REST tooling (FastAPI + Pydantic) is excellent

**Pydantic models:** All request/response shapes are Pydantic models. This gives automatic validation, OpenAPI schema generation, and type safety.

**Background tasks:** FastAPI's `BackgroundTasks` for:
- Updating archetype scores after each API call
- Generating behavior event records
- Sending notifications (future)

**FastAPI dependency injection pattern:**
```python
# Auth dependency used on every protected route
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    ...

# Archetype context available to any route
async def get_user_archetype(user: User = Depends(get_current_user)) -> ArchetypeContext:
    ...
```

---

### 7.3 Flask/Quart Web Layer Design

**Flask vs. Quart decision:**
- Use **Quart** if any real-time features are planned (WebSockets for live updates, async streaming)
- Use **Flask** if the app is purely request/response
- Recommendation: **start with Flask** (simpler, more documentation), plan migration path to Quart if needed
- Both use Jinja2 templates — the swap is not difficult later

**Flask-to-FastAPI communication:**
```python
# Flask calls FastAPI via httpx (async-capable HTTP client)
import httpx

API_BASE = "http://localhost:8000/api/v1"

async def get_today_entries(user_jwt: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE}/entries",
            params={"date": date.today().isoformat()},
            headers={"Authorization": f"Bearer {user_jwt}"}
        )
        response.raise_for_status()
        return response.json()
```

**Session handling in Flask:**
- User logs in through Flask form → Flask calls FastAPI `/auth/token`
- FastAPI returns JWT → Flask stores JWT in server-side session (Flask-Session with Redis or filesystem backend)
- Each Flask request extracts JWT from session, passes to FastAPI calls
- Session expiry tied to JWT refresh token lifetime

**Rendering strategy — HTMX-first:**
- Server-side Jinja2 templates render full HTML pages
- HTMX handles partial page updates (form submissions, task completions, habit check-ins)
- This avoids a heavy JavaScript framework while keeping interactivity
- HTMX attributes: `hx-post`, `hx-target`, `hx-swap` for in-place updates
- Result: feels like a SPA without being one

**Why not a full SPA (React/Vue):**
- Adds enormous frontend complexity for a single-developer project
- HTMX achieves 90% of the interactivity at 10% of the complexity
- Server-side rendering is better for SEO (if ever needed) and accessibility
- Python-first stack stays consistent

---

### 7.4 Mobile Readiness

The FastAPI layer is designed from day 1 for mobile clients, even though no mobile app exists yet. Key contracts:

**API design rules that matter for mobile:**
1. **Pagination on all list endpoints** — `?page=1&per_page=50`. Mobile clients cannot load 10 years of entries at once.
2. **Partial responses** — `?fields=id,content,type,created_at` (sparse fieldsets) to reduce data transfer
3. **Offline-first affordance** — entries have client-assigned UUIDs (not server-generated), so mobile clients can create entries offline and sync later
4. **Conflict resolution** — `updated_at` timestamp on all entities; last-write-wins with optional conflict notification
5. **Push notification tokens** — `User` entity has a `push_tokens: JSON` field for FCM/APNs tokens (registered later)
6. **Versioned endpoints** — `/api/v1/` prefix. When breaking changes occur, `/api/v2/` is added without breaking mobile clients still on v1.
7. **Error format consistency** — all errors: `{"error": {"code": "...", "message": "...", "field": "..."|null}}`

**Client-generated UUIDs (critical for offline):**
```python
# Mobile/web client generates UUID before API call
entry_id = str(uuid.uuid4())  # client-side
# POST /api/v1/entries with id=entry_id
# Server accepts client ID, rejects if collision (extremely rare)
```

---

### 7.5 Database Recommendations

**Development:** SQLite — zero setup, file-based, sufficient for single-user dev
**Production:** PostgreSQL — JSON support, GIN indexes, full-text search, reliability

**ORM:** SQLAlchemy (async via `sqlalchemy[asyncio]` + `asyncpg` for PostgreSQL)

**Migration tool:** Alembic — works natively with SQLAlchemy, supports up/down migrations

**Schema design notes:**
- `Entry.attributes` JSON column with GIN index for flexible attribute queries
- `BehaviorEvent` table will grow large — partition by month in production or use a time-series friendly approach
- Consider archiving `BehaviorEvent` older than 90 days to a separate table
- `Entry` soft-delete (`deleted_at` timestamp) rather than hard delete for data safety

---

## 8. Recommended Build Sequence

### 8.1 Phase 1: Foundation (Weeks 1-4)

**Goal:** A working, deployed application that any archetype can use at minimum viability.

**Build order and rationale:**

1. **FastAPI skeleton + auth** *(Week 1)*
   - Project structure, dependency injection, error handling middleware
   - JWT authentication endpoints (`/auth/token`, `/auth/refresh`)
   - User model and registration
   - **Why first:** Everything else depends on auth. Getting this right now prevents painful refactoring.

2. **Core data model + migrations** *(Week 1-2)*
   - `Entry`, `User`, `Tag` tables
   - Alembic migration setup
   - Basic CRUD endpoints for entries
   - **Why early:** The Entry model is the central entity. Decisions made here (UUID PKs, attributes JSON, soft-delete) are hard to change later.

3. **Flask web layer skeleton** *(Week 2)*
   - Basic Jinja2 templates
   - Flask-to-FastAPI HTTP client wrapper
   - Session management (login/logout flow)
   - **Why third:** Need auth working before building web layer on top of it.

4. **Daily log view** *(Week 2-3)*
   - Today's entries, date navigation
   - Universal capture input
   - Basic task creation + completion (HTMX)
   - Basic note creation
   - **Why:** This is the core loop — open app, write something, see it in the log.

5. **Habits MVP** *(Week 3)*
   - Habit definition
   - Daily check-in
   - Streak counter
   - **Why now:** Habits drive daily engagement. Without habits, some users (Habit-Builder archetype) have no reason to return daily.

6. **BehaviorEvent collection** *(Week 3-4)*
   - Instrument all API endpoints with event emission
   - Session tracking
   - **Why this early:** The personalization engine needs data from day 1 of production. Starting event collection late means losing the most valuable early behavioral data.

7. **Basic settings + data export** *(Week 4)*
   - Timezone, theme
   - JSON data export
   - **Why export early:** Builds user trust. Knowing you can export your data lowers the psychological barrier to committing to a new tool.

---

### 8.2 Phase 2: Personalization Engine (Weeks 5-8)

**Goal:** The app begins adapting based on behavior.

8. **Archetype scoring model** *(Week 5)*
   - Signal extraction from BehaviorEvents
   - Score computation + storage
   - API endpoint exposing current archetype scores
   - **Why before UI adaptation:** Need the scores to be correct before acting on them.

9. **Phase 1 UI adaptation** (soft signals) *(Week 6)*
   - Default view changes based on dominant archetype
   - De-emphasize unused features
   - **Why:** This is the product's differentiator. It should come early enough to learn from real users.

10. **Journal entry enhancements** *(Week 6-7)*
    - Rich text editor (Markdown)
    - Mood tracking
    - Reflection templates (optional prompts)
    - **Why here:** Journaler archetype is high-value, high-retention. These features serve them.

11. **Archetype-specific views** *(Week 7-8)*
    - Time-blocker day view (time grid)
    - Goal hierarchy view (for Goal-Tracker)
    - Phase 2+3 UI adaptation (terminology changes, feature promotion)

---

### 8.3 Phase 3: Full Feature Surface (Weeks 9-16+)

**Goal:** Each archetype has a purpose-built experience.

12. Tasks: contexts, projects, recurring tasks
13. Goals: OKR structure, progress metrics, quarterly reviews
14. Knowledge organizer: PARA structure, note linking, full-text search
15. Pomodoro timer integration
16. Calendar export (iCal)
17. Notification system (web push → mobile push later)
18. Data import (Markdown, CSV, Todoist)
19. Mobile API hardening (pagination, sparse fields, offline UUID support)

---

### 8.4 Decisions That Lock In Early (Do Not Defer These)

These architectural decisions are expensive to change later:

| Decision | Lock-in Point | Why It Matters |
|----------|--------------|----------------|
| UUID primary keys | Week 1 | Required for client-generated IDs (offline sync). Changing PK type later requires full table rewrite. |
| `attributes: JSON` on Entry | Week 1 | Enables flexible archetype-specific fields without migrations. If you start with typed columns, you'll fight migrations forever. |
| JWT auth (not sessions) | Week 1 | Mobile clients cannot use server-side sessions. JWT from day 1 makes mobile readiness real. |
| Soft deletes | Week 1 | Users lose trust if data disappears. Hard to add soft-delete semantics to existing queries later. |
| API versioning prefix | Week 1 | Once mobile clients exist, you cannot change URL structure. |
| FastAPI as data owner | Week 1 | Flask must never query the database directly. If Flask touches the DB, you lose the clean API contract mobile needs. |
| Client-side UUID generation | Phase 2 | Once your IDs are server-generated, offline-first sync requires a major refactor. Decide before mobile matters. |

---

### 8.5 What Can Be Deferred

- Pomodoro timer (Phase 3+)
- Calendar sync (Phase 3+)
- Push notifications (Phase 3+)
- Data import (Phase 3+)
- Note linking / bidirectional references (Phase 3+)
- PARA full implementation (Phase 3+)
- Any archetype adaptation beyond Phase 1 (Phase 2)
- Rich text beyond Markdown (Phase 3+)
- Multi-device conflict resolution UI (Phase 3+)

---

## 9. Open Questions

These are real unresolved decisions that must be made before or during implementation. They are not questions with obvious answers.

---

**Q1: Where does personalization state live?**

*The question:* The archetype score vector is continuously updated. Does it live in the `User` table as a JSON column, in a separate `UserProfile` table, or in a time-series of score snapshots?

*Why it matters:* If stored as a single JSON blob per user, you lose history (can't see how their score evolved over time). A snapshot table is more powerful but adds write overhead.

*Options:*
- `User.archetype_scores: JSON` — simple, loses history
- `ArchetypeSnapshot` table (daily snapshot) — queryable history, moderate overhead
- `BehaviorEvent` derived (scores always computed from events) — perfectly auditable, expensive to compute

~~*Recommendation direction:* Start with JSON on User, add snapshot table in Phase 2 when you need history for adaptation.~~

**DECIDED:** History since the beginning is non-negotiable. `BehaviorEvent` records are permanent and immutable — the raw behavioral history is the source of truth and must never be discarded. Archetype scores are always fully derivable from the complete event log. An `ArchetypeSnapshot` table is added for read performance (avoid recomputing from all events on every request), updated incrementally as new events arrive. The JSON blob on `User` is not used for scores — only for user-controlled preferences and settings.

*Implications:*
- `BehaviorEvent` table must have no TTL, no pruning, no archiving — append-only forever
- `ArchetypeSnapshot` stores daily score vectors (one row per user per day)
- Score queries read from the latest snapshot, not from raw events
- The event log enables future features: replay, trend visualization, "how you've changed over a year"

---

**Q2: What is the exact Flask-to-FastAPI communication contract?**

*The question:* Should Flask call FastAPI via HTTP (treating it as a true external service), or should Flask import FastAPI app objects and call them in-process?

*Why it matters:* In-process calls (same Python process) are faster and simpler for development but blur the separation. HTTP calls are architecturally clean but add latency and network complexity.

*Options:*
- HTTP (recommended) — clean separation, mobile-ready, testable independently
- In-process with `httpx.AsyncClient` to `TestClient` — hybrid, complex
- Shared database access (Flask reads DB directly) — defeats the purpose of the API layer

**DECIDED:** Flask and FastAPI run as separate processes. Communication is via HTTP using `httpx`. In-process calls and shared database access are explicitly ruled out.

*Implications:*
- Flask is a true HTTP client of the FastAPI service — no shared Python state
- Both processes can be deployed, scaled, and restarted independently
- FastAPI remains the single point of data access; Flask never touches the database directly
- Service URL is configurable via environment variable (e.g. `FASTAPI_BASE_URL`) for dev/prod parity

*Open research note:* HTTP is the baseline decision. Before Phase 2, research whether more efficient secure IPC methods are appropriate for same-host deployments — candidates include Unix domain sockets (lower overhead than TCP loopback), gRPC (typed contracts, binary protocol), or message queues (async decoupling). Evaluate against the mobile-readiness requirement: the chosen protocol must not prevent FastAPI from serving mobile clients over standard HTTP/HTTPS.

---

**Q3: How should the free-text capture input work for type inference?**

*The question:* When a user types into the universal capture box, how does HYPPO decide if it's a task, a note, or an event?

*Why it matters:* Getting this wrong creates friction (user types a note, it becomes a task). The heuristic matters for the first-use experience.

*Options:*
- Explicit type toggle (user always picks) — zero ambiguity, more clicks
- Keyword heuristics (starts with verb → task, contains date/time → event, else → note)
- ML classification (overkill for MVP, could be Phase 3+)
- Default to note, user promotes to task — reversal is easy

**DECIDED:** The capture box is a writing-first, zero-friction surface. The system must never interrupt or challenge the user during writing. All captured text defaults to the simplest available type: **note**.

*The two-mindset principle:* Writing and reviewing are distinct cognitive modes and must be treated as separate workflows. Classification belongs to the review mindset, not the capture mindset.

*Post-save review flow:*
- Every newly captured note is automatically flagged as "pending review"
- During the review workflow (a dedicated, separate context), the user is presented with the note and can be asked: "Would you like to convert this to a task, event, or goal?"
- System heuristics (keyword signals, patterns, context) may pre-suggest a type as a hint — but never apply it automatically
- The user confirms or dismisses in review; the note remains a note until explicitly converted

*Power user escape hatch:*
- A type selector is available in all interfaces for users who want to set the type at capture time
- This is a secondary affordance — visible but not prominent — so it does not distract default users
- Power users may also set type during inline editing, not only during capture

*Implications for data model:*
- Notes gain a `review_status` field: `pending | reviewed | dismissed`
- Heuristic signals are stored as metadata on the note (not applied as the type)
- The review queue is a first-class UI surface, not an afterthought

---

**Q4: What is the right granularity for BehaviorEvent collection?**

*The question:* Every keystroke? Every page view? Only meaningful interactions? The granularity affects storage, privacy, and the quality of archetype signals.

*Why it matters:* Too coarse → signals are weak. Too fine → storage explosion, privacy concerns, GDPR implications.

*Options:*
- Session-level only (entry count, word count, features used, time of day)
- Interaction-level (entry created, task completed, feature viewed)
- Micro-interaction level (time spent on each element, scroll depth)

*Recommendation direction:* Interaction-level (middle option). Capture meaningful semantic events (`entry_created`, `task_completed`, `feature_opened`, `habit_checked`) with rich metadata. Avoid sub-interaction tracking.

---

**Q5: How does the adaptation present itself without feeling creepy?**

*The question:* Users will notice the app is changing. If they feel surveilled, they will distrust the product. If they don't understand why it's changing, they'll be confused.

*Why it matters:* The personalization is the whole point — but it must feel like the app *growing with you*, not being *watched*.

*Options:*
- Invisible adaptation (just changes, no explanation) — may feel jarring
- Explicit: "Based on how you use HYPPO, we've adjusted your layout" — transparent but clinical
- Narrative framing: "Your HYPPO is evolving" with user control to accept/reject changes
- Opt-in adaptation: off by default, user turns it on — loses the key differentiator

*Recommendation direction:* Subtle adaptation with an opt-out. Occasional surfaced insight ("We noticed you use HYPPO mostly for journaling — we've made the journal view your home"). User can always go to Settings > My Style and see/override their profile.

---

**Q6: SQLite vs. PostgreSQL for development?**

*The question:* SQLite is zero-config but has JSON operator differences vs. PostgreSQL. If the production path is PostgreSQL, using SQLite in development will mask production-specific bugs.

*Why it matters:* JSON attribute querying (the `attributes: JSON` column) has different performance characteristics and slightly different syntax between SQLite and PostgreSQL.

*Options:*
- SQLite dev / PostgreSQL prod — fast setup, risk of behavioral difference
- PostgreSQL everywhere (Docker) — consistent, more setup friction
- Both supported with conditional ORM behavior — complex

*Recommendation direction:* PostgreSQL via Docker from day 1. Add a `docker-compose.yml` in Phase 1. Eliminating the dev/prod parity problem is worth the setup cost.

---

**Q7: What is the MVP definition for "journaling"?**

*The question:* Is MVP journaling a plain textarea per day, or does it require rich text, mood, habits, and prompts from the start?

*Why it matters:* The Journaler archetype will not stick with a plain textarea — they need enough emotional richness to feel the app understands them. But overbuilding journaling in the MVP delays other archetypes.

*Options:*
- Plain textarea + date (minimal) — fast to build, may lose journalers early
- Markdown textarea + mood indicator — medium complexity, most journalers satisfied
- Full rich text + mood + prompts + habits in MVP — overwrought for day 1

*Recommendation direction:* Markdown textarea + mood indicator (1-5 scale) + optional single prompt ("What's one thing you want to remember about today?") in MVP. Sufficient to retain journalers without overcomplicating Phase 1.

---

**Q8: Multi-user / family use case — in or out?**

*The question:* Some users will want to share their planner with a partner or family member (shared grocery list, shared goals). HYPPO is designed as a personal tool — but shared lists are a natural request.

*Why it matters:* Adding sharing to the data model after launch is painful. If sharing is ever in scope, the data model should have `owner_id` vs. `user_id` semantics from day 1.

*Options:*
- Strictly single-user (simplest, cleanest) — build as personal tool only
- Shared lists only (entries can be shared, not accounts) — limited scope
- Full multi-user (teams, families) — too complex for current scope

*Recommendation direction:* Single-user only for MVP and Phase 2. Design the data model with `user_id` as the sole ownership dimension. Revisit in Phase 3 if user feedback demands it. Do NOT architect for sharing preemptively.

---

*End of document*

---

**Document version:** 1.0
**Last updated:** 2026-03-27
**Next action:** Review open questions with decision-makers, select first methodology paradigm to implement, confirm database choice.
