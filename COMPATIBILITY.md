# Compatibility Matrix: OraCLI 10G Web

This document outlines Oracle 10g feature compatibility across the web application.

---

## 1. Datatypes

| Oracle Datatype | Status | Internal Mapping / Emulation |
|---|---|---|
| `NUMBER` | EMULATED | Mapped to SQLite `NUMERIC` / `REAL` |
| `NUMBER(p, s)` | EMULATED | Mapped to SQLite `NUMERIC` |
| `VARCHAR2(n)` | EMULATED | Mapped to SQLite `TEXT` |
| `CHAR(n)` | EMULATED | Mapped to SQLite `TEXT` |
| `DATE` | EMULATED | Mapped to SQLite `TEXT` (ISO-8601 string) |
| `TIMESTAMP` | EMULATED | Mapped to SQLite `TEXT` |
| `CLOB` | EMULATED | Mapped to SQLite `TEXT` |
| `BLOB` | SUPPORTED | Mapped to SQLite `BLOB` |
| `INTEGER` / `INT` | SUPPORTED | Mapped to SQLite `INTEGER` |

---

## 2. SQL DDL & DML

| Feature | Status | Notes |
|---|---|---|
| `CREATE TABLE` | SUPPORTED | Supports column definitions, constraints (PK, FK, UNIQUE, NOT NULL, CHECK, DEFAULT) |
| `DROP TABLE` | SUPPORTED | Supported |
| `ALTER TABLE` | SUPPORTED | Basic add/drop columns |
| `TRUNCATE TABLE`| SUPPORTED | Transpiled to DELETE / VACUUM |
| `INSERT INTO` | SUPPORTED | Values lists and SELECT inserts |
| `SELECT` | SUPPORTED | Projections, WHERE, GROUP BY, HAVING, ORDER BY, DISTINCT, Subqueries |
| `UPDATE` | SUPPORTED | Standard UPDATE with WHERE |
| `DELETE` | SUPPORTED | Standard DELETE with WHERE |
| `CREATE VIEW` | PARTIALLY SUPPORTED | In progress for Phase 3 |
| `CREATE MATERIALIZED VIEW` | EMULATED | In progress for Phase 3 |

---

## 3. SQL Functions

| Function | Status | Notes |
|---|---|---|
| `COUNT`, `SUM`, `AVG`, `MIN`, `MAX` | SUPPORTED | Standard aggregate functions |
| `NVL(expr1, expr2)` | SUPPORTED | Oracle NULL coalescing function |
| `COALESCE(...)` | SUPPORTED | Standard ANSI SQL coalescing |
| `SYSDATE` | SUPPORTED | Returns current date in DD-MON-YY format |
| `UPPER`, `LOWER`, `LENGTH`, `TRIM` | SUPPORTED | String scalar functions |
| `SUBSTR`, `INSTR` | SUPPORTED | 1-indexed string slicing/searching |
| `ROUND`, `TRUNC`, `MOD` | SUPPORTED | Math scalar functions |

---

## 4. SQL*Plus Client Commands

| Command | Status | Web Behavior |
|---|---|---|
| `SHOW USER` | SUPPORTED | Returns current database user (default `SYSTEM`) |
| `SET PAGESIZE` | SUPPORTED | Configures pagination repeat line intervals |
| `SET LINESIZE` | SUPPORTED | Configures line width limits |
| `SET HEADING` | SUPPORTED | Toggles column headings ON/OFF |
| `SET FEEDBACK` | SUPPORTED | Toggles row count feedback ON/OFF |
| `SET NULL` | SUPPORTED | Configures NULL display string |
| `DESC` / `DESCRIBE` | PARTIALLY SUPPORTED | Table description rendering |
| `CLEAR SCREEN` | SUPPORTED | Clears web console output buffer |
| `EXIT` / `QUIT` | SUPPORTED | Supported in terminal mode; resets session in web mode |
| `HOST` | NOT SUPPORTED | Disabled for security |
