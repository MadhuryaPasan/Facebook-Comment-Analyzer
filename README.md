# Facebook Comment Analyzer

Analyzes comments on a company's Facebook page so the company can see what customers think and which improvements they ask for. Comments are pulled from Facebook through the Graph API, stored, analyzed for sentiment, intent, language and aspects, and served to a dashboard through a REST API.

This README describes **what belongs in each folder**. Put new code in the folder whose description matches it. If no folder fits, ask the repo owner before creating a new one.

For setup steps see [`docs/setup.md`](docs/setup.md). For the API spec see [`docs/api.md`](docs/api.md).

---

## Folder structure

```
Facebook-Comment-Analyzer/
├── README.md
├── .gitignore
├── .vscode/settings.json
├── docs/
├── notebooks/
├── Frontend/
└── Backend/
    ├── main.py
    ├── pyproject.toml / uv.lock
    ├── .env.example
    ├── AGENTS.md / CLAUDE.md
    ├── libs/
    │   ├── facebook_graph.py
    │   └── comment_analyzer.py
    ├── app/
    │   ├── main.py
    │   ├── core/
    │   ├── shared/
    │   ├── api/
    │   ├── modules/
    │   │   ├── posts/
    │   │   ├── comments/
    │   │   └── analysis/
    │   ├── pipeline/
    │   │   └── ingestion.py
    │   └── workers/
    │       └── queue.py
    └── tests/
        └── test_app.py
```

---

## Root folders

### `docs/`
Project documentation for the team.
- `setup.md`: how to clone, install packages with uv, create `.env`, branch and run the project.
- `api.md`: every endpoint with its purpose and sample requests/responses.
- `uv-environment.md`: short notes on creating the uv environment.
- `ollama-cpu-mode.md`: how to run Ollama without the GPU.

**Does not hold:** code, or notes about a single person's work in progress.

### `notebooks/`
Jupyter notebooks for experiments, such as testing Graph API calls or trying analyzer models.
- Name them `<area>_<what>_test.ipynb`, e.g. `analyzer_typesafe_ollama_test.ipynb`.
- `notebooks/data/` holds exported data and is git-ignored.
- Clear all outputs before committing, and never paste tokens into a notebook.

**Does not hold:** code the app depends on. When notebook code works, move it into `Backend/app/`.

### `Frontend/`
The dashboard UI that calls the backend API.

### `Backend/`
The FastAPI backend. Run all `uv` commands from this folder.

---

## Backend root files

| File | Holds |
|---|---|
| `main.py` | Entry point. `uv run python main.py` starts the server with settings from `.env`. |
| `pyproject.toml` / `uv.lock` | Dependencies. Change them only with `uv add` / `uv remove`, and commit both files together. **Repo owner only.** |
| `.env.example` | Every environment variable with a placeholder value. Copy it to `.env` (never committed). |
| `AGENTS.md` / `CLAUDE.md` | Rules for AI coding tools: stay in your own module, don't add packages. |

---

## `Backend/libs/`

Standalone libraries with **no imports from `app/`**. They could be copied into another project unchanged.

### `facebook_graph.py`
The Meta Graph API client (`FacebookCommentAnalyzerClient`). It holds:
- reading posts, comments and replies, including following Facebook's pagination
- `get_comment()` for a single comment
- replying to and deleting comments
- retries, rate-limit handling and `MetaGraphAPIError`

**Does not hold:** anything that knows about our database, schemas or `Config`. Tokens and the page ID are passed in by the caller.

### `comment_analyzer.py`
The NLP analyzer (`CommentAnalyzer`). It holds:
- `analyze(text)` / `analyze_batch(texts)`: comment text in, a plain dict out with `language`, `sentiment`, `sentiment_score`, `intent`, `aspects`, `keywords`, `is_actionable` and `model_version`
- model loading and model calls (e.g. Ollama / TypeSafe). Load models once, when the class is created.

The string values must match `app/shared/enums.py`, so `pipeline/ingestion.py` can turn the dict into an `AnalysisResult` without changes.

**Does not hold:** database access, HTTP code, Facebook calls, or imports from `app/`. Model settings are passed into `__init__` by the caller.

---

## `Backend/app/`

### `app/main.py`
Builds the FastAPI app: CORS, global error handlers, and registering the API router.

### `app/core/`: app-wide infrastructure (repo owner only)
| File | Holds |
|---|---|
| `config.py` | `Config`: every setting read from `.env` (Facebook token, page ID, Graph API version, database, Redis, analyzer version). |
| `database.py` | Database engine and `get_session()`. |
| `dependencies.py` | Shared FastAPI dependencies, e.g. `DBSession`. |
| `exceptions.py` | Base error classes: `AppException`, `NotFoundException`, `BadRequestException`, `ServiceUnavailableException`. |
| `exception_handlers.py` | Turns every `AppException` into `{"error": {"code": ..., "message": ...}}`. |
| `logging.py` | Console and file logging setup. |

**Does not hold:** anything specific to one feature.

### `app/shared/`: types used by more than one module (repo owner only)
| File | Holds |
|---|---|
| `enums.py` | `Sentiment`, `Intent`, `Language`, `TaskStatus`. |
| `types.py` | Reusable field types: `FBPostId`, `FBCommentId`, `Score`. |
| `schemas.py` | Shared Pydantic models: `DateRangeParams`, `AspectSentimentDTO`, `ErrorResponseDTO`. |
| `contracts.py` | `RawComment` (what ingestion produces) and `AnalysisResult` (what ingestion builds from the analyzer's output). Change them only after agreeing as a team. |

### `app/api/`: API wiring (repo owner only)
| File | Holds |
|---|---|
| `tags.py` | Swagger group names and descriptions. |
| `v1/router.py` | Registers every module's router under `/api/v1`. Each module is added once. |

### `app/modules/`: one folder per feature

Every module owns its endpoints, logic and database tables. **Only that module's owner edits its folder.** Each module uses these files:

| File | Holds |
|---|---|
| `router.py` | HTTP endpoints only: read the request, call the service, return the response. No database queries. |
| `service.py` | Business logic: checks, rules, building responses, raising the module's exceptions. |
| `repository.py` | Database queries only (`select`, insert, update). |
| `models.py` | SQLModel table classes for this module. |
| `schemas.py` | Pydantic request, response and filter models for this module's endpoints. |
| `exceptions.py` | This module's errors, e.g. `PostNotFoundException`. |

#### `modules/posts/`
Endpoints: `GET /posts`, `GET /posts/{post_id}`.
Table: `posts` (`Post`). Provides `PostRepository.exists()` for the comments module.

#### `modules/comments/`
Endpoints: `GET /posts/{post_id}/comments`, `GET /comments`, `GET /comments/{comment_id}`.
Tables: `comments` (`Comment`) and `comment_analyses` (`CommentAnalysis`).

#### `modules/analysis/`
Endpoint: `POST /comments/analyze`, which queues a post's comments for (re-)analysis and returns `202` with a `task_id`.
No tables of its own and no `repository.py`.

**Rules across modules:**
- A module may import another module's `models.py`, `repository.py` or `exceptions.py`, never its `service.py` or `router.py`.
- Link tables with string foreign keys (`"posts.post_id"`), not `Relationship()` across modules.

### `app/pipeline/ingestion.py`
The single entry point for getting comments into the system, used by the analysis module.
- Converts Facebook data (`facebook_graph.py` results) into `RawComment`, hashing commenter IDs.
- Saves comments as "insert or update" by `comment_id`, so receiving the same comment twice is harmless.
- Queues saved comments for analysis.
- Calls `libs/comment_analyzer.py` with each comment's text, and turns the returned dict into an `AnalysisResult`. This is the only place in `app/` that uses the analyzer.

**Does not hold:** HTTP endpoints, or the analysis logic itself.

### `app/workers/queue.py`
Task queue setup (Redis connection and queue configuration) for running analysis in the background.

---

## `Backend/tests/`

| File | Holds |
|---|---|
| `test_app.py` | Checks that the app starts, `/health` works, and every route has a `summary` and `description` in Swagger. |

Run with `uv run pytest -v` from `Backend/`.

---

## Who edits what

| Area | Owner |
|---|---|
| `core/`, `shared/`, `api/`, `app/main.py`, `tests/test_app.py`, `pyproject.toml`, `uv.lock`, `README.md` | Repo owner |
| `modules/posts/` | Posts owner |
| `modules/comments/` | Comments owner |
| `modules/analysis/`, `workers/` | Analysis / queue owner |
| `libs/facebook_graph.py`, `pipeline/ingestion.py` | Facebook / ingestion owner |
| `libs/comment_analyzer.py` | Analyzer owner |

Need a change in a folder you don't own? Ask its owner, or open a GitHub issue. For branch naming and pull requests, see `docs/setup.md`.
