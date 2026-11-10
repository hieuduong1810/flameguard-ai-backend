# Local development runbook — Windows, FastAPI, Poetry, PostgreSQL

Run commands from the existing `flameguard-ai-backend` folder. This repository
is **not** a monorepo package and must not modify its sibling frontend.

## Prerequisites

- Python 3.12 (compatible versions are defined in `pyproject.toml`).
- Poetry 2.x on PATH; this app uses Poetry **non-package mode**.
- A PostgreSQL instance, native Windows or Docker Compose.
- Docker Desktop only if you choose the Docker PostgreSQL option.
- A local `.env` with private settings matching your selected database;
  `.env` is ignored by Git. `README.md` lists supported variables.

```powershell
py -3.12 --version
poetry --version
poetry install
poetry check
```

The user may have Poetry under a local ignored `.tools/` directory; follow
the existing machine setup rather than installing a second global copy.
**Do not switch this backend to uv** because Spec Kit's separate CLI recommends uv.

## Choose exactly one development database

1. Native PostgreSQL: check its configured host/port/user/database and set
   `DATABASE_URL` accordingly.
2. Docker PostgreSQL: `docker compose up -d --wait postgres` and ensure its
   `POSTGRES_PORT` mapping matches the URL. Do not confuse native 5432 with
   Docker-mapped 5433 if both exist.

The two servers are independent. Never use Docker volume removal to solve a
connection problem. Do not print or commit the full `DATABASE_URL`.

Before proposing migration changes, inspect current state:

```powershell
poetry run alembic history
poetry run alembic current
poetry run alembic check
```

These commands do not replace a reviewed, specifically approved migration
deployment. Only upgrade after confirming the target DB and user authorization:

```powershell
# After separately confirming the intended nonproduction target:
poetry run alembic upgrade head
```

## Start and inspect the API

```powershell
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The endpoints available in the submitted Phase 2 code are:

- `http://127.0.0.1:8000/api/v1/health`
- `http://127.0.0.1:8000/api/v1/ready`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Do not assume roadmap business routes exist. Source of truth for current routes
is the running OpenAPI and code, not the proposed endpoint table in the plan.

## Local frontend collaboration

The Next.js frontend is a **separate** repository and team. Its deployed URL
is `https://flame-in-freewall-tourbillion.vercel.app/dashboard`, but the
submitted source currently uses client-side static dataset and demo engines.
Its team must explicitly implement an API adapter and set a public base URL,
e.g. `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1` for local
development. CORS must include the actual development/deployment origin.

Do not expose backend secrets as `NEXT_PUBLIC_*`, and do not modify the
frontend repo without explicit authorization.

## Common troubleshooting rules

| Symptom | Inspect first | Do not do |
| --- | --- | --- |
| Database unavailable | Selected URL host/port, native vs Docker server, role/database, readiness error | Drop database, delete volume, stamp migration |
| New models not visible | Registered metadata, migrations, current head, test schema | `Base.metadata.create_all()` at app startup |
| CORS error | Exact frontend origin, API host/port, browser network request | Set production wildcard CORS |
| Frontend shows old mock data | Frontend imports/API adapter and deployed environment variables | Invent DB rows to match UI |
| Chat lost after refresh | Current Zustand-only memory state, absent API/session adapter | Add user/login tables without approved design |

Record real troubleshooting outcomes in a task/phase record, not as temporary
machine-specific advice appended to the stable architecture plan.
