# FlameGuard AI Backend

Backend for a research platform that explores NASA microgravity combustion experiments,
compares evidence, identifies scenario knowledge gaps and supports source-grounded scientific
explanations. FlameGuard AI is a research and demonstration platform; its outputs must not
be presented as operational spacecraft fire-safety certification or unvalidated safety advice.

This README is a stable project guide for all development phases. Change it only when the
user explicitly requests or approves changes to requirements, architecture, configuration
contracts or the development workflow. Feature completion, migration revisions, test totals
and temporary environment issues belong in separate phase records under [docs/](docs/).

## Project references

- [Architecture and implementation plan](docs/backend-implementation-plan.md): scope,
  responsibility boundaries, approved logical entities, API mappings and delivery roadmap.
- [Original architecture and ERD diagrams](docs/index.html): approved design reference.
- [Implementation records](docs/): phase-specific decisions, delivered changes and executed checks.
- [Dependency configuration](pyproject.toml) and [lockfile](poetry.lock): supported runtimes
  and reproducible dependency versions.

Feature/API availability is documented by the running application's OpenAPI and delivery
records. This README does not track which roadmap phase is complete.

## Architecture and stack

Use a modular monolith with a separately deployed frontend and backend. API routes validate
HTTP contracts; services own business workflows and transaction boundaries; repositories
handle async queries; models and migrations define persistence; integrations and ingestion
handle external systems, source parsing and provenance.

| Technology | Responsibility |
| --- | --- |
| Python | Backend runtime; use a version supported by pyproject.toml |
| FastAPI / Uvicorn | HTTP application, development server and OpenAPI |
| Poetry | Dependency groups, reproducible lockfile and project virtual environment |
| PostgreSQL | Relational storage with source traceability and referential integrity |
| SQLAlchemy 2.x async / asyncpg | ORM, async database engine and sessions |
| Alembic | Versioned schema migrations |
| Pydantic v2 / pydantic-settings | Typed contracts and environment validation |
| pytest / pytest-asyncio / HTTPX | Unit, async, API and integration verification |
| Ruff | Linting and formatting |

Poetry uses non-package mode because the backend runs as an application from this repository.
It creates an in-project `.venv/`; development tools use the `dev` dependency group. Commit
`poetry.lock`, keep `.venv/` out of Git, and manage project dependencies through Poetry.

## Prerequisites

- Python 3.12 recommended, subject to the supported range in `pyproject.toml`.
- Poetry 2.x available on PATH; use the [official installation guide](https://python-poetry.org/docs/#installation).
- A reachable PostgreSQL server, installed directly or run through Docker Compose.
- Docker Desktop with its Linux engine running when choosing the Docker database option.
- Git and a terminal; VS Code is suitable for the Windows development workflow.

Run FastAPI directly through Poetry. Docker Compose is used for PostgreSQL, avoiding an
unnecessary application container for local development.

## Initial setup (Windows PowerShell)

From the workspace root:

```powershell
Set-Location .\flameguard-ai-backend
py -3.12 --version
poetry --version
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Edit .env to select your database and local credentials.
poetry env use 3.12
poetry install
poetry check
```

Run subsequent commands from the backend repository root. The local `.env` contains private
configuration and is ignored by Git. `.env.example` contains non-sensitive examples only.

## Database selection

**DATABASE_URL selects the database used by both FastAPI and Alembic.** These processes run
independently; Alembic does not require Uvicorn to be running. The database server must be
available before migrations or database-dependent requests can succeed.

| Configuration | Consumer |
| --- | --- |
| `DATABASE_URL` | FastAPI and Alembic connection target, user, password and database |
| `POSTGRES_PORT` | Docker Compose host-side PostgreSQL port |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Docker database initialization settings |

For Docker:

```powershell
docker compose up -d --wait postgres
docker compose ps
```

Set DATABASE_URL to match the Docker host port and database credentials. If native PostgreSQL
uses 5432, Docker can use `POSTGRES_PORT=5433`, with `127.0.0.1:5433` in DATABASE_URL.
PostgreSQL inside the container can still use its normal internal port 5432.

For native PostgreSQL, select its actual host/port, user, password and database in DATABASE_URL
and skip Docker startup. With native PostgreSQL on 5432 and Docker mapped to 5433, changing
the URL port switches servers only if the other credentials/database settings also match.
The two servers hold independent users, databases and data.

Percent-encode special characters in URL credentials. Changing POSTGRES_* does not change
credentials or recreate data inside an existing persistent Docker volume. Do not delete
volumes or reset database state to solve a connection or port configuration problem.

Stop Docker PostgreSQL while retaining its volume:

```powershell
docker compose stop postgres
```

## Application configuration

Settings read `.env` from the working directory. Process environment variables take precedence.
Restart the backend after changing `.env` so cached settings and engine configuration are
recreated. Use actual private values locally; do not expose secrets in public frontend variables.

| Variable | Purpose |
| --- | --- |
| `APP_NAME` | Application/OpenAPI title |
| `APP_ENV` | development, test, staging or production |
| `DEBUG` | Development debug switch; production debug must be disabled |
| `API_V1_PREFIX` | Versioned API prefix; default /api/v1 |
| `DATABASE_URL` | PostgreSQL connection URL using postgresql+asyncpg:// |
| `CORS_ORIGINS` | JSON array of explicit allowed frontend origins |
| `LOG_LEVEL` | Application logging level |
| `DB_CONNECT_TIMEOUT_SECONDS` | Database connection timeout |
| `DB_READY_TIMEOUT_SECONDS` | Database readiness deadline |

Use `.env.example` and the settings definitions for configuration details. Configure CORS for
explicit frontend origins, including localhost:3000 for local integration and the appropriate
HTTPS frontend deployment. CORS does not replace authentication or authorization.

## Migrations and application startup

Review and apply the repository's existing migration chain to the selected DATABASE_URL:

```powershell
poetry run alembic history
poetry run alembic upgrade head
poetry run alembic current
poetry run alembic check
poetry run uvicorn app.main:app --reload
```

Inspect upgrade SQL without connecting to PostgreSQL:

```powershell
poetry run alembic upgrade head --sql
```

Models must be registered with Alembic metadata. Review generated migration code before
applying it; do not replace migrations with application-startup table creation, delete
existing revisions or blindly stamp a database to suppress an unexplained conflict.

Repositories do not own implicit commits. Services/callers explicitly control transactions,
and request-scoped sessions release resources and roll back uncommitted work on exit.

## API discovery and operational checks

| URL | Purpose |
| --- | --- |
| http://localhost:8000/docs | Swagger UI and available API operations |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | Machine-readable API schema |
| http://localhost:8000/api/v1/health | Liveness, independent of database availability |
| http://localhost:8000/api/v1/ready | Readiness of the configured database |

The health paths follow API_V1_PREFIX if it is customized. Liveness must remain available
during database outages; readiness failures must be bounded and sanitized. Business endpoint
contracts and delivery scope are described in the architecture plan and phase records.

## Testing and code quality

```powershell
poetry check
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
```

Checks that do not require PostgreSQL must run independently of Docker. Database integration
tests use a separate PostgreSQL testing target, never the development database. Configure
TEST_DATABASE_URL as a process environment variable when running those tests:

```powershell
# Replace the example password with the testing role's actual password, URL-encoded as needed.
$env:TEST_DATABASE_URL = 'postgresql+asyncpg://flameguard:YOUR_TEST_PASSWORD@127.0.0.1:5433/flameguard_test_suite'
poetry run pytest -m integration
Remove-Item Env:\TEST_DATABASE_URL
```

The testing role needs CREATEDB for fresh isolated databases. Use a test-name prefix distinct
from the development database. Fixture transactions must roll back synthetic records, even
if application code commits. Never truncate, overwrite or reset development data during tests.
Consult the test fixtures and phase verification records for detailed test setup and results.

## Frontend integration and scientific integrity

The Next.js frontend connects to a separately deployed HTTPS backend. Its public configuration
can use a value such as NEXT_PUBLIC_API_BASE_URL=https://your-backend-host.example/api/v1;
provider keys and database credentials remain private on the backend.

Keep public slugs, database UUIDs and NASA identifiers distinct. Preserve source documents,
locators/excerpts, original units, unknown values, uncertainty and validation context across
API mappings. Do not seed frontend demo data as verified NASA research. Retrieval, matching
and prediction features must follow the evidence and validation requirements in the plan.

## Repository organization and documentation policy

The following describes responsibility boundaries rather than an exhaustive file inventory.
Directories are added when real functionality requires them:

```text
app/
  main.py          Application entry point and resource lifecycle
  api/             HTTP routes and versioned routers
  core/            Settings and database infrastructure
  models/          Approved persistence entities
  schemas/         Typed input/output contracts
  repositories/    Async persistence queries
  services/        Business workflows and transaction coordination
  integrations/    External source/provider adapters
  ingestion/       Scientific parsing, provenance and curation
alembic/           Versioned schema changes
tests/             Unit, API, migration and database verification
docs/              Architecture references and phase-specific records
```

Keep README and backend-implementation-plan as shared project baselines. Do not append phase
completion notes, machine-specific setup history, temporary blockers, test counts or migration
revision lists to them. Record each delivery separately in `docs/phase-*.md`; update these two
baseline documents only for an explicit user-requested or user-approved requirements change.
