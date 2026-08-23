# Streamlit Community Cloud Deployment Guide

This guide documents the setup, deployment, automated CI/CD validation, and monitoring procedures for **OraCLI 10G** on **Streamlit Community Cloud** with **GitHub Actions**.

---

## 1. Important Policy & Hibernation Notice

> [!IMPORTANT]
> **Platform Hibernation & Resource Limits:**
> GitHub Actions cannot guarantee continuous execution of a Streamlit Community Cloud application. Streamlit platform hibernation and resource policies remain authoritative.
> 
> When an application on Streamlit Community Cloud receives no traffic for a prolonged period, the platform automatically places the container into a hibernated state. Visiting the application URL directly in any web browser will immediately wake the application up. Do **NOT** use automated scripts, bot traffic, or artificial ping loops to circumvent platform hibernation policies.

---

## 2. Architecture & File Structure

The GitHub repository is the single source of truth for all code, configurations, and automated workflows.

```text
SQL-10G/
├── app.py                      # Primary Streamlit application entrypoint
├── requirements.txt            # Pinned, tested dependency manifest
├── runtime.txt                 # Target Python runtime version (python-3.11)
│
├── .streamlit/
│   └── config.toml             # Streamlit server & theme configuration
│
├── .github/
│   ├── dependabot.yml          # Automated dependency updater
│   └── workflows/
│       ├── ci.yml              # CI test & lint pipeline
│       ├── deploy-check.yml    # Post-CI deployment readiness check
│       └── health-check.yml    # Availability monitoring
│
├── app/                        # Application backend & SQL engine
│   ├── cli/                    # SQL*Plus formatting & command engine
│   ├── database/               # Database adapter abstraction layer
│   └── engine/                 # SQLGlot AST transpiler, DCL & MViews
│
├── scripts/
│   ├── smoke_test.py           # Pre-deployment smoke test suite
│   └── health_check.py         # HTTP health checking script
│
├── tests/                      # Pytest unit & integration test suites
└── docs/
    └── deployment.md           # This documentation
```

---

## 3. Step-by-Step Streamlit Cloud Setup

1. **Push Changes to GitHub**:
   Ensure all changes are committed and pushed to your GitHub repository `main` branch.

2. **Connect Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Sign in with your GitHub account.
   - Click **"New app"**.

3. **Configure Deployment Settings**:
   - **Repository:** `your-username/SQL-10G` (e.g. `rcpspk0305-bit/SQL-10G`)
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (optional):** Choose a custom subdomain if desired.

4. **Deploy**:
   - Click **"Deploy!"**.
   - Streamlit will read `runtime.txt` (Python 3.11), install dependencies from `requirements.txt`, apply `.streamlit/config.toml`, and launch `app.py`.

---

## 4. GitHub Actions Workflows

### 4.1 CI Pipeline (`.github/workflows/ci.yml`)
- **Trigger**: Every `push` and `pull_request` to `main`.
- **Pipeline**:
  1. Checks out repository code.
  2. Sets up Python 3.11 with pip caching.
  3. Installs dependencies from `requirements.txt`.
  4. Runs `ruff check .` linter.
  5. Executes all 61+ automated unit and integration tests via `pytest`.
  6. Runs `scripts/smoke_test.py` to verify end-to-end database engine integrity.

### 4.2 Deployment Check (`.github/workflows/deploy-check.yml`)
- **Trigger**: Runs automatically after `CI Pipeline` succeeds, or via manual `workflow_dispatch`.
- **Verification**: Validates repository file structure, dependency consistency, entrypoint presence, and outputs a deployment readiness report.

### 4.3 Health Check Monitoring (`.github/workflows/health-check.yml`)
- **Trigger**: Runs twice daily (`0 */12 * * *`) and on manual dispatch.
- **Repository Variable**: Uses the GitHub repository variable `STREAMLIT_APP_URL`.
- **Behavior**: Makes an HTTP GET request to verify application reachability (status 200), retries up to 3 times on transient network errors, and alerts if unreachable.

---

## 5. Configuring GitHub Repository Variables

To enable automated health monitoring without hardcoding URLs in source code:

1. In your GitHub repository, navigate to **Settings** > **Secrets and variables** > **Actions** > **Variables** tab.
2. Click **"New repository variable"**.
3. Set **Name:** `STREAMLIT_APP_URL`.
4. Set **Value:** Your deployed Streamlit app URL (e.g. `https://oracli-10g.streamlit.app`).
5. Click **Add variable**.

---

## 6. Secrets Management

- **Zero Secrets in Source Code**: No API keys, tokens, or credentials are committed to git.
- **Streamlit Secrets**: If external services or persistent database credentials are required in the future, configure them exclusively in the Streamlit Cloud Dashboard under **App Settings > Secrets** (`secrets.toml`).

---

## 7. Database Persistence Limitations & Roadmap

- **Current Architecture**: The application uses an isolated in-memory SQLite database per user session (`:memory:`) with full Oracle SQL transpilation, transaction management, DCL security catalogs, and materialized view snapshots.
- **Session Isolation**: Each connected user receives an independent database sandbox.
- **Ephemeral Storage**: Streamlit Community Cloud containers are ephemeral; restarting the container or refreshing the browser tab initializes a clean session.
- **Future Database Migration**: The database abstraction layer (`DatabaseAdapter` in `app/database/adapter.py`) allows migrating backend storage to PostgreSQL or Spanner without modifying any SQL parsing or translation logic.

---

## 8. Troubleshooting & FAQ

| Issue | Cause | Resolution |
|---|---|---|
| App is sleeping / "This app has gone to sleep" | Inactivity on Streamlit Community Cloud | Click "Yes, get this app back up!" in your browser. |
| `ModuleNotFoundError` during deploy | Missing dependency in `requirements.txt` | Ensure the package is added to `requirements.txt` and pushed to `main`. |
| CI Pipeline fails | Lint or test failure | Run `ruff check .` and `pytest` locally to diagnose and fix before pushing. |
| Health check workflow returns warning | `STREAMLIT_APP_URL` variable not set | Set the `STREAMLIT_APP_URL` variable in GitHub Repository Settings. |
