# Development Roadmap: OraCLI 10G Web

## Milestone Overview

### Phase 1: Web Foundation & Walking Skeleton (Current Target)
- [x] Backend API service with FastAPI and health endpoint (`/api/health`).
- [x] Frontend Single Page App with React + TypeScript + Vite.
- [x] Application Shell: Responsive layout, developer dark console theme, left navigation sidebar.
- [x] SQL Console & Editor: Multiline editor with keyboard shortcut `Ctrl+Enter` to run, SQL*Plus formatted output pane.
- [x] End-to-End Database Pipeline: Browser → REST API (`POST /api/sql/execute`) → Oracle SQL Transpiler → SQLite Adapter → SQL*Plus Formatter → Browser Output.
- [x] Core DDL/DML Verification: `CREATE TABLE student`, `INSERT INTO student`, `SELECT * FROM student`.

### Phase 2: Schema Explorer & SQL*Plus Commands
- [ ] Database Explorer panel (`/tables`): tables, columns, constraints, datatypes.
- [ ] DESC / DESCRIBE command support in web console and API.
- [ ] In-browser SQL*Plus command support (`SET`, `SHOW`, `CLEAR`, `HELP`).
- [ ] Query history tracker (`/history`) with search, filter, copy, and re-run.

### Phase 3: Views & Materialized Views Subsystem
- [ ] Views manager (`/views`): `CREATE VIEW`, `DROP VIEW`, schema dependency view.
- [ ] Materialized views manager (`/materialized-views`): `CREATE MATERIALIZED VIEW`, snapshot storage, manual `REFRESH`.

### Phase 4: PL/SQL Engine & DBMS_OUTPUT
- [ ] PL/SQL editor workspace (`/plsql`): `DECLARE-BEGIN-END` blocks, variables, control flow (`IF`, `LOOP`, `FOR`, `WHILE`), `SELECT INTO`.
- [ ] Dedicated `DBMS_OUTPUT.PUT_LINE` capture buffer pane.

### Phase 5: Scripts & Storage
- [ ] SQL script management (`/scripts`): Upload, create, edit, save, download, and batch execute `@script.sql`.

### Phase 6: College Lab & Exam Mode
- [ ] Pre-packaged educational exercises (Tables, Constraints, DML, Aggregates, Joins, Subqueries, Views, PL/SQL).
- [ ] Isolated database sessions for tests.
- [ ] Database state evaluation engine (verifying table contents, constraints, and views).
- [ ] Timed Exam Mode with score calculation and test case reporting.
