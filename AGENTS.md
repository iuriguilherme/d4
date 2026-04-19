# HYPPO — Agent Context

## Project

HYPPO (Hyper Personalized Planner and Organizer) — a planner app that adapts to user behavior over time.

## Architecture

Two-service Python stack:
- `api/` — FastAPI (port 8000): business logic, database owner, JWT auth
- `web/` — Flask (port 5000): web UI, HTMX, calls FastAPI via httpx only
- PostgreSQL (port 5432): all data, run via Docker

Flask **never** queries the database directly. All data access goes through FastAPI.

## Key Files

- `api/app/main.py` — FastAPI app entry point, router registration
- `api/app/core/config.py` — settings (env vars)
- `api/app/core/database.py` — SQLAlchemy async engine, get_db dependency
- `api/app/models/` — SQLAlchemy models (User, Entry, Habit, BehaviorEvent, etc.)
- `api/app/routers/` — FastAPI route handlers
- `api/app/services/` — business logic (streak, behavior events, export)
- `web/app/__init__.py` — Flask app factory
- `web/app/api_client.py` — **only** file in web/ that imports httpx
- `alembic/versions/` — database migrations
- `docs/solutions/` — documented solutions to past problems (bugs, architectural violations, best practices), organized by category with YAML frontmatter (`module`, `tags`, `problem_type`)

## Running

```bash
docker-compose up --build   # start all services
make migrate                # run Alembic migrations
make test                   # run all tests
```

Tests require PostgreSQL at localhost:5432 (user: hyppo, password: hyppo, db: hyppo_test for API tests).

## Conventions

- UUID primary keys everywhere
- Soft-delete: `deleted_at` timestamp, list endpoints filter `WHERE deleted_at IS NULL`
- BehaviorEvent is append-only, no FK constraints, fire-and-forget via BackgroundTasks
- Entry `attributes` is a GIN-indexed JSON column for flexible metadata
- API versioning prefix: `/api/v1/` — never change this
- HTMX partials: Flask routes check `HX-Request` header for fragment vs full page
- `X-Session-ID` header threads Flask session UUID to FastAPI for event grouping

## Current Branch

`feat/hyppo-mvp-foundation` — Phase 1 MVP implementation (all 9 units complete)

## Phase Status

- Phase 1 (this branch): complete — scaffold, auth, entries, habits, journal, behavior events, export
- Phase 2: archetype scoring engine, UI adaptation (not started)
- Phase 3: PARA structure, note linking, full-text search (not started)

---

## Documentation

Do not delete files under docs/

If files are no longer relevant to the current context, archive them under the appropriate archive/ subfolder of each section.

Every change to the codebase should be documented using the appropriate tool.

### Compound Engineering Workflows

This repository uses Compound Engineering to track decisions and scale knowledge:

- `docs/brainstorms/` — captures product-level requirements and scope decisions using `/ce:brainstorm`. Completed brainstorms should be archived in `docs/brainstorms/archive/`.
- `docs/plans/` — technical implementation plans created using `/ce:plan`. Once implemented and verified, plans should be moved to `docs/plans/archive/`.
- `docs/ideation/` — open-ended notes, research, and deferred feature ideas.

### Documented Solutions

`docs/solutions/` — documented solutions, architecture decisions, and best practices organized by category with YAML frontmatter (`module`, `tags`, `problem_type`). Relevant when implementing or debugging in documented areas. Create these using `/ce:compound`.

### Prompt Convention

Prompts go in `docs/prompts/`, not `prompts/`.

## Efficiency & Communication

- **Caveman Mode** — use `caveman` skill whenever applicable to minimize token usage and keep communication terse.

## Versioning & Tagging

- **SemVer** — use `vX.Y.Z` prefix for git tags.
- **Rules**:
  - `feat`: increment minor (`v0.Y.0`).
  - `fix`: increment patch (`v0.0.Z`).
  - `refactor`: increment minor if breaking changes, increment patch otherwise.
  - `docs`, `chore`: do NOT tag.
