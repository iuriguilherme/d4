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
