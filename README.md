# FlameGuard AI Backend

FastAPI backend for exploring microgravity combustion research with traceable evidence.
Phase 1 provides application, configuration, database, migration, and test infrastructure.
It contains no scientific records, domain tables, matching algorithm, RAG, or predictive model.
This is a research demonstration, not a source of operational spacecraft fire safety advice.

The existing [design diagrams](docs/index.html) are preserved. See the
[architecture audit and API proposal](docs/backend-implementation-plan.md) for the 21-table
inventory, frontend mappings, unresolved design decisions, and implementation phases.

## Stack and requirements

- Python 3.12 recommended; the project permits 3.12 and 3.13.
- Poetry 2.x manages dependencies, the lockfile, and the in-project `.venv/`.
- FastAPI and Uvicorn provide HTTP routing, validation, OpenAPI, and the development server.
- Pydantic v2 and pydantic-settings validate environment configuration.
- PostgreSQL 17 runs as the only Docker Compose service.
- SQLAlchemy 2.0 async sessions and asyncpg provide database access; Alembic manages migrations.
- pytest, pytest-asyncio, and HTTPX test the API; Ruff handles linting and formatting.
- Docker Desktop with its Linux engine running, Docker Compose, and VS Code are recommended
  for the Windows development workflow. PostgreSQL is optional for unit tests and liveness.

Poetry uses **non-package mode** (`package-mode = false`): this application runs from the
repository, rather than being built and published as a Python distribution. Runtime dependencies
are in `[project]`; test/lint dependencies are in the Poetry `dev` group (installed by default).
`poetry.toml` sets `virtualenvs.in-project = true`. Commit `poetry.lock`; never commit `.venv/`.
Do not install project dependencies with pip or manually create a virtual environment.

## Local setup (PowerShell)

From the existing backend directory:

```powershell
Set-Location 'C:\Source Code\NASA\flameguard-ai-backend'
py -3.12 --version
poetry --version
Copy-Item .env.example .env
# Edit .env with your local values before starting services.
poetry env use 3.12
poetry install
poetry check
docker compose up -d postgres
docker compose ps
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Copy `.env.example` only when `.env` does not already exist. If Poetry is not available, install
it using the [official isolated installer](https://python-poetry.org/docs/#installation) before
running the commands above. No global project dependencies are required.

For this implementation session, Poetry was installed locally under ignored `.tools/poetry/`.
To use that installation in the current PowerShell session:

```powershell
$env:Path = "$(Join-Path (Get-Location) '.tools\poetry\bin');$env:Path"
poetry --version
```

This local tool directory is not committed or required by other developers.

## Environment variables

Settings read `.env` in the current working directory; actual environment variables take
precedence. Run commands from the backend root. Unrecognized `.env` entries are ignored so the
same file can hold Compose settings. Configuration is validated before the application starts.

| Variable | Purpose / example |
| --- | --- |
| `APP_NAME` | OpenAPI title; `FlameGuard AI Backend` |
| `APP_ENV` | `development`, `test`, `staging`, or `production` |
| `DEBUG` | Boolean, default `false`; rejected when true in production |
| `API_V1_PREFIX` | `/api/v1`; starts with `/`, no trailing slash |
| `DATABASE_URL` | PostgreSQL URL using `postgresql+asyncpg://`; stored as a secret setting |
| `CORS_ORIGINS` | JSON array of explicit HTTP(S) origins; no wildcards or URL paths |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `DB_CONNECT_TIMEOUT_SECONDS` | Connection timeout; default 3 seconds |
| `DB_READY_TIMEOUT_SECONDS` | Readiness query deadline; default 3 seconds |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Local Compose credentials/database |
| `POSTGRES_PORT` | Host port, default `5432`; bound only on `127.0.0.1` |

The checked-in values are local examples. Keep `DATABASE_URL` synchronized with Compose
credentials and host port, and percent-encode special characters in URL credentials. Changing
`POSTGRES_*` does not reinitialize a previously created PostgreSQL volume. The example defaults
also allow health/docs to start without a `.env` file. Replace local defaults for deployment.
If the host already defines an unrelated `DEBUG` value, explicitly set `$env:DEBUG = 'false'`.

The default CORS allowlist includes `http://localhost:3000` and
`https://flame-in-freewall-tourbillion.vercel.app`. Browser credentials are disabled; the
allowlist permits GET, POST, OPTIONS and Content-Type/Authorization headers. CORS is a browser
access policy, not authentication. The backend has no authentication system in this phase.

## Endpoints

| URL | Behavior |
| --- | --- |
| http://localhost:8000/api/v1/health | Always 200 while HTTP is serving; no database dependency |
| http://localhost:8000/api/v1/ready | Executes `SELECT 1`; 200 if available, 503 if unavailable/timed out |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | OpenAPI schema |

Health returns `{"status":"ok","service":"flameguard-ai-backend"}`.
Readiness returns `{"status":"ready","service":"flameguard-ai-backend","database":"ok"}`
or HTTP 503 with `status` and `database` set to `unavailable`. Failure responses do not include
connection strings or database errors. Startup creates an engine without requiring a live
database; shutdown disposes its pool. No schema creation occurs on application startup.

In another PowerShell terminal:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/ready
Start-Process http://localhost:8000/docs
```

## Database and migrations

Only PostgreSQL runs in Docker, with a named persistent volume, health check, one CPU and a
256 MB memory limit. Run FastAPI through Poetry on the host to keep local RAM usage modest.

```powershell
docker compose up -d postgres
docker compose logs --tail 50 postgres
poetry run alembic heads
poetry run alembic upgrade head
```

There are **no revisions or domain tables in Phase 1**. `upgrade head` requires a reachable
database even with no revisions. It may initialize Alembic's own version bookkeeping;
it does not implement the ERD. Offline wiring can be checked without PostgreSQL:

```powershell
poetry run alembic upgrade head --sql
```

In Phase 2, resolve the audit's open schema details, implement approved models under
`app/models/`, and import them in `app/models/__init__.py` so Alembic sees their metadata.
Then generate and review a migration before applying it:

```powershell
poetry run alembic revision --autogenerate -m "implement approved ERD"
poetry run alembic upgrade head
```

Database sessions are request scoped through `get_db_session`. Session context exit closes
resources and rolls back uncommitted transactions; future services explicitly commit writes.
Keep business logic in services and database queries in repositories when those modules are
needed. No unused service/repository/ingestion/integration packages were created in Phase 1.
The async design follows [SQLAlchemy's async session guidance](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html);
resource cleanup uses [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/).

Stop the local database without deleting its data:

```powershell
docker compose stop postgres
```

## Testing and code quality

```powershell
poetry check
poetry install
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
```

Unit tests isolate local settings, use HTTPX with application lifespan, and replace database
sessions for readiness success, failure, and timeout checks. They cover CORS, error redaction,
session cleanup, settings, OpenAPI, and engine shutdown without Docker. One read-only PostgreSQL
integration test is opt-in:

```powershell
$env:RUN_DB_INTEGRATION = '1'
poetry run pytest -m integration
Remove-Item Env:\RUN_DB_INTEGRATION
```

Start PostgreSQL and configure `.env` before opting in. See
[verification results](docs/phase-1-verification.md) for checks actually executed in this session.

## Frontend integration (future phases)

The sibling Next.js frontend remains unchanged and still uses static TypeScript fixtures and
local algorithms. Only health and readiness APIs are implemented here. Future frontend changes
will use an environment setting such as:

```text
NEXT_PUBLIC_API_BASE_URL=https://your-backend-host.example/api/v1
```

The separately deployed backend needs HTTPS and an explicit CORS allowlist for the frontend's
origin. Public frontend variables must never contain database credentials or provider keys.
Use the API proposal in the audit before integrating business features. Keep public slugs,
database UUIDs, and NASA PSI identifiers distinct. Unknown scientific values must remain
unknown; do not fabricate values to satisfy existing required TypeScript fields.

## Current structure

```text
flameguard-ai-backend/
  app/
    main.py
    api/v1/router.py
    api/v1/endpoints/health.py
    core/config.py
    core/database.py
    models/base.py
    schemas/health.py
  alembic/
    env.py
    script.py.mako
    versions/.gitkeep
  tests/
    conftest.py
    test_app.py
    test_config.py
    test_cors.py
    test_database.py
    test_health.py
  docs/
    index.html                      # existing, unchanged
    backend-implementation-plan.md
    phase-1-verification.md
  .env.example
  .gitignore
  alembic.ini
  compose.yaml
  poetry.toml
  pyproject.toml
  poetry.lock
  README.md
```

Python package directories also contain `__init__.py`. The local `.venv/` and `.tools/` are
ignored. No frontend mocks have been imported or seeded. Next: resolve the audit's schema
ambiguities and implement the approved ERD and migrations in Phase 2.
