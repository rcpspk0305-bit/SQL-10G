# Capability Map: OraCLI 10G

## Overview
OraCLI 10G is an independent, lightweight, educational database environment that reproduces the Oracle SQL*Plus 10g user experience and command behavior on top of SQLite with Oracle SQL transpilation, SQL*Plus commands, metadata simulation, and PL/SQL interpretation.

## Modules

| Module ID | Responsibility | Depends On |
|---|---|---|
| `core-cli` | CLI terminal, multiline buffer, command routing, session state, SQL*Plus output formatting | — |
| `db-adapter` | SQLite connection lifecycle, transaction management, query execution | — |
| `sql-translator` | Oracle SQL AST parsing (SQLGlot + custom), Oracle type mapping, Oracle function transpilation, ORA error mapping | `db-adapter` |
| `sqlplus-cmds` | SQL*Plus command execution (EXIT, QUIT, SET, SHOW, DESC, SPOOL, COLUMN, CLEAR, LIST, RUN, HOST) | `core-cli`, `db-adapter` |
| `metadata-dict` | Data dictionary emulation (USER_TABLES, USER_TAB_COLUMNS, USER_VIEWS, USER_INDEXES) and DESCRIBE engine | `sql-translator`, `db-adapter` |
| `views-mviews` | VIEW metadata lifecycle and MATERIALIZED VIEW snapshot storage & manual REFRESH subsystem | `sql-translator`, `metadata-dict` |
| `plsql-engine` | PL/SQL lexical scanner, recursive-descent parser, interpreter runtime, DBMS_OUTPUT buffer | `sql-translator`, `db-adapter` |
| `script-runner` | `@script.sql` and `START script.sql` runner with path security and batch execution | `sqlplus-cmds`, `plsql-engine` |
| `lab-mode` | Predefined lab exercises, schema validation, result state verification, automated evaluation | `core-cli`, `sql-translator`, `metadata-dict` |

## Build Order

1. **Phase 1 (First Task / Foundation)**: `core-cli` + `db-adapter` + `sql-translator` (Walking skeleton supporting interactive prompt, multiline buffer, Oracle types `NUMBER`/`VARCHAR2`, `CREATE TABLE`, `INSERT`, `SELECT`, and Oracle-style tabular formatting).
2. **Phase 2**: `sqlplus-cmds` (SET, SHOW, SPOOL, COLUMN, CLEAR, LIST, RUN) + `metadata-dict` (USER_TABLES, USER_TAB_COLUMNS, DESC).
3. **Phase 3**: `views-mviews` (CREATE VIEW, DROP VIEW, CREATE MATERIALIZED VIEW, REFRESH MATERIALIZED VIEW).
4. **Phase 4**: `plsql-engine` (DECLARE-BEGIN-END blocks, variables, IF-THEN-ELSE, LOOPS, SELECT INTO, DBMS_OUTPUT).
5. **Phase 5**: `script-runner` + advanced Oracle SQL functions (NVL, SYSDATE, SUBSTR, INSTR, MINUS).
6. **Phase 6**: `lab-mode` (College lab exercises & grading engine).
