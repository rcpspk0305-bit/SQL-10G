# Architecture: OraCLI 10G Web

OraCLI 10G Web is a browser-based, lightweight, local educational database environment that reproduces the Oracle 10g SQL*Plus experience and command behavior on top of a modern full-stack web architecture.

## 1. High-Level Architecture Diagram

```
                    Browser Client (React + TypeScript + Vite)
                                       |
    +----------------------------------+----------------------------------+
    |                                  |                                  |
    v                                  v                                  v
+------------------+         +--------------------+             +------------------+
|   SQL Console    |         | Database Explorer  |             |  Lab / Exercises |
| (Editor, Output) |         | (Tables, Views, MV)|             |  (Practice/Exam) |
+------------------+         +--------------------+             +------------------+
                                       |
                                HTTP REST / JSON
                                       v
                    FastAPI Application Server (Python 3.12+)
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        v                              v                              v
+-------------------+        +--------------------+         +--------------------+
|  SQL / PL/SQL     |        | SQL*Plus Command   |         | Schema & Metadata  |
|  Transpiler       |        | Engine             |         | Inspector          |
| (Oracle -> SQLite)|        | (DESC, SHOW, SET)  |         | (USER_TABLES, etc.)|
+-------------------+        +--------------------+         +--------------------+
        |                              |                              |
        +------------------------------+------------------------------+
                                       |
                                       v
                             SQLite Storage Engine
                           (In-Memory / User Database)
```

## 2. Layered Subsystems

### Frontend (Browser)
- **Framework**: React 18+ with TypeScript, bundled with Vite.
- **Styling**: Modern, dark developer-console aesthetic (monochrome slate, subtle amber/blue accents, crystal-clear typography and tabular grid).
- **Core Views**:
  - `/` & `/console`: Interactive SQL*Plus console, multiline code editor, toolbar (`Run`, `Clear`, `Explain`, `Format`), tabular and feedback output pane.
  - `/tables`: Interactive database table and column browser.
  - `/views`: View definitions, source SQL, and live data inspector.
  - `/materialized-views`: Snapshot storage, refresh triggers, and metadata.
  - `/scripts`: Script manager and SQL file runner.
  - `/plsql`: PL/SQL block editor with DBMS_OUTPUT pane.
  - `/lab` & `/exam`: Step-by-step lab exercises and automated state evaluation.
  - `/history`: Executed query history with timing and replay.
  - `/settings`: Configuration (PAGESIZE, LINESIZE, HEADING, FEEDBACK, NULL).
  - `/about`: Compatibility documentation and engine details.

### Backend API (FastAPI)
- **REST Endpoints**:
  - `GET /api/health`: Health status.
  - `POST /api/sql/execute`: Executes SQL statements/scripts, translates dialect, returns structured rows, columns, feedback, and SQL*Plus pre-formatted text.
  - `GET /api/schema/tables`: Discovers user tables and columns with Oracle datatype representations.
  - `GET /api/schema/tables/{table_name}`: Detailed column, datatype, and constraint metadata.
  - `GET /api/schema/views`: Lists views and queries.
  - `GET /api/schema/materialized-views`: Materialized view registry and refresh status.
  - `POST /api/materialized-views/{name}/refresh`: Executes snapshot refresh.
  - `GET /api/history`: Returns historical queries.
  - `POST /api/lab/evaluate`: Runs student SQL against isolated database state and evaluates assertions.

### Engine & Database Layer
- **SQL Translation**: Reuses existing `app.engine.translator` and `sqlglot` to parse Oracle SQL dialect and convert to SQLite.
- **Database Engine**: Reuses `app.database.sqlite_adapter` with registered Oracle compatibility functions (`NVL`, `SYSDATE`, `DUAL`).
- **Error Mapping**: Reuses `app.engine.errors` to guarantee Oracle-style `ORA-xxxxx` error codes.
