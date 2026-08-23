# Specification: Mandatory Core Database Subsystems (OraCLI 10G)

## 1. Objective
Provide a fully compliant, self-contained educational database system for OraCLI 10G that implements:
1. **DDL**: `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`, `TRUNCATE TABLE`, `RENAME`, `CREATE INDEX`, `DROP INDEX`, `CREATE VIEW`, `DROP VIEW`.
2. **DML**: `INSERT`, `UPDATE`, `DELETE`, `SELECT` with Oracle-style row feedback (`1 row created.`, `1 row updated.`, `1 row deleted.`).
3. **DCL**: Educational user privilege model (`GRANT`, `REVOKE` for `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `ALL` on tables to users with `ORA-01031: insufficient privileges` enforcement).
4. **TCL**: Real transaction management (`COMMIT`, `ROLLBACK`, `SAVEPOINT <name>`, `ROLLBACK TO <name>`).
5. **Advanced SELECT**: `WHERE`, `DISTINCT`, `ORDER BY` (ASC/DESC/multiple/alias), `GROUP BY` (with non-aggregate validation), `HAVING` (evaluated post-aggregation), `JOIN` (INNER, LEFT, CROSS, RIGHT via emulated rewrite), `UNION`, `INTERSECT`, `MINUS` (mapped to `EXCEPT`), `SUBQUERIES`.
6. **Aggregates**: `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`.
7. **Constraints & Cascade**: `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK`, `DEFAULT`, and `ON DELETE CASCADE` foreign keys.
8. **Views & Materialized Views**: Standard SQL views and educational materialized views with snapshot refresh (`REFRESH MATERIALIZED VIEW <name>`).
9. **SQL*Plus Client Commands**: `DESC` / `DESCRIBE`, `SHOW USER`, `SET`, `CLEAR`, `LIST`, `RUN`, `SPOOL`, `COLUMN`, `EXIT`, `QUIT`.
10. **Automated Lab Validation**: Test suites and web UI categories for all features.
11. **Compatibility Status**: Web UI matrix backed by automated test verifications.

---

## 2. Technical Architecture & Component Contracts

### 2.1 DDL & Constraints (`app/engine/translator.py`, `app/database/sqlite_adapter.py`)
- **Oracle Types**: `NUMBER`, `NUMBER(p,s)`, `VARCHAR2(size)`, `CHAR(size)`, `DATE`, `TIMESTAMP`, `CLOB`, `BLOB`, `INTEGER`, `FLOAT`.
- **Constraint Support**: Inline and out-of-line `PRIMARY KEY`, `FOREIGN KEY ... REFERENCES ... ON DELETE CASCADE`, `UNIQUE`, `NOT NULL`, `CHECK(...)`, `DEFAULT <val>`.
- **DDL Commands**:
  - `TRUNCATE TABLE <table>` -> Transpiled to `DELETE FROM <table>` (and resets sqlite_sequence if applicable) with feedback `Table truncated.`.
  - `ALTER TABLE <table> ADD/DROP/MODIFY/RENAME ...` -> Transpiled to SQLite supported `ALTER TABLE` or table rebuild for unsupported alterations.
  - `RENAME <table> TO <new_table>` -> Transpiled to `ALTER TABLE <table> RENAME TO <new_table>` with feedback `Table renamed.`.
  - `CREATE INDEX <idx> ON <table> (<col>)` -> `Index created.`.
  - `DROP INDEX <idx>` -> `Index dropped.`.
  - `CREATE VIEW <view> AS <select>` -> `View created.`.
  - `DROP VIEW <view>` -> `View dropped.`.

### 2.2 DML & Feedback Messages (`app/cli/formatter.py`, `app/engine/executor.py`)
- Standard feedback strings:
  - `INSERT`: `{n} row(s) created.`
  - `UPDATE`: `{n} row(s) updated.`
  - `DELETE`: `{n} row(s) deleted.` (plus cascade count if dependent rows removed)
  - `SELECT`: `{n} rows selected.` or formatted table.

### 2.3 Educational DCL System (`app/engine/dcl.py`, `app/database/sqlite_adapter.py`)
- Maintain a system catalog table `_oracli_privileges (grantee TEXT, privilege TEXT, table_name TEXT, grantor TEXT)`.
- Default `SYSTEM` user has full privileges.
- When executing DML on a table as a non-SYSTEM user, check `_oracli_privileges`.
- Raise `ORA-01031: insufficient privileges` if unauthorized.
- Support `GRANT <privs> ON <table> TO <user>` and `REVOKE <privs> ON <table> FROM <user>`.

### 2.4 Real Transaction Control (TCL) (`app/database/sqlite_adapter.py`)
- Active SQLite connection per session maintaining `autocommit=False`.
- `COMMIT` -> `connection.commit()` with feedback `Commit complete.`.
- `ROLLBACK` -> `connection.rollback()` with feedback `Rollback complete.`.
- `SAVEPOINT <name>` -> `SAVEPOINT <name>` executed in SQLite with feedback `Savepoint created.`.
- `ROLLBACK TO <name>` -> `ROLLBACK TO SAVEPOINT <name>` executed in SQLite with feedback `Rollback complete.`.

### 2.5 Advanced Querying & MINUS Transpilation (`app/engine/translator.py`)
- `MINUS` -> Transpiled to `EXCEPT` in SQLite.
- `GROUP BY` -> Verified for non-aggregate column selection.
- `HAVING` -> Verified to preserve aggregation filters.
- `JOIN` -> `INNER JOIN`, `LEFT JOIN`, `CROSS JOIN`, `FULL OUTER JOIN` / `RIGHT JOIN` emulation.

### 2.6 Materialized Views Layer (`app/engine/mviews.py`)
- System catalog `_oracli_mviews (mview_name TEXT PRIMARY KEY, query_sql TEXT, last_refreshed TIMESTAMP)`.
- `CREATE MATERIALIZED VIEW <name> AS <query>`: creates table snapshot `<name>` and registers SQL query.
- `REFRESH MATERIALIZED VIEW <name>`: truncates `<name>` and re-inserts fresh results from query.
- `DROP MATERIALIZED VIEW <name>`: drops `<name>` table and unregisters from `_oracli_mviews`.

### 2.7 DESCRIBE Engine (`app/cli/sqlplus_commands.py`, `app/engine/executor.py`)
- `DESC[RIBE] <table_or_view>`:
  ```text
  Name       Null?       Type
  ---------- ----------- ---------------
  ROLLNO     NOT NULL    NUMBER
  NAME       NOT NULL    VARCHAR2(50)
  CGPA                   NUMBER(3,2)
  ```

---

## 3. Verification & Acceptance Criteria
1. **MVP Acceptance Script**: The multi-table Department-Student lifecycle (DDL, Foreign Keys with CASCADE, DML, Aggregates, GROUP BY, HAVING, Views, Savepoints, Rollbacks, DCL Grant/Revoke) executes end-to-end without errors.
2. **Automated Test Suite**: 100% passing tests covering all 18 feature sections.
3. **Web UI Explorer & Lab**: Interactive UI reflecting live tables, views, materialized views, lab exercises, and live compatibility matrix.
