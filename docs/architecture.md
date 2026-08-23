# Architecture: OraCLI 10G

## System Architecture Overview

OraCLI 10G is organized into distinct decoupled layers following SOLID principles and clean separation of concerns:

```
                  +-----------------------------------+
                  |   SQL*Plus-Compatible Terminal    |
                  |          (app.cli.terminal)       |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |      Multiline Input Buffer       |
                  |          (app.parser.buffer)      |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |          Command Router           |
                  |     (app.cli.command_router)      |
                  +--------+-----------------+--------+
                           |                 |
            +--------------+                 +--------------+
            | (SQL*Plus Command)                            | (SQL / DDL / DML)
            v                                               v
+-----------+-----------+                       +-----------+-----------+
|  SQL*Plus Command     |                       |     SQL Translator    |
|       Engine          |                       | (Oracle SQL -> SQLite)|
| (app.cli.sqlplus_cmds)|                       | (app.engine.translator|
+-----------+-----------+                       +-----------+-----------+
            |                                               |
            |                                               v
            |                                   +-----------+-----------+
            |                                   |  Execution Coordinator|
            |                                   | (app.engine.executor) |
            |                                   +-----------+-----------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |     Database Adapter (SQLite)     |
                  |   (app.database.sqlite_adapter)   |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |   Output Formatter / Error Mapper |
                  |   (app.cli.formatter / errors)    |
                  +-----------------------------------+
```

## Core Components

1. **Terminal (`app.cli.terminal`)**:
   - Manages interactive REPL session, SQL*Plus banner, primary `SQL>` prompt, and continuation line prompts `  2  `, `  3  `.
2. **Buffer (`app.parser.buffer`)**:
   - Parses multi-line input while being string-literal and comment aware (handles quotes, semicolons inside strings, block comments `/* */`, single-line comments `--`).
3. **Command Router (`app.cli.command_router`)**:
   - Detects whether an input is a SQL*Plus command (e.g. `EXIT`, `QUIT`, `SET`, `SHOW`, `DESC`) or a SQL statement.
4. **SQL Translator (`app.engine.translator`)**:
   - Converts Oracle SQL dialect into SQLite executable SQL via `sqlglot` and custom AST transformations.
   - Maps Oracle datatypes (`NUMBER`, `VARCHAR2`, `DATE`, `TIMESTAMP`, etc.) to SQLite equivalents.
5. **Database Adapter (`app.database.sqlite_adapter`)**:
   - Encapsulates SQLite connection lifecycle, transaction commits/rollbacks, and query execution.
6. **Output Formatter (`app.cli.formatter`)**:
   - Renders tabular results with uppercase column headings, exact underline dash lengths, right-aligned numbers, left-aligned strings, and Oracle feedback messages (`Table created.`, `N rows selected.`).
7. **Error Mapper (`app.engine.errors`)**:
   - Maps SQLite errors into canonical Oracle `ORA-xxxxx` codes and descriptions.
