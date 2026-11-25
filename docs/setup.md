# Project setup guide: Facebook Comment Analyzer

Follow these steps once to get the backend running on your machine. The daily workflow is at the end.

Repo: https://github.com/MadhuryaPasan/Facebook-Comment-Analyzer

---

## 1. Install the tools

You need these three:

| Tool | Why | Check it's installed |
|---|---|---|
| **Git** | Get the code and push your work | `git --version` |
| **uv** | Installs Python and all packages for the project | `uv --version` |
| **PostgreSQL** | The database (only needed once we start using the DB) | `psql --version` |

**Install uv** (it can also install Python 3.13 for you, so you don't need to install Python yourself):

- macOS / Linux:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- Windows (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

Close and reopen your terminal afterwards, then run `uv --version` to check.

---

## 2. Clone the repository

```bash
git clone https://github.com/MadhuryaPasan/Facebook-Comment-Analyzer.git
cd Facebook-Comment-Analyzer
```

Make sure you're on the latest `main`:

```bash
git checkout main
git pull
```

Then create **your own branch** to work on. Never work directly on `main` (the naming rules are in "Branching" below):

```bash
git checkout -b feature/<feature-name>
# example: git checkout -b feature/facebook-api
```

---

## 3. Install the packages

All Python code lives in `Backend/`. Run uv from there:

```bash
cd Backend
uv sync
```

`uv sync` does three things:

1. Installs Python 3.13 if you don't have it (from `.python-version`).
2. Creates a virtual environment in `Backend/.venv/`.
3. Installs the exact package versions listed in `uv.lock`, so everyone on the team has the same versions.

You don't need to activate the virtual environment. Put `uv run` in front of every command instead (see step 5).

---

## 4. Create your `.env` file

The app reads its settings from `Backend/.env`. That file is **not** in Git because it holds secrets, so each person creates their own from the example:

- macOS / Linux:
  ```bash
  cp .env.example .env
  ```
- Windows (PowerShell):
  ```powershell
  Copy-Item .env.example .env
  ```

Open `.env` and fill in the values:

| Variable | What to put |
|---|---|
| `FB_PAGE_ID` | The Facebook page id (ask Sharuna) |
| `FB_PAGE_ACCESS_TOKEN` | The page access token (ask Sharuna, and never post it in chat or commit it) |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | Your local PostgreSQL details |
| Everything else | Leave the default |

> The app **won't start** without `FB_PAGE_ID` and `FB_PAGE_ACCESS_TOKEN`. Any placeholder value is fine until you need to call Facebook.

---

## 5. Run the backend

From `Backend/`:

```bash
uv run python main.py
```

or, with auto-reload while coding:

```bash
uv run fastapi dev main.py
```

Check it works:

- http://localhost:8000/health should show `{"status": "ok"}`
- http://localhost:8000/docs shows all the API endpoints (Swagger UI)

The full API spec is in `docs/api.md`.

---

## 6. VS Code setup (optional)

The repo already includes `.vscode/settings.json`, which points VS Code to `Backend/.venv`. If VS Code doesn't pick it up:

1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac).
2. Choose **Python: Select Interpreter**.
3. Pick `Backend/.venv`.

---

## 7. Jupyter notebooks (for testing)

We use `.ipynb` notebooks to try things out, for example testing the Graph API calls or the analyzer model on sample comments. Notebooks are for experiments. Once code works, move it into `app/` so the API can use it.

### Where they go

Notebooks live in the **`notebooks/` folder at the repo root**, next to `Backend/`, named by what they test:

```
Facebook-Comment-Analyzer/
├── Backend/
│   ├── app/
│   ├── .venv/          ← notebooks use this environment too
│   └── main.py
├── notebooks/
│   ├── fetcher_graph_api_test.ipynb
│   └── analyzer_sentiment_test.ipynb
├── docs/
└── frontend/
```

Keep them in `notebooks/` rather than loose in the root, so the root stays clean.

### Running them

Notebooks use the same environment as the backend, `Backend/.venv`. There's no separate setup for them: `uv sync` in `Backend/` already installs `ipykernel`, which VS Code needs to run notebooks. You don't need to install Jupyter separately.

1. Open the `.ipynb` file in VS Code.
2. Click **Select Kernel** (top right) → **Python Environments** → choose **`Backend/.venv`**. If it isn't listed, choose **Enter interpreter path** and enter `Backend/.venv/bin/python` (on Windows: `Backend\.venv\Scripts\python.exe`).

If VS Code asks to install `ipykernel`, you picked the wrong kernel. Choose `Backend/.venv` instead of clicking install, because installing from that prompt skips `uv.lock`.

### Importing project code in a notebook

The repo's `.vscode/settings.json` runs every notebook from the `notebooks/` folder:

```json
"jupyter.notebookFileRoot": "${workspaceFolder}/notebooks"
```

So relative paths start from `notebooks/`. For example, `"data/comments.json"` means `notebooks/data/comments.json`.

The `app` package is inside `Backend/`, so Python can't find it from `notebooks/` on its own. Make this the **first cell of every notebook** that uses project code:

```python
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND = Path.cwd().parent / "Backend"
sys.path.insert(0, str(BACKEND))   # lets `from app...` work
load_dotenv(BACKEND / ".env")      # loads Backend/.env (token, DB settings)
```

After that cell, project imports work:

```python
from app.config import Config
from app.models.schemas.comment import RawComment
```

If you change code in `app/` while a notebook is open, restart the kernel to load the new version.

### Notebook rules

- **Clear all outputs before committing.** Outputs can contain the access token, API responses and personal data from Facebook comments, and they cause merge conflicts. In VS Code, click **Clear All Outputs** in the notebook toolbar, then save.
- **Never paste the token into a notebook.** Read it from `.env` with `Config.FB_PAGE_ACCESS_TOKEN` instead.
- **Don't commit downloaded data** such as large CSV or JSON exports of real comments. Keep it in `notebooks/data/`, which is in `.gitignore`.
- **Don't import notebooks from `app/`.** The app code must never depend on a notebook.

---

## Branching: always work on your own branch

Every piece of work gets **its own branch**, created from `main`. Nobody commits directly to `main`. Work reaches `main` only through a reviewed Pull Request.

```
main
  │
  ├── feature/user-authentication
  ├── feature/facebook-api
  ├── feature/sentiment-analysis
  ├── feature/dashboard
  └── fix/comment-fetching
```

### Branch names

Use `<type>/<short-description>`, lowercase, words joined with `-`:

| Prefix | Use it for | Examples |
|---|---|---|
| `feature/` | New functionality | `feature/facebook-api`, `feature/sentiment-analysis`, `feature/dashboard` |
| `fix/` | Fixing a bug in existing code | `fix/comment-fetching`, `fix/token-expiry` |

Name the branch after **what it does**, not who is doing it. `feature/facebook-api` is right; `madhurya/stuff` or `test-branch` are not.

**One branch = one feature or one fix.** When it's merged, start a new branch for the next piece of work. Don't keep reusing an old branch.

### Starting a new branch

```bash
git checkout main
git pull                                   # get the latest code
git checkout -b feature/<feature-name>     # or fix/<what-you-fix>
cd Backend && uv sync                      # install any new packages
```

### Keeping your branch up to date

When others merge into `main`, bring their changes into your branch, at least once a day, and always before opening a Pull Request:

```bash
git checkout main
git pull
git checkout feature/<feature-name>
git merge main
cd Backend && uv sync
```

If Git reports a **merge conflict**, open the listed files, keep the right code between the `<<<<<<<` and `>>>>>>>` markers, delete the markers, then:

```bash
git add .
git commit
```

Ask the person who wrote the other side of the conflict if you're not sure which code to keep.

### Finishing a branch

1. Update from `main` (above) and make sure the app still runs.
2. Push your branch:
   ```bash
   git push -u origin feature/<feature-name>
   ```
3. On GitHub, open a **Pull Request** from your branch **into `main`**.
4. At least one teammate reviews it, then it's merged.
5. Delete the branch after merging. GitHub offers a button for this. Locally:
   ```bash
   git checkout main
   git pull
   git branch -d feature/<feature-name>
   ```

---

## Daily workflow

### Start of the day: get the latest code and packages

```bash
git checkout main
git pull
git checkout feature/<feature-name>
git merge main
cd Backend
uv sync
```

Run `uv sync` **every time you pull**. If someone added a package, it gets installed. If you skip this, you'll see `ModuleNotFoundError`.

### Adding a new package

Always use `uv add`, **never `pip install`**:

```bash
cd Backend
uv add <package-name>             # needed to run the app
uv add --dev <package-name>       # only for development (tests, linting)
```

`uv add` updates both `pyproject.toml` and `uv.lock`. **Commit both files** so the rest of the team gets the package on their next `uv sync`.

To remove a package: `uv remove <package-name>`.

### Saving and sharing your work

```bash
git status                        # check what changed
git add .
git commit -m "feat: short description of what you did"
git push -u origin feature/<feature-name>  # -u only needed the first time
```

Then open a **Pull Request** on GitHub into `main` so someone can review it before it's merged.

---

## Rules

- **Always work on your own branch.** Never commit or push directly to `main`. Name branches `feature/...` or `fix/...`. See "Branching" above.
- **Never commit `.env`.** It's in `.gitignore`. If a token is ever pushed by mistake, tell the team so it can be replaced.
- **Never commit `.venv/`** or `__pycache__/`. Both are in `.gitignore` already.
- **Clear notebook outputs before committing**, and keep tokens out of notebooks (see step 7).
- **Never use `pip install`.** Use `uv add`, otherwise your package won't be in `uv.lock`.
- **Commit `pyproject.toml` and `uv.lock` together** whenever packages change.
- **Don't share the project as a zip.** Push to your branch instead. Zips can include your `.env` and the `.venv` folder.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `uv: command not found` | Reopen the terminal after installing uv. On Windows, restart VS Code too. |
| `ModuleNotFoundError: No module named ...` | Run `uv sync` in `Backend/`, and run the app with `uv run`. |
| `KeyError: 'FB_PAGE_ID'` | Your `.env` is missing or not in `Backend/`. Redo step 4. |
| `Address already in use` (port 8000) | Another server is running. Stop it, or set a different `BACKEND_PORT` in `.env`. |
| VS Code shows red import errors but the app runs | Select the `Backend/.venv` interpreter (step 6). |
| Notebook asks to install `ipykernel` | Select the `Backend/.venv` kernel instead (step 7), then run `uv sync`. |
| `ModuleNotFoundError: No module named 'app'` in a notebook | Run the setup cell from step 7 first. If it still fails, restart the kernel. |
| `KeyError: 'FB_PAGE_ID'` in a notebook | The setup cell's `load_dotenv` must run **before** `from app.config import Config`. |
| `uv sync` fails after pulling | Make sure you're in `Backend/`, then try `uv sync --refresh`. |
