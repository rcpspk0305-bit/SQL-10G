# Changelog

All notable changes to **OraCLI 10G** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-streamlit-launch] - 2026-08-23

### Added
- **Streamlit Community Cloud Primary Entrypoint**: Full interactive Oracle SQL*Plus 10g workspace in `app.py`.
- **Streamlit Configuration**: Theme, server, and headless settings in `.streamlit/config.toml`.
- **Target Runtime & Dependency Pinning**: `runtime.txt` (Python 3.11) and pinned `requirements.txt`.
- **Automated CI Pipeline**: `.github/workflows/ci.yml` running linting, 61+ pytest test cases, and smoke tests on push/PR.
- **Deployment Verification Workflow**: `.github/workflows/deploy-check.yml` validating structure and compatibility.
- **Health Check Monitoring**: `.github/workflows/health-check.yml` with retry and failure alerts using `STREAMLIT_APP_URL`.
- **Smoke & Health Check Scripts**: `scripts/smoke_test.py` and `scripts/health_check.py`.
- **Deployment Documentation**: Complete deployment, hibernation, and architecture manual in `docs/deployment.md`.
- **Dependabot Integration**: `.github/dependabot.yml` for automated dependency updates.

## [0.3.0-core-db] - 2026-08-23

### Added
- **Complete DDL Subsystem**: Full support for `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `TRUNCATE TABLE`, `RENAME TABLE`, `CREATE INDEX`, `DROP INDEX`, `CREATE VIEW`, `DROP VIEW`.
- **DCL Educational Security & Privileges**: `GRANT` and `REVOKE` for `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `ALL` with `_oracli_privileges` catalog and `ORA-01031: insufficient privileges` enforcement.
- **TCL Real Transaction Subsystem**: Full ACID transaction controls with `COMMIT`, `ROLLBACK`, `SAVEPOINT <name>`, `ROLLBACK TO [SAVEPOINT] <name>`.
- **Advanced Query Operations**: Full support for `WHERE`, `ORDER BY` (ASC/DESC/multi-column/alias), `GROUP BY`, `HAVING` (evaluated post-aggregation), `JOIN` (INNER, LEFT, CROSS), `UNION`, `INTERSECT`, and `MINUS` (`EXCEPT`).
- **Aggregates**: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()` with multi-expression projection.
- **Constraints & Cascade**: Support for `PRIMARY KEY`, `FOREIGN KEY ... ON DELETE CASCADE`, `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT`.
- **Materialized Views**: Emulated snapshot table layer with `CREATE MATERIALIZED VIEW`, `REFRESH MATERIALIZED VIEW`, and `DROP MATERIALIZED VIEW`.
- **SQL*Plus Client Commands**: Implemented `DESC` / `DESCRIBE`, `SHOW USER`, `SET`, `CLEAR`, `LIST`, `RUN`, `SPOOL`, `COLUMN`, `EXIT`, `QUIT`.
- **Web UI Quick Palette & Live Matrix**: Quick-insert database operations bar, live feature compatibility matrix, and 18-part lab exercises.

## [0.2.0-web] - 2026-08-23

### Added
- **Web Application Architecture**: Browser-based educational platform with React 18, TypeScript, and Vite.
- **FastAPI Backend Server**: High-performance REST API with endpoints for SQL execution, schema discovery, query history, and health checks.
- **SQL Console Workspace**: In-browser SQL editor with `Ctrl+Enter` execution, toolbar controls, sample script loader, and real-time SQL*Plus formatted output.
- **Data Grid View**: Tabbed output switcher between SQL*Plus monospace terminal and interactive tabular data grid.
- **Database Explorer & Views**: Tables browser with columns, datatypes, PK indicators, and quick-action query generators (`SELECT *`, `DESC`).
- **College Lab Mode**: Pre-packaged coursework exercises (DDL, Constraints, DML, Joins, Aggregates, Views) with practice and timed exam modes.
- **Production Build Integration**: Vite frontend pre-built into `web/dist` and directly served by FastAPI.

## [0.1.0-alpha] - 2026-08-23

### Added
- Core architecture, project layout, and pyproject.toml configuration.
- Interactive SQL*Plus 10g terminal shell with `SQL>` prompt and multiline continuation `  2  `.
- Multiline input buffer with quote, string literal, and comment awareness.
- Oracle SQL to SQLite transpiler supporting `NUMBER`, `VARCHAR2`, `DATE`, `CHAR`, `INTEGER`.
- SQLite database adapter with in-memory and file-backed persistence.
- Oracle SQL*Plus table and feedback output formatter (aligned headers, dashed separators, right-aligned numbers).
- Error mapper for `ORA-00942`, `ORA-00904`, `ORA-00001`, `ORA-01400`, `ORA-00933`.
- Basic SQL*Plus commands (`EXIT`, `QUIT`, `SHOW USER`, `SET`).
- Test suite with unit and end-to-end integration tests.
