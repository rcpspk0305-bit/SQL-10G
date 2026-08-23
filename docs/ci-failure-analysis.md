# CI/CD Pipeline Failure Analysis & Resolution

## Problem 1: Missing `httpx` Test Dependency in Clean Environments

- **Problem:** GitHub Actions CI job `Build, Lint & Test` failed during `pytest` test suite execution.
- **Root Cause:** `fastapi.testclient.TestClient` requires `httpx` at runtime. `httpx` was not listed in `requirements.txt`.
- **Affected File:** `requirements.txt` & `tests/api/test_routes.py`
- **Why It Failed:** In a fresh runner environment (e.g. GitHub Actions `ubuntu-latest`), running `pip install -r requirements.txt` installed `fastapi` without `httpx`. When `pytest` loaded `tests/api/test_routes.py`, `TestClient(create_app())` raised `RuntimeError: The starlette.testclient module requires the httpx library to be installed.`
- **Fix:** Added pinned `httpx>=0.27.0,<=0.28.1` to `requirements.txt` and `pyproject.toml`.
- **Verification:** Verified `pytest -v` across all 61 tests in an isolated clean environment.

---

## Problem 2: Python Version Mismatch Between `pyproject.toml` and Deployment Runtime

- **Problem:** Inconsistent Python version constraints across configuration files.
- **Root Cause:** `pyproject.toml` declared `requires-python = ">=3.12"` and `target-version = "py312"`, whereas `.github/workflows/ci.yml`, `runtime.txt`, and Streamlit Community Cloud target Python 3.11.
- **Affected File:** `pyproject.toml`
- **Why It Failed:** Package managers or build tools verifying `pyproject.toml` metadata against Python 3.11 environments could fail dependency resolution or flag environment incompatibility.
- **Fix:** Standardized `requires-python = ">=3.11"` and `target-version = "py311"` in `pyproject.toml` to unify local, CI, and production environments on Python 3.11.
- **Verification:** Verified compatibility with `ruff check .`, `pytest`, and `python scripts/smoke_test.py` under Python 3.11.

---

## Problem 3: Ruff Formatting Discrepancies (`ruff format --check .`)

- **Problem:** Style and formatting inconsistency across application files.
- **Root Cause:** Unformatted dictionary literal blocks and multiline line breaks in `app.py`, `app/api/routes_sql.py`, and `app/cli/sqlplus_commands.py`.
- **Affected Files:** `app.py`, `app/api/routes_sql.py`, `app/cli/sqlplus_commands.py`, `scripts/smoke_test.py`
- **Why It Failed:** Running `ruff format --check .` flagged 4 files as unformatted.
- **Fix:** Executed `ruff format .` to canonicalize formatting across the entire codebase.
- **Verification:** `ruff format --check .` and `ruff check .` both return 0 errors.

---

## Problem 4: Missing Concurrency Control & Compute Waste in GitHub Actions

- **Problem:** Obsolete CI runs continued executing on GitHub Actions when new commits were pushed, wasting compute minutes and increasing carbon footprint.
- **Root Cause:** `.github/workflows/ci.yml` lacked a concurrency group with `cancel-in-progress: true`.
- **Affected File:** `.github/workflows/ci.yml`
- **Why It Failed:** Multiple parallel CI executions consumed redundant runner resources.
- **Fix:** Added concurrency group `ci-${{ github.ref }}` with `cancel-in-progress: true` and streamlined steps.
- **Verification:** Tested workflow concurrency cancellation configuration.
