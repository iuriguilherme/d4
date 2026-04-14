# HYPPO Ideation — Open-Ended Phase 2+ Ideas
**Date:** 2026-04-13  
**Status:** Complete — 7 survivors from 40 raw candidates  
**Focus:** Open-ended (no constraint specified)  
**Frames:** User pain/friction · Inversion/automation · Assumption-breaking · Leverage/compounding

---

## Ideation Log

| Session | Date | Action |
|---------|------|--------|
| 001 | 2026-04-13 | Initial ideation — 4 parallel agents, 40 raw candidates → 7 survivors |

---

## Survivors

### 1. Replace Streaks with Rhythms
**Status:** Survivor  
**Frame:** Assumption-breaking  
**Archetype fit:** Habit-Builder, Time-Blocker, all

**What it is:** Abandon streak counts as the primary habit metric. Replace with a *rhythm profile* — a rolling pattern of when and how often a user engages with a habit (e.g., "every 2–3 days, usually morning"). A missed day is only a problem if it breaks the user's *own observed rhythm*, not a universal daily requirement.

**Why it matters:** Streak mechanics are borrowed from gamification and actively harm users with irregular schedules, illness, or travel. HYPPO's own key debts (N+1 queries, timezone-aware streaks, materialized cache) reveal that the current streak model is already wrong. Reframing now prevents compounding a flawed concept into the Phase 2 scoring engine. Rhythm-based tracking is honest about how habits actually form, removes punitive UX, and produces richer behavioral signals than a binary streak count.

**Grounding:** The N+1 streak debt, materialized streak cache debt, and timezone-aware streak debt are all listed. BehaviorEvent timestamps are the raw material for rhythm extraction (time-of-day, day-of-week, interval distribution). `api/app/services/habit_streak.py` is the isolated service to refactor. Rhythm profiles map naturally to archetype scoring — a Habit-Builder who exercises every 2 days is still a Habit-Builder.

**Risks:** Breaking change to the habit UX concept. Users who like streaks lose their existing counts. Rhythm profile visualization is non-trivial (requires a new UI component).

---

### 2. BehaviorEvent Schema Registry
**Status:** Survivor  
**Frame:** Leverage/compounding  
**Archetype fit:** All (infrastructure)

**What it is:** Define a controlled vocabulary of `event_type` values (e.g., `entry.created`, `habit.checked`, `journal.opened`, `export.triggered`) with a lightweight registry module in `api/app/services/` or `api/app/core/`. The registry validates event_type at emission and provides a canonical reference for the scoring engine.

**Why it matters:** BehaviorEvent is the raw signal source for Phase 2 archetype scoring. If different routers emit slightly different strings for the same semantic action, the scoring engine must handle ambiguity or produce noisy scores. Fixing this *before* the scoring engine is built means clean signal from day one. Every new router added in Phase 3 imports one function to emit correctly. The registry compounds in value as the event vocabulary grows.

**Grounding:** BehaviorEvent is append-only with no FK constraints. Events are currently fire-and-forget from `api/app/routers/`. No validation layer exists. The scoring engine in Phase 2 will rely on `event_type` grouping — ambiguous strings are a direct threat to score quality.

**Risks:** Low. This is additive infrastructure. Existing event strings can be grandfathered in with a migration or normalized at read time by the scoring engine.

---

### 3. Archetype Dissolution — Score Behavioral Modes, Not People
**Status:** Survivor  
**Frame:** Assumption-breaking  
**Archetype fit:** All (architecture)

**What it is:** Instead of assigning a user to one dominant archetype, score every *session* or *day* across all six archetype dimensions simultaneously. A user is not a List-Maker — they are 40% List-Maker on Monday mornings and 70% Reflective Journaler on Sunday evenings. The `ArchetypeSnapshot` stores a score vector per time window, not a single label.

**Why it matters:** The archetype-as-identity model will fail users who are contextually different by design (different roles, different days of the week, different life phases). Behavioral modes tied to time/context produce richer adaptation signals and avoid the false taxonomy. Phase 2 UI adaptation can respond to the current session's dominant mode rather than a stale historical label. This is also more honest: no user is just one thing.

**Grounding:** BehaviorEvent is append-only with timestamps — temporal windowing is implicit. `Entry.attributes` GIN JSON can store per-entry mode vector scores without schema changes. `ArchetypeSnapshot` table design can accommodate a JSONB score vector column. Nothing in the current architecture prevents this model; adopting it now avoids a painful rewrite if the single-label model proves too rigid.

**Risks:** More complex than single-label scoring. Requires defining the time window granularity (session vs. day vs. week). UI adaptation logic becomes conditional on "current session mode" rather than a stable label.

---

### 4. Behavioral Debt Surfacing
**Status:** Survivor  
**Frame:** Assumption-breaking  
**Archetype fit:** Goal-Tracker, Habit-Builder, Reflective Journaler

**What it is:** Surface "behavioral debt" to users: habits they've declared but never acted on, entries they've opened but never completed, goals they've created and ignored. Treat this not as failure but as information. The gap between declared intent and actual behavior is surfaced as a non-judgmental prompt: "You created this habit 3 weeks ago and have never checked in — keep it or let it go?"

**Why it matters:** Most productivity apps either hide this gap or create anxiety through accumulating backlogs. Making it visible without judgment gives users agency to recommit or explicitly abandon. The act of explicit abandonment is itself a high-value behavioral signal for archetype scoring. It also differentiates HYPPO from tools that pretend users always follow through.

**Grounding:** BehaviorEvent stores every open, edit, and create event — the raw data for intent-vs-action gap analysis is already being collected. Soft-delete with `deleted_at` means abandoned items persist and are queryable. `Entry.attributes` could store a `declared_intent` field at creation to make gap analysis precise. The "explicit abandonment" action maps naturally to the Anti-Planner concept as a complementary UX moment.

**Risks:** UX sensitivity — surfacing unfulfilled intentions must feel empowering, not shaming. Copy and framing are as important as the feature itself. Requires defining "stale" thresholds that aren't one-size-fits-all.

---

### 5. One-Tap Habit + Journal Co-Creation
**Status:** Survivor  
**Frame:** User pain/friction  
**Archetype fit:** Habit-Builder, Reflective Journaler, Goal-Tracker

**What it is:** When creating any entry, surface the day's unchecked habits as inline checkboxes in the same form. A user logs a journal entry and ticks off habits in a single submit. The form detects which habits haven't been checked today and inlines them automatically via an HTMX partial.

**Why it matters:** Making users navigate to a separate habits page to check in creates friction that compounds daily. Users who journal but forget to check habits get inaccurate streak/rhythm data and eventually stop trusting it. The co-creation moment also captures a high-value behavioral signal: which habits are associated with which journal contexts. This correlation is exactly the kind of signal the archetype scoring engine needs.

**Grounding:** HTMX partials pattern already handles fragment responses. `Entry.attributes` can carry `habit_check_ids` metadata. FastAPI can accept a compound payload or process parallel requests from one HTMX trigger. BehaviorEvent captures the co-occurrence as a behavioral signal. The `X-Session-ID` header already threads the Flask session to FastAPI for event grouping — this event co-occurrence is natively supported.

**Risks:** Compound form submit requires careful API design (atomic or two-phase). If habits list is long, the inline form becomes cluttered — needs a "show first N unchecked" heuristic.

---

### 6. Behavioral Heatmap Calendar
**Status:** Survivor  
**Frame:** User pain/friction  
**Archetype fit:** All

**What it is:** A GitHub-style contribution heatmap showing entry density, habit completion rate, and behavior event volume per day across the past 90 days, surfaced on the dashboard without any user configuration. Intensity varies by activity level. Clicking a day shows a summary of what was created/completed that day.

**Why it matters:** Users have no visual sense of their own consistency or momentum with HYPPO. A heatmap makes long-term patterns visible and creates a "don't break the chain" anchoring effect without the punitive streak mechanic. It also makes HYPPO's adaptive value proposition visible — "look how your patterns have shifted over 3 months." Operators can use it to demonstrate value retention.

**Grounding:** BehaviorEvent is append-only and timestamped — natural heatmap source. Entry and habit checkin data already exists. FastAPI can aggregate with a single date-bucketed query bounded by 90 days (respecting the date lower-bound convention). The GIN index on `Entry.attributes` supports filtered counts. HTMX can load this lazily on dashboard mount without blocking page render.

**Risks:** The aggregation query must be well-bounded (90-day window is safe; unbounded would violate the documented convention). Heatmap rendering in HTMX/Flask templates requires a small JS or CSS grid component.

---

### 7. Retroactive Signal Injection
**Status:** Survivor  
**Frame:** Assumption-breaking / Leverage  
**Archetype fit:** Reflective Journaler, Knowledge-Organizer, all

**What it is:** When a user explicitly categorizes, tags, or edits an old entry, treat that act as a retroactive behavioral signal — a new BehaviorEvent with type `retroactive.tag` or `retroactive.edit`. The timestamp reflects *when the retroactive action occurred*, not the original entry date. The scoring engine weights these differently from forward events.

**Why it matters:** Most event systems only capture forward-in-time actions. Retroactive engagement is a high-intent signal: a user who goes back and labels old entries reveals current cognitive state and priority. This signal is more valuable than the original creation event for archetype scoring. Building the distinction now means the scoring engine can be designed with it from the start rather than bolted on later.

**Grounding:** BehaviorEvent is append-only — a `retroactive.tag` event type is additive. `Entry.attributes` JSON already supports arbitrary metadata so the tag is already storable. The BehaviorEvent Schema Registry (Idea #2) would formalize this event type. This idea compounds with Idea #3 (temporal mode scoring) — retroactive actions contribute to the mode score for the time window when they occurred.

**Risks:** The scoring engine must be designed to weight retroactive events differently (lower than real-time, or differently directed). If this isn't explicit in the scoring model, retroactive tagging could bias archetype scores in misleading ways.

---

## Rejected Candidates (Reasons)

| Idea | Rejection Reason |
|------|-----------------|
| Zero-Input Habit Tracking via NLP | Requires NLP infrastructure not in stack. Over-engineered for Phase 2 signal density. |
| Offline-First Entry Drafts (localStorage sync) | Complex failure modes; localStorage sync queue is significant scope; HTMX not designed for offline-first. |
| Automatic Sensitivity Detection for Journal | Requires ML/NLP; manual privacy lock covers the need with far less risk. |
| Two-Service Split Architectural Critique | Valid concern but not actionable without major rewrite. BackgroundTasks covers Phase 2 need. |
| Methodology Agnosticism as Liability | Premature — insufficient behavioral data to know which archetypes to bet on. Revisit after Phase 2 data. |
| Ambient Daily Digest Email/Webhook | Requires email/webhook infra not in stack. Lower urgency than data quality. |
| Automated Token Lifecycle (invisible refresh) | Retry-on-401 with refresh has race conditions in httpx. Flask 401 redirect covers 80% of need. |
| Behavior-Driven UI Declutter | High implementation surface. Requires complete UI inventory and absence-of-behavior detection. |
| Operator Audit Log for Export | Premature for single-user MVP. Add when multi-user deployment is targeted. |
| Scheduled Auto-Export | Requires cron infra. Lower urgency than data quality issues. |
| Passive Archetype Scoring (no questionnaire) | Already committed as Phase 2 core. Not an idea — it's the plan. |
| ArchetypeSnapshot Table | Already flagged in AGENTS.md as a prerequisite. Not an idea — it's a known debt. |
| Flask 401 → Login Redirect | Pre-planned debt. Must ship but not an ideation output. |
| Materialized Streak Cache | Pre-planned debt. Must ship but not an ideation output. |
| Soft-Delete ORM Mixin | Pre-planned debt. Must ship but not an ideation output. |
| BehaviorEvent Partitioning | Pre-planned debt. Must ship but not an ideation output. |
| Timezone-Aware Date Boundary Service | Pre-planned debt. Must ship but not an ideation output. |

---

## Debt Reminder (Not Ideas — Must Ship)

These are pre-planned debts that should be resolved *before* Phase 2 feature work begins:

1. **Refresh token revocation** — security gap (logout does not invalidate refresh token)
2. **Flask 401 → login redirect** — UX correctness for all HTMX routes
3. **Materialized streak cache** — N+1 performance debt
4. **Soft-delete ORM mixin** — prevents silent data surface bugs in new queries
5. **Timezone-aware streak computation** — correctness for non-UTC users
6. **BehaviorEvent partitioning** — infrastructure scale, do while table is small
7. **ArchetypeSnapshot table** — prerequisite before scoring engine starts

---

## Cross-Cutting Combinations Identified

**Rhythm Transparency Dashboard** (Ideas #1 + #4):  
Surface a user's actual rhythm profile alongside their behavioral debt — "You said daily, you do every 2–3 days, and that's fine — here's what that actually looks like." Combines rhythm-based habit tracking with explicit gap visibility. More honest and differentiated than either feature alone.

**Temporal Archetype Memory** (Ideas #3 + #7):  
Temporal mode scoring (Idea #3) treats time windows as the unit of archetype measurement. Retroactive signal injection (Idea #7) contributes retroactive actions to the time window they semantically belong to (via original entry date). Together, these produce a scoring model that is both temporally honest and signal-rich from day one.

---

## Next Steps

Use `ce:brainstorm` to pick one survivor and define it precisely enough for planning.

Suggested priority order based on leverage and Phase 2 dependency:
1. **BehaviorEvent Schema Registry** (#2) — blocks Phase 2 scoring engine quality; low risk; do first
2. **Archetype Dissolution** (#3) — shapes Phase 2 architecture; should be decided before `ArchetypeSnapshot` table is created
3. **Replace Streaks with Rhythms** (#1) — highest user impact; reframes core mechanic; resolves multiple debts
4. **Behavioral Heatmap Calendar** (#6) — high visual impact; no dependencies; quick win
5. **One-Tap Habit + Journal Co-Creation** (#5) — immediate friction fix; Phase 2 behavior signal enrichment
6. **Behavioral Debt Surfacing** (#4) — unique UX differentiator; requires behavioral data density first
7. **Retroactive Signal Injection** (#7) — high-value signal; pairs with scoring engine design
