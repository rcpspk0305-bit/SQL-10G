# Changelog

All notable changes to **OraCLI 10G** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
