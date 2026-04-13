---
title: Flask/FastAPI Service Boundary Violations in HYPPO Phase 1 MVP
date: 2026-04-13
category: integration-issues
module: web/app/settings, api/app/routers/auth, api/app/services/habit_streak
problem_type: integration_issue
component: service_object
symptoms:
  - "web/app/settings/routes.py imported httpx directly despite AGENTS.md rule"
  - "Private helpers _headers() and _base_url() called from outside api_client.py"
  - "JWT refresh endpoint compared UUID column against Python str from token payload"
  - "Habit streak query had no date bound — grew unbounded with user history"
  - "httpx.Client in settings route had no timeout — could hang Flask worker indefinitely"
root_cause: wrong_api
resolution_type: code_fix
severity: high
related_components:
  - authentication
  - tooling
tags:
  - httpx
  - flask-fastapi-boundary
  - api-client
  - jwt
  - uuid
  - query-bounds
  - timeout
  - production-guard
---

# Flask/FastAPI Service Boundary Violations in HYPPO Phase 1 MVP

## Problem

Multiple service boundary violations were introduced during Phase 1 MVP implementation,
found via `ce-review`. The most critical: `web/app/settings/routes.py` imported `httpx`
directly and called private functions from `api_client.py`, bypassing the single
httpx-boundary rule documented in AGENTS.md. Associated with this, related correctness
and safety issues were found in the FastAPI layer (JWT type mismatch, no production guard,
unbounded DB query).

## Symptoms

- `import httpx` present in `web/app/settings/routes.py` (only `api_client.py` is permitted)
- `from web.app.api_client import APIError, _headers, _base_url` — private name access from outside the module
- Forwarding `dict(r.headers)` from upstream FastAPI response (propagates `content-length`, `transfer-encoding`, risks truncation)
- `httpx.Client(base_url=_base_url())` with no `timeout=` — Flask worker hangs if FastAPI is slow
- `select(User).where(User.id == user_id)` where `user_id` is `str` from JWT `payload.get("sub")`
- `habit_streak.py` fetched all checkin entries ever with no date filter

## What Didn't Work

Not applicable — all issues were identified via static code review (`ce-review`), not runtime failures. PostgreSQL's implicit `str→UUID` coercion meant Fix 2 worked in development despite being type-unsafe.

## Solution

### Fix 1 — Move export proxy into api_client, remove httpx import from route

**Before** (`web/app/settings/routes.py`):
```python
import httpx
from web.app.api_client import APIError, _headers, _base_url

@settings_bp.get("/settings/export")
@login_required
def export_data():
    with httpx.Client(base_url=_base_url()) as client:
        r = client.get("/api/v1/users/me/export", headers=_headers())
        r.raise_for_status()
    return Response(
        response=r.content,
        status=r.status_code,
        headers=dict(r.headers),   # propagates upstream headers — risky
        content_type="application/json",
    )
```

**After** (`web/app/api_client.py` addition):
```python
def export_data() -> bytes:
    with httpx.Client(base_url=_base_url(), timeout=30.0) as client:
        r = client.get("/api/v1/users/me/export", headers=_headers())
        r.raise_for_status()
        return r.content
```

**After** (`web/app/settings/routes.py`):
```python
# no httpx import, no private _headers/_base_url access
from web.app.api_client import APIError

@settings_bp.get("/settings/export")
@login_required
def export_data():
    content = api_client.export_data()
    return Response(
        response=content,
        status=200,
        headers={"Content-Disposition": "attachment; filename=hyppo-export.json"},
        content_type="application/json",
    )
```

### Fix 2 — Cast JWT sub to UUID before DB comparison

**Before** (`api/app/routers/auth.py`):
```python
user_id = payload.get("sub")   # str | None
result = await db.execute(select(User).where(User.id == user_id))
```

**After**:
```python
from uuid import UUID

try:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise JWTError("wrong type")
    user_id = UUID(payload.get("sub", ""))
except (JWTError, ValueError):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

result = await db.execute(select(User).where(User.id == user_id))
```

### Fix 3 — Production guard for default JWT secret

Added to `api/app/main.py` at module level (before `app = FastAPI(...)`):
```python
if settings.environment == "production" and settings.jwt_secret == "change-me-in-production":
    raise RuntimeError("JWT secret must be changed before running in production")
```

### Fix 4 — Bound habit streak query to 366 days

**Before** (`api/app/services/habit_streak.py`):
```python
result = await db.execute(
    select(Entry.entry_date)
    .where(Entry.user_id == user_id)
    .where(Entry.type == EntryType.habit_checkin)
    .where(Entry.deleted_at.is_(None))
    .where(Entry.attributes["habit_id"].astext == habit_id)
    .order_by(Entry.entry_date.desc())
)
```

**After**:
```python
_MAX_STREAK_DAYS = 366

async def compute_streak(habit_id: str, user_id, db: AsyncSession) -> int:
    earliest = date.today() - timedelta(days=_MAX_STREAK_DAYS)
    result = await db.execute(
        select(Entry.entry_date)
        .where(Entry.user_id == user_id)
        .where(Entry.type == EntryType.habit_checkin)
        .where(Entry.deleted_at.is_(None))
        .where(Entry.attributes["habit_id"].astext == habit_id)
        .where(Entry.entry_date >= earliest)
        .order_by(Entry.entry_date.desc())
    )
```

## Why This Works

**Fix 1**: `api_client.py` is the single httpx abstraction boundary. All HTTP concerns
(base URL, auth headers, timeouts, error handling) belong there. Route handlers become
thin: call the function, return the response. Forwarding upstream headers is unsafe —
`content-length` from FastAPI may not match the bytes Flask actually sends, causing
truncation. Allowlisting only `Content-Disposition` is the safe pattern.

**Fix 2**: `UUID(str)` raises `ValueError` for any non-UUID string, including empty string
when `sub` is absent. Catching `(JWTError, ValueError)` collapses all bad-token paths to
401. PostgreSQL's implicit `str→UUID` coercion works _today_ but is driver-version-dependent
and undocumented behavior; passing a typed `UUID` object is correct.

**Fix 3**: `RuntimeError` at module load time prevents Uvicorn from accepting connections at
all. A missing or misconfigured `JWT_SECRET` surfaces immediately in deployment logs rather
than silently compromising all user auth. The check is in `main.py` (not `config.py`) so it
only fires in the running app, not in test environments that import settings directly.

**Fix 4**: A habit streak cannot exceed 366 consecutive days without a gap, so entries older
than 366 days cannot contribute to the current streak. The date bound converts an unbounded
table scan into a time-windowed range query that stays O(1) in terms of rows loaded as
user history grows.

## Prevention

**Architectural boundary (httpx)**:
- Add `ruff` rule or pre-commit grep: flag any `import httpx` outside `web/app/api_client.py`
- Test pattern: walk `web/app/` with `ast.parse` and assert no module except `api_client.py` imports httpx
- Code review checklist in AGENTS.md: "Does any new Flask route import httpx directly?"

**All new api_client functions** must include `timeout=30.0` — consider a module-level constant:
```python
_DEFAULT_TIMEOUT = 30.0
```

**JWT token parsing**:
- Always cast `payload.get("sub")` to `UUID(...)` before use in DB queries
- Catch `(JWTError, ValueError)` together — missing `sub` and malformed UUID both map to 401
- Test: `POST /api/v1/auth/refresh` with `sub="not-a-uuid"` must return 401, not 500

**Production config guard**:
- Test: set `ENVIRONMENT=production`, leave `JWT_SECRET` unset, assert process exits non-zero
- Document `JWT_SECRET` as required (not optional) in deployment runbook and `.env.example`

**Query bounds**:
- Any query that walks back through time-series data must have a date lower bound
- Streak phase-2 plan: materialize streak as a cached column, eliminate the walk entirely (session history: this is documented as Phase 2 scope in the plan)
- Note: `compute_streak` still uses server `date.today()` — Phase 2 should pass user timezone so streaks are computed in the user's local date

**Deferred from this review**:
- Refresh token revocation on logout (P1, gated_auto) — requires JTI denylist or token store, deferred to Phase 2
- N+1 habit streak queries in list endpoint — batch fetch all habit checkin dates in one query, deferred to Phase 2

## Related Issues

- `docs/plans/2026-04-07-001-feat-hyppo-mvp-foundation-plan.md` — line 332, 340, 353: httpx boundary rule was stated but not enforced; line 607: O(n) streak acknowledged as Phase 1 compromise
- Phase 2 deferred: streak materialized cache, refresh token revocation, N+1 batch fix
