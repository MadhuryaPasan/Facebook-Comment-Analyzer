# Facebook Comment Analyzer — Backend

Modular FastAPI backend for fetching Facebook Page posts and comments via the Meta Graph API and running NLP sentiment, intent, language, and aspect analysis.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [How This Architecture Reduces Merge Conflicts](#how-this-architecture-reduces-merge-conflicts)
4. [Developer Instructions (Step-by-Step)](#developer-instructions-step-by-step)
   - [1. Working on the Graph API Client (`libs/facebook_graph.py`)](#1-working-on-the-graph-api-client-libsfacebook_graphpy)
   - [2. Adding Database Models & Migrations](#2-adding-database-models--migrations)
   - [3. Implementing Repositories & Services](#3-implementing-repositories--services)
   - [4. Adding or Documenting API Routes](#4-adding-or-documenting-api-routes)
   - [5. Working on the Ingestion & NLP Pipeline (`app/pipeline/`)](#5-working-on-the-ingestion--nlp-pipeline-apppipeline)
   - [6. Raising Consistent API Errors](#6-raising-consistent-api-errors)
   - [7. Adding a New Feature Module](#7-adding-a-new-feature-module)
5. [Testing & Code Quality](#testing--code-quality)
6. [Recommended Git Team Workflow](#recommended-git-team-workflow)

---

## Quick Start

### Prerequisites

- Python **3.13+**
- [`uv`](https://docs.astral.sh/uv/) package manager
- PostgreSQL (for persistence) and Redis (for background analysis jobs)

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Environment variables used by `app/core/config.py`:

| Variable | Purpose | Default |
| --- | --- | --- |
| `BACKEND_HOST` | Host interface for Uvicorn | `localhost` |
| `BACKEND_PORT` | Port for Uvicorn | `8000` |
| `BACKEND_DEBUG` | Enables Uvicorn auto-reload and SQL echo | `true` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5500,http://127.0.0.1:5500` |
| `FB_PAGE_ID` | Target Facebook Page ID | `""` |
| `FB_PAGE_ACCESS_TOKEN` | Meta Page Access Token | `""` |
| `FB_GRAPH_API_VERSION` | Graph API version | `v21.0` |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | PostgreSQL connection settings | `postgres`, `""`, `localhost`, `5432`, `comment_analyzer` |
| `DATABASE_URL` | Optional full SQLAlchemy connection URI override | Built from `DB_*` |
| `ANALYZER_MODEL_VERSION` | Model tag stored with analysis outputs | `analyzer-0.1.0` |
| `REDIS_URL` | Redis broker URL for task queue | `redis://localhost:6379/0` |

### 3. Run the Development Server

Recommended (FastAPI CLI with auto-reload on `127.0.0.1:8000`):

```bash
uv run fastapi dev
```

*(Alternatively, `uv run fastapi dev app/main.py` works too. For production without reload, use `uv run fastapi run`.)*

If you want the server to automatically use `BACKEND_HOST`, `BACKEND_PORT`, and `BACKEND_DEBUG` from `.env`:

```bash
uv run python main.py
```

Once running:
- **Swagger UI (Interactive Docs):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **Health Check:** `GET http://localhost:8000/health`

---

## Architecture Overview

```text
backend/
├── main.py                         # Thin ASGI entrypoint (`uvicorn main:app` / `python main.py`)
├── pyproject.toml                  # Dependencies, pytest pythonpath, and ruff settings
├── .env.example                    # Environment variable template
│
├── libs/                           # Standalone single-file libraries (ZERO `app.*` imports)
│   └── facebook_graph.py           # Self-contained Facebook Graph API client
│
├── app/
│   ├── main.py                     # FastAPI factory (`create_app`), lifespan, CORS, exception handlers
│   │
│   ├── core/                       # App-wide infrastructure (rarely changed once configured)
│   │   ├── config.py               # `Config` environment settings & validation helpers
│   │   ├── database.py             # Cached SQLModel `get_engine()` & `get_session()`
│   │   ├── dependencies.py         # Shared FastAPI dependencies (`DBSession`)
│   │   ├── exceptions.py           # Base HTTP exceptions (`AppException`, `NotFoundException`, ...)
│   │   ├── exception_handlers.py   # Global JSON error envelope handler
│   │   └── logging.py              # Console + file logging setup
│   │
│   ├── shared/                     # Primitives shared across modules
│   │   ├── enums.py                # `Sentiment`, `Intent`, `Language`, `TaskStatus`
│   │   ├── types.py                # Annotated types (`FBPostId`, `FBCommentId`, `Score`)
│   │   └── schemas.py              # `DateRangeParams`, `AspectSentimentDTO`, `ErrorResponseDTO`
│   │
│   ├── api/                        # API versioning & OpenAPI documentation metadata
│   │   ├── tags.py                 # `OPENAPI_TAGS` descriptions for Swagger/ReDoc
│   │   └── v1/
│   │       └── router.py           # Aggregates module routers under `/api/v1`
│   │
│   ├── modules/                    # Vertical, feature-isolated domain slices
│   │   ├── posts/                  # `router.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, `exceptions.py`
│   │   ├── comments/               # `router.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, `exceptions.py`
│   │   └── analysis/               # `router.py`, `service.py`, `schemas.py`, `exceptions.py`
│   │
│   └── pipeline/                   # Decoupled ingestion & NLP stages
│       ├── contracts.py            # `RawComment` and `AnalysisResult` data contracts
│       ├── fetcher.py              # `FacebookCommentFetcher` (adapts `libs.facebook_graph` -> `RawComment`)
│       └── analyzer.py             # `CommentAnalyzer` (`RawComment` -> `AnalysisResult`)
│
└── tests/                          # Automated tests mirroring `libs/` and `app/`
    ├── test_app.py                 # Health check & OpenAPI documentation checks
    └── test_facebook_graph.py      # Standalone Graph API client & fetcher tests
```

### Dependency Direction Rules

Keep dependencies flowing cleanly in one direction so modules stay decoupled:

```text
libs/facebook_graph.py   <-- (no imports from app.*)
        ^
        |
app/pipeline/fetcher.py  --> app/pipeline/contracts.py <-- app/pipeline/analyzer.py
                                      ^
app/modules/<domain>/router.py --> service.py --> repository.py --> models.py
        |                              |
        v                              v
   schemas.py / exceptions.py     app/core/* & app/shared/*
```

- **`libs/`** MUST NOT import anything from `app.*`.
- **`app/pipeline/analyzer.py`** MUST NOT import from `libs/` or `app/modules/*/router.py` — it only depends on `app/pipeline/contracts.py`, `app/shared/`, and `app/core/config.py`.
- **`app/modules/<domain>/`** owns its own slice. Avoid importing internals across sibling modules unless strictly necessary; share common types via `app/shared/`.

---

## How This Architecture Reduces Merge Conflicts

1. **Vertical module isolation (`app/modules/posts`, `comments`, `analysis`)**:
   - Posts, Comments, and Analysis each have their own `router.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, and `exceptions.py`.
   - Two developers working on Posts and Comments simultaneously do not touch the same files.
2. **Single-file Graph API library (`libs/facebook_graph.py`)**:
   - All Graph API HTTP logic, pagination, and Meta error mapping live in one self-contained file.
   - Because `app/pipeline/fetcher.py` acts as the adapter, changes inside `libs/facebook_graph.py` do not ripple through routers, schemas, or services.
   - Later, `libs/facebook_graph.py` can be copied or published as its own Python package with zero refactoring of its internals.
3. **Explicit pipeline contracts (`app/pipeline/contracts.py`)**:
   - The person building the fetcher and the person building the NLP analyzer only need to agree on `RawComment` and `AnalysisResult`.

---

## Developer Instructions (Step-by-Step)

### 1. Working on the Graph API Client (`libs/facebook_graph.py`)

When adding or replacing the Graph API class created by your supervisor:

1. Put all Graph API client code inside **`libs/facebook_graph.py`** (single file).
2. **Do NOT import** `app.core.*`, `app.modules.*`, `fastapi`, or `sqlmodel` inside `libs/facebook_graph.py`. Only use Python stdlib and `httpx` (pass tokens/versions into `__init__`, never read `Config` inside `libs/`).
3. Map Graph API failures to the library's own exceptions (`FacebookGraphError`, `FacebookGraphAuthError`, `FacebookGraphRateLimitError`, `FacebookGraphNotFoundError`).
4. Update `app/pipeline/fetcher.py` (`FacebookCommentFetcher`) if method signatures on `FacebookGraphClient` change.
5. Verify library isolation and mocked pagination with:
   ```bash
   uv run pytest tests/test_facebook_graph.py
   ```
   (`test_facebook_graph_is_standalone_single_file_library` automatically fails if anyone accidentally imports `app.*` inside `libs/facebook_graph.py`.)

---

### 2. Adding Database Models & Migrations

1. Define SQLModel table classes inside each domain's own `models.py`:
   - `Post` table -> `app/modules/posts/models.py`
   - `Comment` and `CommentAnalysis` tables -> `app/modules/comments/models.py`
2. Import those models in Alembic's `env.py` metadata setup when configuring migrations so Alembic detects all tables.
3. Never put database queries directly inside `router.py`; keep them in `repository.py`.

---

### 3. Implementing Repositories & Services

Follow the 3-layer separation inside each module (`app/modules/<domain>/`):

1. **`repository.py`** (DB access only):
   - Receives `db: Session` and primitive filter values.
   - Executes SQLModel `select(...)` queries and returns ORM entities or records.
2. **`service.py`** (business logic):
   - Receives Pydantic request/filter DTOs and `db: Session`.
   - Calls repository methods, raises domain exceptions (e.g., `PostNotFoundException(post_id)`), and returns response DTOs (`PostResponseDTO`, `CommentListResponseDTO`, etc.).
3. **`router.py`** (HTTP layer only):
   - Parses path/query/body parameters via FastAPI + Pydantic, injects `db: DBSession`, and delegates directly to the service.

---

### 4. Adding or Documenting API Routes

Every endpoint in `app/modules/<domain>/router.py` should include full OpenAPI metadata so `/docs` stays clear for frontend and QA teammates:

```python
@router.get(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    response_model=PostResponseDTO,
    summary="Short 3-6 word action title",
    description="Clear explanation of behavior, filters, and side effects.",
    response_description="What the 2xx response payload contains.",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponseDTO,
            "description": "Post with the given ID was not found (`POST_NOT_FOUND`).",
        },
    },
)
def get_post(
    post_id: Annotated[str, Path(description="Meta Facebook post ID")],
    db: DBSession,
) -> PostResponseDTO:
    return PostService.get_post(post_id, db)
```

Also document every Pydantic field in `schemas.py` using `Annotated[..., Field(description="...")]`. Note that `tests/test_app.py` asserts every route in OpenAPI has both a `summary` and a `description`.

---

### 5. Working on the Ingestion & NLP Pipeline (`app/pipeline/`)

- **Ingestion (`app/pipeline/fetcher.py`)**:
  - Uses `FacebookGraphClient` (injected in `__init__`) to pull paginated comments from Meta Graph API.
  - Hashes raw Facebook user IDs (`author_hash`) before leaving the fetcher so raw user IDs are never stored or passed to the analyzer.
  - Outputs `list[RawComment]` defined in `app/pipeline/contracts.py`.
- **Analysis (`app/pipeline/analyzer.py`)**:
  - Implement `CommentAnalyzer.analyze(comment: RawComment) -> AnalysisResult` (and optionally override `analyze_batch` for vectorized/batched inference).
  - Return `AnalysisResult` using the enums in `app/shared/enums.py` (`Sentiment`, `Intent`, `Language`) and `AspectSentimentDTO` in `app/shared/schemas.py`.

---

### 6. Raising Consistent API Errors

All HTTP errors use `AppException` from `app/core/exceptions.py`, which the global handler in `app/core/exception_handlers.py` formats as:

```json
{
  "error": {
    "code": "POST_NOT_FOUND",
    "message": "Post 123_456 does not exist"
  }
}
```

- Put generic HTTP base classes in `app/core/exceptions.py` (`NotFoundException`, `BadRequestException`, `ServiceUnavailableException`).
- Put domain-specific exceptions in `app/modules/<domain>/exceptions.py` (e.g., `PostNotFoundException`, `CommentNotFoundException`, `TaskQueueUnavailableException`).

---

### 7. Adding a New Feature Module

If you need a new feature area (for example `reports` or `auth`):

1. Create `app/modules/<feature>/` with `__init__.py`, `router.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, and `exceptions.py`.
2. Add a tag description in `app/api/tags.py` (`OPENAPI_TAGS`).
3. Register the router once in `app/api/v1/router.py` (`api_v1_router.include_router(...)`).
4. Add unit/API tests under `tests/`.

---

## Testing & Code Quality

Run the test suite and linter before opening a pull request:

```bash
# Run all tests
uv run pytest -v

# Check lint & formatting rules
uv run ruff check .
```

When writing tests:
- Mock external Graph API HTTP calls using `httpx.MockTransport` (see `tests/test_facebook_graph.py`) — never hit live Facebook servers in unit tests.
- Use FastAPI's `TestClient(app)` (see `tests/test_app.py`) to verify route status codes, validation errors, and OpenAPI schema generation.

---

## Recommended Git Team Workflow

To avoid conflicts across teammates:

1. **One feature/module per branch** (e.g., `feat/graph-api-client`, `feat/posts-repository`, `feat/comment-analyzer`).
2. **Stay inside your module**:
   - Graph API work -> `libs/facebook_graph.py` + `app/pipeline/fetcher.py`
   - NLP model work -> `app/pipeline/analyzer.py`
   - Posts endpoints/DB -> `app/modules/posts/*`
   - Comments endpoints/DB -> `app/modules/comments/*`
   - Queue/worker orchestration -> `app/modules/analysis/*`
3. **Coordinate changes to `app/shared/` or `app/core/`**: Because multiple modules depend on them, keep shared changes small and merge them early.
4. **Always run `uv run ruff check .` and `uv run pytest -v` before pushing.**
