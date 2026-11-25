# AI Assistant Instructions — Facebook Comment Analyzer (Backend)

**Repository:** `MadhuryaPasan/Facebook-Comment-Analyzer`
**Repository Owner:** Madhurya Pasan
**GitHub Issues:** https://github.com/MadhuryaPasan/Facebook-Comment-Analyzer/issues

This is a multi-developer project. Multiple team members work on different modules in parallel. Your highest priority as an AI assistant is to **avoid merge conflicts**, **protect shared code**, and **strictly follow the project architecture**.

---

## 1. Strict File Scope Rules (Zero Merge Conflicts — Hard Rule)

**Under NO circumstances may you cause merge conflicts or edit files belonging to other team members or shared infrastructure.**

1. **Mandatory Pre-Edit Scope Check — work ONLY on the current developer's assigned files/module.**
   - Before making ANY edit, verify which module/files the developer is assigned to.
   - If the request is ambiguous or does not clearly specify which module/files they own, **STOP and ask** before touching any file.
   - Even if the developer asks to "fix everything", "update all modules", or "make it work end-to-end", **refuse to edit files outside their assigned scope**.
2. **Do NOT make drive-by edits or repo-wide formatting.**
   - Never reformat, refactor, rename, or "clean up" files outside the developer's assigned scope.
   - Never run repo-wide auto-formatters or auto-fixers (`ruff format .`, `ruff check --fix .`, `prettier --write .`, `eslint --fix .`); only run format/fix commands on the exact file(s) the developer owns.
   - Never touch other team members' feature modules, components, or unrelated tests.
   - Never run `git merge`, `git rebase`, `git reset`, `git push --force`, or overwrite/auto-resolve conflicts in shared or teammates' files.
3. **Protected / Shared Files (DO NOT MODIFY under any circumstances without Repo Owner approval):**
   - **Backend shared/core:** `app/core/*` (`config.py`, `database.py`, `dependencies.py`, `exceptions.py`, `exception_handlers.py`, `logging.py`), `app/shared/*` (`enums.py`, `types.py`, `schemas.py`), `app/pipeline/contracts.py` (`RawComment`, `AnalysisResult`), `main.py`, `app/main.py`, `app/api/tags.py`, `app/api/v1/router.py`, `tests/test_app.py`, `tests/test_facebook_graph.py`.
   - **Frontend shared/core (if present):** `package.json`, lockfiles, build/lint/TS configs, `.env*`, root app/router/layout/navigation files, global styles/theme tokens, shared API client, and shared types/hooks/store files.
   - **Project & config files:** `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, `README.md`, `AGENTS.md`, `CLAUDE.md`.
   - **Other members' modules:** Any directory or file under `app/modules/<other_domain>/*`, `libs/*`, `app/pipeline/*`, or frontend feature folders outside the developer's assigned area.

### What to do if a task requires changing shared or other members' files

**STOP immediately. Make ZERO edits to those files.**
Instead, output a clear message to the developer explaining:
1. Which shared or other-member file(s) need changes and why.
2. That they must **contact the repository owner (Madhurya Pasan)** or **open a GitHub Issue** at https://github.com/MadhuryaPasan/Facebook-Comment-Analyzer/issues before making changes to shared or cross-team files.

---

## 2. Package & Dependency Rules (DO NOT Install or Add Packages)

- **NEVER** add, remove, or upgrade packages in either Backend or Frontend.
- **NEVER** modify `pyproject.toml`, `uv.lock`, `.python-version`, `package.json`, or lockfiles, and **NEVER** run `uv add`, `uv remove`, `pip install`, `npm install`, `pnpm add`, `yarn add`, or similar commands.
- If a feature or fix requires a new package or dependency change:
  - **STOP** — do not install it or modify dependency files.
  - Tell the developer which package is needed and why, and instruct them to **contact the repository owner (Madhurya Pasan)** or **open a GitHub Issue** at https://github.com/MadhuryaPasan/Facebook-Comment-Analyzer/issues to request approval.

---

## 3. Module Ownership Map

Stay within the area assigned to the current developer:

| Area | Owned Files |
| --- | --- |
| Graph API Client | `libs/facebook_graph.py` |
| Comment Ingestion Adapter | `app/pipeline/fetcher.py` |
| NLP / Sentiment Analyzer | `app/pipeline/analyzer.py` |
| Posts Feature | `app/modules/posts/*` |
| Comments Feature | `app/modules/comments/*` |
| Analysis Feature | `app/modules/analysis/*` |
| Unit Tests for a Feature | New or assigned test file under `tests/` |

---

## 4. Mandatory Project Architecture Rules

Follow the architecture documented in `README.md`:

### Dependency Direction
```text
libs/facebook_graph.py   <-- (ZERO imports from app.*)
        ^
        |
app/pipeline/fetcher.py  --> app/pipeline/contracts.py <-- app/pipeline/analyzer.py
                                      ^
app/modules/<domain>/router.py --> service.py --> repository.py --> models.py
        |                              |
        v                              v
   schemas.py / exceptions.py     app/core/* & app/shared/*
```

- **`libs/facebook_graph.py`**:
  - Must remain a standalone, single-file library using only Python stdlib and `httpx`.
  - **MUST NOT** import `app.*`, `fastapi`, or `sqlmodel`, and must not read `Config` directly (pass tokens/versions into `__init__`).
  - Map Graph API failures to its own exception classes (`FacebookGraphError`, `FacebookGraphAuthError`, `FacebookGraphRateLimitError`, `FacebookGraphNotFoundError`).
- **`app/pipeline/fetcher.py`**:
  - Adapts `FacebookGraphClient` into `list[RawComment]` (from `app/pipeline/contracts.py`).
  - Must hash raw Facebook user IDs (`author_hash`) before leaving the fetcher.
- **`app/pipeline/analyzer.py`**:
  - Implements `CommentAnalyzer.analyze(comment: RawComment) -> AnalysisResult` (and optional `analyze_batch`).
  - **MUST NOT** import from `libs/` or `app/modules/*/router.py` — only `app/pipeline/contracts.py`, `app/shared/*`, and `app/core/config.py`.
- **`app/modules/<domain>/` (3-layer isolation)**:
  - `router.py`: HTTP layer only. Parse request params/bodies via FastAPI + Pydantic, inject `DBSession`, and delegate directly to the service. **Never** put SQL/DB queries in `router.py`. Every route must include OpenAPI `summary` and `description`.
  - `service.py`: Business logic only. Receive Pydantic DTOs and `db: Session`, call `repository.py`, raise domain exceptions, and return response DTOs.
  - `repository.py`: Database access only (`SQLModel` `select(...)` queries). No HTTP logic.
  - `models.py`: `SQLModel` table classes for that domain only.
  - `schemas.py`: Pydantic DTOs with `Annotated[..., Field(description="...")]`.
  - `exceptions.py`: Domain exceptions subclassing `AppException` (or `NotFoundException`, `BadRequestException`, `ServiceUnavailableException`) from `app/core/exceptions.py`.
  - **No cross-module internal imports**: Do not import internals directly from sibling modules (`app/modules/<other>/*`). If shared types/enums/schemas are needed across modules, stop and tell the developer to contact **Madhurya Pasan** or open a GitHub issue.

---

## 5. Testing & Code Quality

- Before finishing work on the developer's assigned files, run read-only checks (do not auto-format other members' files):
  - `uv run ruff check .`
  - `uv run pytest -v` (or the relevant test file under `tests/`)
- Mock external Meta Graph API calls with `httpx.MockTransport` — never hit live Facebook APIs in tests.
- Never weaken, skip, or delete existing assertions or tests (such as `tests/test_app.py` or `tests/test_facebook_graph.py`) to make tests pass.

---

## 6. Clean, Professional Design & Zero "AI Slop"

Write production-grade code and UI — **never** generate generic "AI slop":

### Frontend & UI Design Rules (Strictly Enforced)
- **Clean, professional visual design**: Use a restrained, cohesive color palette, clear visual hierarchy, consistent spacing/alignment, and readable typography suitable for a real analytics product.
- **No "AI slop" UI tropes**:
  - **NO** cliché purple/indigo/neon gradients, glowing cards, excessive glassmorphism, or decorative animations that hurt clarity.
  - **NO** emojis used as UI icons or status badges — use a proper, consistent icon set or clean text/SVG icons.
  - **NO** fake marketing hero sections, filler taglines, dummy metrics, or hardcoded fake chart data presented as real analytics.
- **Real product states**: Every view and data component must properly handle loading, empty, and error states from real API responses (matching the backend's `ErrorResponseDTO` and pagination/response schemas).
- **Minimal, maintainable components**: Keep styling and component structure clean and consistent with the existing frontend system; do not invent redundant wrapper components or inline style clutter.

### Backend & General Code Quality (No Code Slop)
- **No filler comments or dead boilerplate**: Write concise docstrings and only comment non-obvious *why* decisions — never narrate obvious lines (`# increment counter`).
- **No fake fallbacks or silent stubs**: Do not mask missing data or failed API calls with hardcoded dummy values or bare `except: pass` blocks.
- **Keep changes minimal and idiomatic**: Only build what is actually required for the task.

