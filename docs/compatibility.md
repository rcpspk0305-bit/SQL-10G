# Compatibility Matrix: OraCLI 10G

This document classifies Oracle 10g feature compatibility in OraCLI 10G into four categories:
- **SUPPORTED**: Directly implemented and conforms to Oracle 10g SQL syntax & semantics.
- **EMULATED**: Translated or simulated to work transparently over the underlying engine.
- **PARTIALLY SUPPORTED**: Subset of clauses or arguments supported.
- **NOT SUPPORTED**: Explicitly not implemented in this release.

---

## 1. Datatypes

| Oracle Datatype | Status | Internal Mapping / Behavior |
|---|---|---|
| `NUMBER` | EMULATED | Mapped to SQLite `REAL` / `INTEGER` / `NUMERIC` |
| `NUMBER(p, s)` | EMULATED | Mapped to SQLite `NUMERIC`, precision verified |
| `VARCHAR2(n)` | EMULATED | Mapped to SQLite `TEXT` |
| `CHAR(n)` | EMULATED | Mapped to SQLite `TEXT` |
| `DATE` | EMULATED | Mapped to SQLite `TEXT` (ISO-8601 representation) |
| `TIMESTAMP` | EMULATED | Mapped to SQLite `TEXT` |
| `INTEGER` / `INT` | SUPPORTED | Mapped to SQLite `INTEGER` |
| `CLOB` | EMULATED | Mapped to SQLite `TEXT` |
| `BLOB` | SUPPORTED | Mapped to SQLite `BLOB` |

---

## 2. SQL DDL & DML

| Feature | Status | Notes |
|---|---|---|
| `CREATE TABLE` | SUPPORTED | Supports columns, datatypes, constraints (PK, FK, UNIQUE, NOT NULL, CHECK, DEFAULT) |
| `DROP TABLE` | SUPPORTED | Supports standard table deletion |
| `INSERT INTO` | SUPPORTED | Single-row and multi-row value insertion |
| `SELECT` | SUPPORTED | Basic queries, projection, WHERE, ORDER BY, GROUP BY, HAVING |
| `UPDATE` | SUPPORTED | Basic update with WHERE condition |
| `DELETE` | SUPPORTED | Basic delete with WHERE condition |
| `CREATE VIEW` | PLANNED (Phase 3) | View metadata and execution |
| `CREATE MATERIALIZED VIEW` | PLANNED (Phase 3) | Materialized view snapshot and manual refresh |

---

## 3. SQL*Plus Commands

| Command | Status | Notes |
|---|---|---|
| `EXIT` / `QUIT` | SUPPORTED | Terminates interactive session |
| `SHOW USER` | SUPPORTED | Shows current user (defaults to `SYSTEM`) |
| `SET PAGESIZE` | SUPPORTED | Controls table pagination / repeat header lines |
| `SET LINESIZE` | SUPPORTED | Sets maximum output line width |
| `SET HEADING` | SUPPORTED | Toggles column headings on/off |
| `SET FEEDBACK` | SUPPORTED | Toggles row count feedback on/off |
| `SET NULL` | SUPPORTED | Configures custom string for NULL values |
| `DESC` / `DESCRIBE` | PLANNED (Phase 2) | Displays table/view structure in Oracle format |
| `SPOOL` | PLANNED (Phase 2) | Writes terminal output to file |
