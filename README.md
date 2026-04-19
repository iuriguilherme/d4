# HYPPO

[![Conventional Code](https://img.shields.io/badge/code-conventional%20🏭-red?style=for-the-badge)](https://github.com/zwbao/certified-organic-code)

Hyper Personalized Planner and Organizer — a planner app that adapts to user behavior over time.

## Status

Phase 1 MVP complete on branch `feat/hyppo-mvp-foundation`:
- FastAPI backend + Flask web UI + PostgreSQL, all running via Docker
- JWT auth, entry CRUD, habits with streaks, daily journal, behavior event tracking, data export

## Architecture

Two-service Python stack:

| Service | Port | Role |
|---------|------|------|
| `api/` (FastAPI) | 8000 | Business logic, database, JWT auth |
| `web/` (Flask) | 5000 | Web UI, HTMX, calls FastAPI only |
| PostgreSQL 16 | 5432 | All data (via Docker) |

Flask never queries the database directly — all data access goes through FastAPI.

## Running

```bash
cp .env.example .env        # set JWT_SECRET, POSTGRES_PASSWORD, FLASK_SECRET_KEY
docker-compose up --build   # start all services
make migrate                # run Alembic migrations
make test                   # run all tests (requires PostgreSQL at localhost:5432)
```

## Features (Phase 1)

- **Auth** — JWT access tokens (15 min) + refresh tokens (30 days, HttpOnly cookie)
- **Daily Log** — universal capture, task completion, HTMX partial updates
- **Journal** — per-day journal entry with auto-save
- **Habits** — up to 5 active habits, idempotent check-in, streak computation
- **Behavior Events** — append-only event log, fire-and-forget via BackgroundTasks
- **Export** — full data export at `GET /api/v1/users/me/export`
- **Settings** — timezone, theme preferences

## Roadmap

- **Phase 2** — Archetype scoring engine, UI adaptation, streak materialization
- **Phase 3** — PARA structure, note linking, full-text search

## License

AGPLv3 - see [LICENSE](./LICENSE)

    Copyright (C) 2026  Iuri Guilherme

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
