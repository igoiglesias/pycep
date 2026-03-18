# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyCEP is a FastAPI wrapper over ViaCEP and BrasilAPI for Brazilian postal code (CEP) lookup. It adds dual-layer caching (in-memory + SQLite), automatic provider fallback, JWT auth, rate limiting, and admin/user dashboards. Built live on YouTube.

**Language convention:** all code, variable names, commits, and comments are in Portuguese.

## Commands

```bash
# Development server
./run.sh dev              # or: fastapi dev app.py

# Production
./run.sh prod             # or: fastapi run app.py
./run.sh superprod        # gunicorn + uvicorn workers

# Seed database (admin@pycep.com/admin, user@pycep.com/user)
./run.sh script seed

# Process background CEP update queue
./run.sh script fila_update

# Load testing
locust -f locustfile.py --host=http://localhost:8000
# Then open http://localhost:8089

# Install dependencies
pip install -r requirements.txt
```

**No unit tests exist** — only load testing via Locust.

## Architecture

### Request flow for CEP lookup (`GET /cep/{cep}`)

```
Request → @rate_limit → @cep_request (log) → @cache (in-memory, 10min)
  → cep_service.consultar()
    → Check SQLite cache
    → If miss: ViaCEP → fallback BrasilAPI
    → Save to DB (BackgroundTask)
    → Queue stale CEPs for refresh (BackgroundTask)
```

### Layering

- **routes/** — thin HTTP handlers (API in `routes/api/`, web pages in `routes/web/`)
- **services/** — business logic, decorators for cross-cutting concerns (auth, logging, rate limiting)
- **databases/repository.py** — all SQL queries (repository pattern over async SQLite)
- **databases/db.py** — low-level async SQLite wrapper (`aiosqlite`)
- **modules/** — external API clients (`viacep.py`, `brasilapi.py`) using `httpx` with HTTP/2
- **tools/** — utilities (JWT, Argon2 password hashing, Pydantic validators, cache key builders)
- **scripts/** — standalone scripts run via `./run.sh script <name>`

### Key patterns

- **Decorator-driven cross-cutting concerns:** auth verification, request logging, rate limiting, and caching are all applied as stacked decorators on route handlers.
- **Dual-layer caching:** `fastapi-cache2` in-memory (10min TTL) + SQLite persistent cache. CEPs older than 30 days get queued in `fila_update` for background refresh.
- **Provider fallback:** ViaCEP is primary; BrasilAPI is automatic fallback on failure.
- **Background tasks:** FastAPI `BackgroundTasks` for non-blocking DB saves and queue insertions.
- **Config:** all settings loaded from `config/.env` via `python-dotenv`, centralized in `config/config.py`.

### Database tables (SQLite)

`cep` (cached lookups), `admin`, `user`, `token` (API tokens, max 5/user), `request_log` (audit trail), `fila_update` (background refresh queue). Schema initialized in `repository.initialize_db()`.

### Auth

JWT (HS256) stored in HttpOnly cookies. Passwords hashed with Argon2. `@auth_service.verify()` decorator protects authenticated routes. Separate cookie names for user vs admin sessions.

### Rate limiting

In-memory sliding window per IP. Anonymous: 5 req/min. With Bearer token: 10 req/min. Configured via `config/.env`.
