---
title: "feat: Build HYPPO MVP Foundation (Phase 1)"
type: feat
status: active
date: 2026-04-07
origin: docs/brainstorms/001-planner-brainstorm.md
---

# feat: Build HYPPO MVP Foundation (Phase 1)

## Overview

This plan covers the complete Phase 1 build of HYPPO — the Hyper Personalized Planner and Organizer — bringing the application from zero to a deployed, usable MVP that any user archetype can adopt on day one. Phase 1 does not include UI personalization (that is Phase 2), but it lays all the architectural foundations that make personalization possible: behavioral event collection, methodology-agnostic data model, and a clean two-tier FastAPI/Flask service boundary.

Scope: build sequence items 1–7 from the brainstorm (Weeks 1–4). Phases 2 and 3 (personalization engine, archetype-adapted views) require separate plans.

## Problem Frame

Most planner apps force users into a fixed methodology (GTD, BuJo, time-blocking) that often does not match how they naturally work. Users either abandon the tool or adapt themselves to it at the cost of friction. HYPPO inverts this: the tool adapts to the user over time through passive behavioral observation.

Phase 1 produces the minimum viable surface: a usable daily planner with tasks, notes, habits, and journaling. Critically, it also begins recording the behavioral signal data that Phase 2's personalization engine will consume. Starting event collection from day one is a non-negotiable architectural requirement — losing the first weeks of user behavior data is not recoverable.

(see origin: docs/brainstorms/001-planner-brainstorm.md — §1, §8.1, §8.4)

## Requirements Trace

- R1. A user can register, authenticate, and maintain a secure session
- R2. A user can capture any text in a universal input; it defaults to a `note` type without friction
- R3. A user can view, navigate, and interact with a daily log of entries
- R4. A user can create tasks and mark them complete
- R5. A user can write a journal entry with Markdown formatting and an optional mood rating
- R6. A user can define habits and record daily check-ins with streak tracking
- R7. All user interactions generate `BehaviorEvent` records from day one
- R8. A user can export all their data as JSON
- R9. The API is mobile-ready by design (UUID PKs, client-generated IDs, pagination, versioned endpoints)
- R10. Flask never queries the database directly — FastAPI is the sole data owner

## Scope Boundaries

- Phase 2 features are out of scope: archetype scoring, UI adaptation, terminology changes, insight prompts
- No Pomodoro timer, calendar sync, push notifications, or data import
- No sharing, multi-user, or team features — single-user only throughout
- No rich text beyond Markdown (no WYSIWYG editor in Phase 1)
- No mobile app — FastAPI is designed for mobile readiness, but no client ships in Phase 1
- PARA structure, note linking, and full-text search are Phase 3 features

## Context & Research

### Relevant Code and Patterns

- No existing code — greenfield project
- Tech stack confirmed in brainstorm: FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL (prod) / PostgreSQL via Docker (dev)
- Flask (not Quart) for web layer in Phase 1; Quart migration deferred to when WebSockets are needed
- HTMX for partial page updates; no JavaScript framework
- Jinja2 for server-side templates
- httpx for Flask-to-FastAPI HTTP communication

### Institutional Learnings

- None available yet (first plan for this project)

### External References

- FastAPI dependency injection docs: https://fastapi.tiangolo.com/tutorial/dependencies/
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic migration guide: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- HTMX reference: https://htmx.org/reference/

## Key Technical Decisions

- **UUID primary keys everywhere**: Required for client-generated IDs to support offline sync in future mobile clients. Changing PK type later requires full table rewrites. (see origin: §8.4)
- **`attributes: JSON` on Entry**: A single flexible JSON column enables all methodology-specific fields (task due date, time block start/end, OKR metric type, mood score) without schema migrations for each new archetype feature. Queried with GIN index on PostgreSQL. (see origin: §6.2, §6.4)
- **Soft deletes**: `deleted_at` timestamp instead of hard DELETE. Protects user data, enables recovery. Applied to Entry; Habit and User use separate archival patterns. (see origin: §8.4)
- **JWT authentication, not server-side sessions**: Access tokens (15 min) + refresh tokens (30 days, HttpOnly cookie). Flask stores JWT in server-side session, exchanges on every FastAPI call. Mobile clients will store in keychain/keystore. (see origin: §7.2)
- **API versioning prefix `/api/v1/`**: Once mobile clients exist, URL structure cannot change. Prefix from day one is cheap insurance. (see origin: §7.4)
- **Flask and FastAPI as separate processes**: Communication via httpx. Flask never touches the database. FastAPI is the single point of data access. (see origin: Q2 decision, §7.3)
- **Capture defaults to `note`, not task**: Free-text input must never interrupt the user's writing flow. Type is assigned during a separate review mindset, not during capture. Notes gain a `review_status` field. (see origin: Q3 decision, §6.2)
- **`BehaviorEvent` is append-only, permanent, immutable**: The raw behavioral history is the source of truth for the personalization engine. No TTL, no pruning, no archiving. `ArchetypeSnapshot` stores daily score vectors for read performance (added in Phase 2, but the table schema should be created in Phase 1 to avoid migrations during the active personalization build). (see origin: Q1 decision)
- **PostgreSQL via Docker from day one**: Eliminates dev/prod JSON operator differences. SQLite is not used even in development. (see origin: Q6 decision)
- **BehaviorEvent granularity: interaction-level**: Capture meaningful semantic events (`entry_created`, `task_completed`, `feature_opened`, `habit_checked`) with rich metadata. No sub-interaction tracking (no keystroke or scroll events). (see origin: Q4 recommendation)

## Open Questions

### Resolved During Planning

- **Q1 (personalization state storage)**: Decided in brainstorm — BehaviorEvent is permanent source of truth, ArchetypeSnapshot for read performance
- **Q2 (Flask-FastAPI communication)**: Decided in brainstorm — separate processes, httpx HTTP calls
- **Q3 (capture type inference)**: Decided in brainstorm — defaults to note, review queue is separate workflow
- **Q6 (dev database)**: Decided in brainstorm — PostgreSQL via Docker from day one
- **Q8 (multi-user)**: Out of scope — single-user only; data model uses `user_id` as sole ownership dimension

### Deferred to Implementation

- **FastAPI internal IPC (Q2 open research note)**: The brainstorm notes that Unix domain sockets or gRPC could improve same-host latency over TCP loopback. This is an optimization to evaluate after the HTTP baseline works. Implement HTTP first; measure before optimizing.
- **BehaviorEvent volume management**: The brainstorm notes the table will grow large and suggests monthly partitioning. Partitioning is a Phase 2+ operational concern — design the schema to support it (timestamp-partitionable), but do not implement partitioning in Phase 1.
- **Exact HTMX swap targets**: The specific `hx-target` selectors depend on the actual template structure chosen during implementation. The plan specifies HTMX for which interactions but not the exact attribute values.
- **Flask-Session backend**: Redis or filesystem. Filesystem is acceptable for single-instance development; Redis is preferred for production. Choose during deployment configuration, not here.
- **Q5 (adaptation UX anti-creepiness)**: This is a Phase 2 concern. The UX strategy (subtle with opt-out, "Your HYPPO is evolving" framing) is noted in the brainstorm but not implemented in Phase 1.
- **Q7 (MVP journaling depth)**: The plan implements Markdown textarea + mood (1-5) + one optional prompt — the brainstorm's recommended middle ground. Full rich text and additional prompts are Phase 2.

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

### Service Boundary and Request Flow

```
Browser
  │
  │  Full HTML page (Jinja2 SSR)
  │  Partial HTML fragment (HTMX swap)
  ▼
Flask Web Layer  (port 5000)
  - Session management (Flask-Session)
  - Auth cookie → JWT extraction
  - Template rendering (Jinja2)
  - No direct DB access
  │
  │  HTTP JSON (httpx, Bearer JWT)
  ▼
FastAPI API Layer  (port 8000)
  - Business logic
  - Auth validation (JWT)
  - Pydantic request/response models
  - Background tasks (BehaviorEvent emission)
  - Clean REST endpoints
  │
  │  SQLAlchemy async ORM
  ▼
PostgreSQL  (Docker, port 5432)
  - entries (with GIN index on attributes)
  - habits
  - behavior_events (append-only)
  - archetype_snapshots (Phase 2 reads; Phase 1 creates empty table)
  - sessions (aggregated analytics)
  - users
  - tags
```

### Entry Type Decision Tree (Capture Flow)

```
User types into universal capture box
  │
  ▼
Text is saved immediately as Entry(type=note, review_status=pending)
  │
  ├── [Power user path]
  │   Type selector visible but secondary
  │   User can set type explicitly at capture time
  │
  └── [Default path]
      Entry sits in review queue
      During dedicated review workflow:
        System heuristics suggest a type (stored as metadata, not applied)
        User confirms → type updated, review_status=reviewed
        User dismisses → review_status=dismissed, remains note
```

## Implementation Units

- [ ] **Unit 1: Project Scaffold and Infrastructure**

**Goal:** Establish the project structure, Docker environment, and development tooling so all subsequent units have a consistent foundation.

**Requirements:** R9, R10

**Dependencies:** None

**Files:**
- Create: `docker-compose.yml`
- Create: `pyproject.toml` (or `requirements/base.txt`, `requirements/api.txt`, `requirements/web.txt`)
- Create: `api/` directory structure (FastAPI service)
- Create: `web/` directory structure (Flask service)
- Create: `.env.example`
- Create: `Makefile` (or equivalent runner: `make dev`, `make migrate`, `make test`)

**Approach:**
- Two top-level service directories: `api/` for FastAPI, `web/` for Flask
- Docker Compose runs PostgreSQL, the FastAPI service, and the Flask service as three separate containers
- Environment variables configure service URLs, DB DSN, JWT secrets — no hardcoded values
- `FASTAPI_BASE_URL` env var controls Flask's API target (defaults to `http://api:8000` in Docker, `http://localhost:8000` for direct runs)
- Python dependency management: separate requirements or a monorepo pyproject with extras

**Patterns to follow:** Standard FastAPI application layout (`api/app/main.py`, `api/app/routers/`, `api/app/models/`, `api/app/schemas/`, `api/app/dependencies/`)

**Test scenarios:**
- Test expectation: none — this unit is pure project scaffolding with no behavioral logic. Validate by confirming `docker-compose up` starts all three services without errors.

**Verification:**
- `docker-compose up` raises all three services cleanly
- FastAPI docs page is reachable at `http://localhost:8000/docs`
- Flask renders a placeholder page at `http://localhost:5000`
- No service queries the database from the Flask container

---

- [ ] **Unit 2: FastAPI Authentication**

**Goal:** Implement JWT-based user registration, login, logout, and token refresh. All subsequent API endpoints are protected by auth middleware.

**Requirements:** R1, R9

**Dependencies:** Unit 1 (project structure and DB running)

**Files:**
- Create: `api/app/models/user.py` (SQLAlchemy User model)
- Create: `api/app/schemas/auth.py` (Pydantic request/response models)
- Create: `api/app/routers/auth.py` (`/api/v1/auth/token`, `/api/v1/auth/refresh`, `/api/v1/auth/register`, `DELETE /api/v1/auth/token`)
- Create: `api/app/dependencies/auth.py` (`get_current_user` dependency)
- Create: `api/app/core/security.py` (JWT encoding/decoding, password hashing)
- Create: `alembic/versions/001_create_users.py` (first migration)
- Test: `api/tests/test_auth.py`

**Approach:**
- User model: UUID PK, email (unique), password_hash, created_at, timezone (default UTC), preferences (JSON), push_tokens (JSON, empty for now)
- Access token: 15-minute expiry, signed HS256 or RS256
- Refresh token: 30-day expiry, stored as HttpOnly cookie on the `/api/v1/auth/refresh` endpoint
- `get_current_user` dependency injected on every protected route — validates access token, returns User ORM object
- Password hashing: bcrypt via `passlib`
- Registration endpoint returns the user object (no auto-login); login returns access token + sets refresh cookie
- Alembic: initialize migrations and create first version for the users table

**Patterns to follow:** FastAPI official OAuth2 password flow example; `Depends(get_current_user)` pattern from brainstorm §7.2

**Test scenarios:**
- Happy path: POST `/api/v1/auth/register` with valid email+password → 201, user object returned
- Happy path: POST `/api/v1/auth/token` with correct credentials → 200, access token returned, refresh cookie set
- Error path: POST `/api/v1/auth/token` with wrong password → 401
- Error path: Access protected endpoint without token → 401
- Error path: Access protected endpoint with expired token → 401
- Happy path: POST `/api/v1/auth/refresh` with valid refresh cookie → new access token returned
- Edge case: Register with duplicate email → 409 Conflict
- Error path: Register with malformed email → 422 Unprocessable Entity

**Verification:**
- All test scenarios pass
- `GET /api/v1/users/me` (protected) returns 401 without token and the user object with valid token

---

- [ ] **Unit 3: Core Data Model and Entry CRUD**

**Goal:** Define the methodology-agnostic data schema (`Entry`, `Tag`, `Habit`, `BehaviorEvent`, `Session`, `ArchetypeSnapshot`) and expose basic Entry CRUD endpoints.

**Requirements:** R2, R3, R4, R5, R7, R9

**Dependencies:** Unit 2 (User model and auth dependency exist)

**Files:**
- Create: `api/app/models/entry.py` (Entry SQLAlchemy model)
- Create: `api/app/models/habit.py` (Habit model — definition only, not check-ins)
- Create: `api/app/models/behavior.py` (BehaviorEvent, Session, ArchetypeSnapshot models)
- Create: `api/app/models/tag.py` (Tag model)
- Create: `api/app/schemas/entry.py` (Pydantic schemas for Entry CRUD)
- Create: `api/app/routers/entries.py`
- Create: `alembic/versions/002_create_core_schema.py`
- Test: `api/tests/test_entries.py`

**Approach:**

*Entry model fields:*
- `id: UUID` (client-generated, server accepts and rejects on collision)
- `user_id: UUID` (FK → users.id)
- `type: Enum` (task, note, event, habit_checkin, goal, time_block, review)
- `content: str`
- `content_rich: JSON | null`
- `created_at: datetime`, `updated_at: datetime`, `deleted_at: datetime | null` (soft-delete)
- `entry_date: date` (the logical date this entry belongs to)
- `attributes: JSON` — GIN-indexed on PostgreSQL for flexible attribute queries
- `tags: ARRAY(str)` or join to Tag table — decide at implementation; ARRAY is simpler for Phase 1
- `parent_id: UUID | null` (self-referential FK for hierarchy)
- `review_status: Enum(pending, reviewed, dismissed) | null` — null for non-note types

*Entry REST endpoints:*
- `POST /api/v1/entries` — create (accepts client-generated `id`)
- `GET /api/v1/entries` — list (filter by `date`, `type`, `tags`; paginated with `?page=&per_page=`)
- `GET /api/v1/entries/{id}` — single entry
- `PATCH /api/v1/entries/{id}` — partial update (content, attributes, type, review_status)
- `DELETE /api/v1/entries/{id}` — soft-delete (sets `deleted_at`, never hard-deletes)

*ArchetypeSnapshot table (created now, populated by Phase 2):*
- `id: UUID`, `user_id: UUID`, `date: date`, `scores: JSON` (the score vector), `created_at: datetime`
- Create the table and model now so Phase 2 does not require a migration against a live database

*BehaviorEvent schema:*
- `id: UUID`, `user_id: UUID`, `event_type: str`, `event_data: JSON`, `occurred_at: datetime`, `session_id: UUID`
- No endpoints in this unit — BehaviorEvent is written internally, not via client API

**Patterns to follow:**
- `attributes->>'key'` JSON queries with GIN index
- Soft-delete pattern: all list endpoints filter `WHERE deleted_at IS NULL`
- Pagination: `?page=1&per_page=50` on all list endpoints

**Test scenarios:**
- Happy path: POST entry with `type=note`, no `id` provided → server generates UUID, returns 201 with entry
- Happy path: POST entry with client-provided `id` (UUID) → server accepts that ID, returns same UUID in response
- Happy path: GET entries filtered by `date=2026-04-07` → returns only entries for that date
- Happy path: PATCH entry `type` from `note` to `task` → succeeds, `review_status` updated to `reviewed`
- Happy path: DELETE entry → `deleted_at` set, entry excluded from subsequent list queries
- Edge case: POST entry with duplicate client-provided `id` → 409 Conflict
- Edge case: GET entries with no `date` filter → returns paginated list (default: today)
- Integration: Create entry → list entries → entry appears in list → delete → entry no longer in list

**Verification:**
- GIN index created on `entries.attributes` in migration
- Soft-deleted entries never appear in list or single-get endpoints
- Client-provided UUIDs are accepted and round-tripped correctly

---

- [ ] **Unit 4: Flask Web Layer Skeleton**

**Goal:** Stand up the Flask application with session management, a working login/logout flow, and a reusable HTTP client wrapper for all FastAPI calls.

**Requirements:** R1, R10

**Dependencies:** Units 2 and 3 (FastAPI auth and entries endpoints are live)

**Files:**
- Create: `web/app/__init__.py` (Flask app factory)
- Create: `web/app/auth/routes.py` (login, logout, register views)
- Create: `web/app/auth/templates/login.html`, `register.html`
- Create: `web/app/api_client.py` (httpx wrapper — all FastAPI HTTP calls centralized here)
- Create: `web/app/templates/base.html` (layout with HTMX CDN script tag)
- Create: `web/config.py` (reads `FASTAPI_BASE_URL` from env)
- Test: `web/tests/test_auth_views.py`

**Approach:**
- Flask app factory pattern (`create_app(config)`)
- Flask-Session configured with filesystem backend (Redis deferred to deployment config)
- `api_client.py` is the single place where httpx calls are made — every other module imports from here, never imports httpx directly. This enforces that Flask never touches the database and makes the contract testable.
- Auth flow: login form → `api_client.login(email, password)` → JWT stored in server-side session → redirect to daily log
- Logout: clears session, calls `DELETE /api/v1/auth/token`
- `@login_required` decorator checks session for valid JWT; if absent, redirects to `/login`
- `base.html` loads HTMX from CDN, defines nav skeleton, includes a flash message block

**Patterns to follow:**
- Flask application factory: `create_app()` in `web/app/__init__.py`
- All API calls through `api_client.py` — never inline httpx in route handlers
- `current_user` context processor injects user info from session into all templates

**Test scenarios:**
- Happy path: GET `/login` → renders login form
- Happy path: POST `/login` with correct credentials → session contains JWT, redirects to `/`
- Error path: POST `/login` with wrong credentials → re-renders login with error message
- Happy path: GET `/logout` with active session → session cleared, redirected to `/login`
- Error path: GET protected route without session → redirected to `/login`
- Integration: Login → access protected route → see rendered page (not redirect)

**Verification:**
- No database imports exist anywhere in `web/`
- `api_client.py` is the only file in `web/` that imports `httpx`
- Login/logout round-trip works end-to-end with FastAPI running

---

- [ ] **Unit 5: Daily Log View and Universal Capture**

**Goal:** The core product loop — a user opens HYPPO, sees today's entries, and can capture new ones. Tasks can be completed. Notes can be created. Date navigation works.

**Requirements:** R2, R3, R4

**Dependencies:** Unit 4 (Flask web layer with auth), Unit 3 (entries API)

**Files:**
- Create: `web/app/log/routes.py` (`/` → today's log, `/<date>` → specific date log)
- Create: `web/app/log/templates/log.html` (daily log view)
- Create: `web/app/log/templates/_entry.html` (HTMX partial — single entry row, rendered on create/update)
- Create: `web/app/log/templates/_capture.html` (HTMX partial — capture input form)
- Modify: `web/app/templates/base.html` (add log nav link)
- Test: `web/tests/test_log_views.py`

**Approach:**
- `GET /` renders today's log: calls `api_client.list_entries(date=today)`, renders `log.html`
- `GET /<YYYY-MM-DD>` renders a specific date's log (past or future)
- Universal capture input: a single `<textarea>` or `<input>` at the top of the log. On submit, `hx-post="/entries"` creates the entry, receives back the `_entry.html` partial, and prepends it to the log list — no page reload.
- The capture input has a small, non-prominent type selector (dropdown: Note / Task / Event). Default is Note. This is the "power user escape hatch" from the brainstorm Q3 decision.
- Task completion: the checkbox on each task entry triggers `hx-patch="/entries/{id}"` with `{attributes: {completed: true}}`. The server returns the updated `_entry.html` partial. The checkbox shows a strike-through in the rendered partial.
- Date navigation: prev/next day links update the full page (not HTMX partial — simpler for now)
- `review_status=pending` badge on new notes — indicates the entry is in the review queue

**Patterns to follow:**
- HTMX `hx-post`, `hx-target`, `hx-swap="outerHTML afterbegin"` for capture
- HTMX `hx-patch`, `hx-target="closest li"`, `hx-swap="outerHTML"` for task completion
- Server returns HTML partials (not JSON) from Flask log routes; Flask routes call FastAPI, then render the partial template

**Test scenarios:**
- Happy path: GET `/` with 3 entries for today → all 3 entries rendered in log
- Happy path: POST capture form with text → new note entry appears at top of log (HTMX swap)
- Happy path: Check task checkbox → entry updates in place, shows completed state
- Edge case: GET `/2026-01-01` (past date) → renders that day's log, navigation shows correct prev/next links
- Edge case: GET `/` with no entries for today → empty state message rendered
- Integration: Create entry via capture → entry appears in log → complete task → entry shows completed state without page reload

**Verification:**
- Capture creates an entry with `type=note` and `review_status=pending` by default
- Completing a task does not reload the page
- Past date navigation works correctly

---

- [ ] **Unit 6: Journal Entry View**

**Goal:** A dedicated journaling interface — a richer daily entry with Markdown formatting, an optional mood indicator (1-5), and one optional writing prompt.

**Requirements:** R5

**Dependencies:** Unit 5 (daily log view, entry model is live)

**Files:**
- Create: `web/app/journal/routes.py` (`GET/POST /journal/<date>`)
- Create: `web/app/journal/templates/journal.html` (journal entry editor)
- Create: `web/app/journal/templates/_journal_preview.html` (rendered Markdown preview partial)
- Modify: `web/app/templates/base.html` (add journal nav link)
- Test: `web/tests/test_journal_views.py`

**Approach:**
- Journal entry is an `Entry` with `type=note` and specific attributes: `{"entry_subtype": "journal", "mood": 3, "prompt_response": "..."}`
- One journal entry per date per user — GET the journal for a date loads the existing entry if present; POST creates or updates it (upsert by `entry_date + user_id + subtype=journal`)
- Markdown rendering: client-side using a small library (e.g., marked.js via CDN), or server-side via Python `markdown` library — choose at implementation based on simplicity. Server-side is more consistent with the no-JS-framework principle.
- Mood selector: 5 emoji or star buttons (1=lowest, 5=highest). Stored in `attributes.mood`.
- Writing prompt: "What's one thing you want to remember about today?" — displayed as placeholder text, not a required field. The response is stored in `attributes.prompt_response`.
- Auto-save: HTMX `hx-trigger="keyup changed delay:1500ms"` posts the textarea content to the server at intervals. This avoids a manual save button. Server responds with a "saved" indicator partial.

**Patterns to follow:**
- Entry upsert pattern (find by `entry_date + user_id + attributes.entry_subtype`, create if not found)
- HTMX auto-save: `hx-trigger="keyup changed delay:1500ms"` on the editor textarea

**Test scenarios:**
- Happy path: GET `/journal/2026-04-07` with no existing entry → blank editor with prompt placeholder
- Happy path: GET `/journal/2026-04-07` with existing entry → editor pre-populated with saved content
- Happy path: Type in editor → auto-save fires → "Saved" indicator appears
- Happy path: Set mood to 4 → mood persisted in entry attributes
- Edge case: GET `/journal/2026-04-07` twice in same session → same entry loaded, not two entries created
- Integration: Write journal → navigate away → return to `/journal/2026-04-07` → content preserved

**Verification:**
- Only one journal entry exists per user per date (upsert, not insert)
- Mood is stored and retrieved correctly from `attributes.mood`
- Auto-save does not create duplicate entries

---

- [ ] **Unit 7: Habits MVP**

**Goal:** A user can define up to 5 daily habits, check them off each day, and see their streak count. This is the minimum needed to retain Habit-Builder archetype users.

**Requirements:** R6, R7

**Dependencies:** Unit 3 (entry model for habit_checkin type), Unit 4 (Flask auth)

**Files:**
- Create: `api/app/routers/habits.py` (`POST /api/v1/habits`, `GET /api/v1/habits`, `POST /api/v1/habits/{id}/checkin`, `DELETE /api/v1/habits/{id}`)
- Create: `api/app/schemas/habit.py` (Pydantic schemas)
- Create: `api/app/services/habit_streak.py` (streak computation logic)
- Create: `web/app/habits/routes.py`
- Create: `web/app/habits/templates/habits.html` (habit board view)
- Create: `web/app/habits/templates/_habit_row.html` (HTMX partial — single habit with check button)
- Modify: `web/app/templates/base.html` (add habits nav link)
- Test: `api/tests/test_habits.py`
- Test: `web/tests/test_habit_views.py`

**Approach:**
- `Habit` model (definition): `id`, `user_id`, `name`, `description`, `frequency` (daily only in Phase 1; weekday variants deferred), `target_value` (default 1 = binary), `unit`, `created_at`, `archived_at`, `color`, `icon`
- Daily check-in is recorded as an `Entry(type=habit_checkin)` with `attributes: {"habit_id": "...", "value": 1, "target": 1}`
- This means check-ins appear in the daily log — they are visible as part of the day's record, not siloed
- `POST /api/v1/habits/{id}/checkin` checks if a checkin already exists for today's `entry_date`; if so, it returns the existing one (idempotent). This prevents double-check-ins.
- Streak: computed by `habit_streak.py` — walks back through `habit_checkin` entries for the habit, counts consecutive days. Runs server-side per request in Phase 1; a cached/materialized version is Phase 2.
- MVP limit: 5 habits per user. Return 400 if user tries to create a 6th.
- Habit check-in on the board: checkbox triggers `hx-post="/habits/{id}/checkin"`. Server responds with updated `_habit_row.html` partial showing the new streak count.

**Patterns to follow:**
- Idempotent check-in (same day, same habit → same result, no duplicate)
- Streak computed from `Entry` table query — no separate state to maintain
- BehaviorEvent emitted on `habit_checked` (see Unit 8)

**Test scenarios:**
- Happy path: POST new habit with name → habit created, returned with streak=0
- Happy path: POST checkin for today → `habit_checkin` entry created, streak becomes 1
- Edge case: POST checkin for today twice → second call is idempotent, returns same entry, streak still 1
- Happy path: Check in 3 consecutive days → streak is 3
- Edge case: Miss a day, check in again → streak resets to 1
- Error path: Attempt to create a 6th habit → 400 with clear error message
- Integration: Create habit → check in → habit board shows streak updated without page reload

**Verification:**
- Streak computation is correct for consecutive days with a gap
- Double check-in on the same day does not create two entries
- Habit check-in entries appear in the daily log for the corresponding date

---

- [ ] **Unit 8: BehaviorEvent Collection**

**Goal:** Instrument all significant user interactions with `BehaviorEvent` records so the Phase 2 personalization engine has data from the first day of production.

**Requirements:** R7

**Dependencies:** Units 3–7 (all features to be instrumented are built)

**Files:**
- Create: `api/app/services/behavior.py` (event emission service — `emit_event(user_id, event_type, event_data, session_id)`)
- Create: `api/app/services/session_tracker.py` (session open/close, Session record aggregation)
- Modify: `api/app/routers/entries.py` (add event emission via FastAPI `BackgroundTasks`)
- Modify: `api/app/routers/habits.py` (add event emission)
- Modify: `api/app/routers/auth.py` (emit `user_login` event)
- Create: `api/app/routers/analytics.py` (`GET /api/v1/analytics/behavior` — current raw events for user, paginated)
- Test: `api/tests/test_behavior.py`

**Approach:**
- Events are emitted via FastAPI `BackgroundTasks` — the main request completes first, then the event is written. This ensures event emission never delays API responses.
- `emit_event` writes to `behavior_events` table. The function is fire-and-forget from the route's perspective.
- Events to emit in Phase 1:
  - `entry_created` — `{entry_type, word_count, has_time, entry_date, hour_of_day}`
  - `task_completed` — `{entry_id, time_to_complete_seconds (if known)}`
  - `habit_checked` — `{habit_id, streak_at_time}`
  - `feature_opened` — `{feature_name}` (log view, journal, habits — emitted from Flask via a lightweight API call)
  - `user_login` — `{hour_of_day, day_of_week}`
- `session_id` is a UUID generated at login time and stored in the Flask session. It is passed in requests from Flask to FastAPI via a custom header (`X-Session-ID`). This allows BehaviorEvents to be grouped by session.
- `Session` aggregate record: created when session ends (logout or timeout) with summary stats (duration, entry_count, word_count, features_used). The aggregate is derived from BehaviorEvents for the session.
- `analytics/behavior` endpoint: not used by the web UI in Phase 1, but available for debugging and Phase 2 engineering validation.

**Patterns to follow:**
- FastAPI `BackgroundTasks` for async fire-and-forget event writes
- No event data should contain PII beyond `user_id` (no email, no raw entry content)
- `BehaviorEvent` table has no foreign key constraints to other tables (events must survive even if related entities are soft-deleted)

**Test scenarios:**
- Happy path: Create an entry → `behavior_events` table contains `entry_created` event with correct metadata
- Happy path: Complete a task → `task_completed` event emitted
- Happy path: Check in a habit → `habit_checked` event with correct streak value emitted
- Integration: Create 3 entries, complete 2 tasks → `GET /api/v1/analytics/behavior` returns 5 events for the session
- Error path: BehaviorEvent write failure → main API response is unaffected (background task failure is logged, not propagated)
- Edge case: Entry created with empty content → word_count in event data is 0

**Verification:**
- All instrumented actions produce corresponding BehaviorEvent records
- Main API response latency is not increased by event emission (background tasks verified async)
- Events table has no entries for soft-deleted users (soft-delete of a user cascades to events in Phase 2; in Phase 1, simply confirmed not required)

---

- [ ] **Unit 9: Settings and Data Export**

**Goal:** User can set timezone and theme preferences, and export all their data as a JSON file.

**Requirements:** R8, R1 (preferences on User entity)

**Dependencies:** Unit 4 (Flask web layer), Unit 3 (all entity types exist)

**Files:**
- Create: `api/app/routers/users.py` (`GET /api/v1/users/me`, `PATCH /api/v1/users/me`, `GET /api/v1/users/me/export`)
- Create: `api/app/schemas/user.py`
- Create: `api/app/services/export.py` (assembles full user data export as Python dict → JSON)
- Create: `web/app/settings/routes.py`
- Create: `web/app/settings/templates/settings.html`
- Test: `api/tests/test_users.py`

**Approach:**
- `PATCH /api/v1/users/me`: accepts partial updates to `preferences` (theme: light/dark, timezone string) and top-level fields. Does not accept email or password changes via this endpoint (those are separate auth operations).
- `GET /api/v1/users/me/export`: assembles all of the user's non-deleted entries, habits, habit check-ins, and tags into a single JSON structure, streamed as a file download. This is synchronous in Phase 1 (acceptable for small data sets); background job generation is Phase 3.
- Export format:
  ```json
  {
    "exported_at": "...",
    "user": {"id": "...", "email": "...", "timezone": "...", "created_at": "..."},
    "entries": [...],
    "habits": [...],
    "tags": [...]
  }
  ```
- Theme preference stored in `User.preferences` JSON field. Flask reads it from the session and adds a `data-theme` attribute to `base.html`'s `<html>` tag for CSS dark mode targeting.

**Patterns to follow:**
- `PATCH` with partial update (only provided fields updated, others unchanged)
- JSON export: deterministic field ordering for readability

**Test scenarios:**
- Happy path: PATCH timezone to `America/Sao_Paulo` → GET `/users/me` returns updated timezone
- Happy path: PATCH theme to `dark` → preference persisted in user record
- Happy path: GET `/users/me/export` with 10 entries, 2 habits → JSON contains all entries and habits, correct structure
- Edge case: GET export with no data → valid JSON with empty arrays
- Error path: PATCH with invalid timezone string → 422 Unprocessable Entity

**Verification:**
- Export contains all non-deleted entries including habit check-ins
- Theme preference survives logout/login cycle (stored on User, not just in session)
- Export JSON is valid and parseable

## System-Wide Impact

- **Interaction graph:** Every entry creation, task completion, and habit check-in emits a BehaviorEvent via FastAPI BackgroundTasks. Flask routes that open major views emit `feature_opened` events via a lightweight side-channel API call. The `session_id` header threads through all requests from Flask to FastAPI, linking events to sessions.
- **Error propagation:** FastAPI returns `{"error": {"code": "...", "message": "...", "field": "..."|null}}` for all error responses. Flask api_client wraps these and either re-raises or logs, depending on severity. BehaviorEvent write failures are logged but never propagate to the main request path.
- **State lifecycle risks:** Soft-delete semantics must be enforced at the ORM level (not just in routes) via a custom query filter that appends `WHERE deleted_at IS NULL`. Without this, soft-deleted entries could re-appear if a developer writes a raw query. Consider a SQLAlchemy session event or mixin that adds this filter automatically.
- **API surface parity:** The Flask web layer is a client of the API, not a co-owner. Any behavior reachable through the web UI must be achievable via the FastAPI API directly. This is the foundation for future mobile and API access.
- **Integration coverage:** The HTMX partial-swap pattern means Flask routes must return either a full HTML page or an HTML fragment — the same route must handle both cases (full request vs. HTMX partial request, distinguished by `HX-Request` header). This is a non-obvious integration seam between Flask and HTMX.
- **Unchanged invariants:** The API versioning prefix `/api/v1/` must not be changed or removed. All test clients and Flask api_client references must use the versioned prefix.

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| `attributes: JSON` queries become slow as entry count grows | GIN index created in migration from day one. Monitor query plans before Phase 2 scale. |
| Flask session JWT expiry causes silent auth failures mid-session | Flask should intercept 401 from FastAPI and redirect to `/login` with a "session expired" message rather than showing a broken page. Implement in `api_client.py` error handling. |
| BehaviorEvent table grows unbounded | Accept this in Phase 1 (data is valuable). Add PostgreSQL table partitioning by month in Phase 2 before production scale. Schema should be partition-ready (no FK dependencies from other tables). |
| Streak computation is O(n) per habit per request | Acceptable for Phase 1 (small data). Add a materialized streak cache in Phase 2 when habit history grows. |
| Docker Compose complexity slows onboarding | Provide a `make dev` target that starts all three services in one command. Document setup in README. |
| HTMX partial/full page route ambiguity | Document the `HX-Request` header pattern in a shared template helper. Include in base template as a comment. |
| Client-generated UUID collisions | Astronomically rare but must be handled — return 409 Conflict on collision. |

## Documentation / Operational Notes

- `docker-compose.yml` should include a healthcheck for all three services
- `.env.example` must document all required environment variables: `DATABASE_URL`, `FASTAPI_BASE_URL`, `JWT_SECRET`, `FLASK_SECRET_KEY`
- The `make migrate` target must run Alembic `upgrade head` against the Docker PostgreSQL instance
- Data export (`/users/me/export`) should be tested with real data before launch — it is a trust-building feature and must work correctly from day one
- README should document the two-service architecture and explain why Flask never touches the database directly

## Sources & References

- **Origin document:** [docs/brainstorms/001-planner-brainstorm.md](docs/brainstorms/001-planner-brainstorm.md)
- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- HTMX: https://htmx.org/reference/
- httpx: https://www.python-httpx.org
