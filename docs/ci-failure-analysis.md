# CI/CD Pipeline Failure Analysis & Resolution

## Problem: GitHub Actions Step 7 `Run Test Suite (Pytest)` Failed

- **Problem:** GitHub Actions CI job `Build, Lint & Test` failed at Step 7 (`Run Test Suite (Pytest)`).
- **Root Cause:** When running `pytest -v` directly on Linux runners without the package installed in editable mode (`pip install -e .`) and without `pythonpath = ["."]` in `[tool.pytest.ini_options]`, Python's module resolver could not locate the root `app` package during test collection, resulting in `ModuleNotFoundError: No module named 'app'`.
- **Affected Files:** `pyproject.toml`, `.github/workflows/ci.yml`, `requirements.txt`
- **Why It Failed:** 
  1. On Windows, `pytest` often adds the working directory to `sys.path`. On Ubuntu Linux runners in GitHub Actions, `pytest -v` does not automatically prepend `.` to `sys.path` unless configured via `pythonpath = ["."]` or invoked via `python -m pytest`.
  2. `requirements.txt` previously lacked `httpx` for `TestClient`.
- **Fix:** 
  1. Added `pythonpath = ["."]` to `[tool.pytest.ini_options]` in `pyproject.toml`.
  2. Added `pip install -e .` to `.github/workflows/ci.yml`.
  3. Standardized all CI test/lint runners to use `python -m pytest -v`, `python -m ruff check .`, and `python -m ruff format --check .`.
  4. Removed redundant `deploy-check.yml` to save compute minutes and prevent unnecessary duplicate test runs.
- **Verification:** 
  - Verified `python -m ruff check .` -> 0 errors.
  - Verified `python -m ruff format --check .` -> 0 errors.
  - Verified `python -m pytest -v` -> 61/61 tests passing.
  - Verified `python scripts/smoke_test.py` -> 9/9 stages passing.
