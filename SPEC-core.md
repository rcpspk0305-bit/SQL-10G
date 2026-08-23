# Spec: OraCLI 10G Core Foundation (First Task)

## Objective
Build a lightweight, local, educational CLI that reproduces the Oracle SQL*Plus 10g interactive shell experience.
Users (students/instructors) can start `python main.py`, see the SQL*Plus banner and `SQL>` prompt, input multiline SQL statements, execute DDL (`CREATE TABLE`), DML (`INSERT`, `SELECT`), receive Oracle SQL*Plus formatted tabular output and feedback strings (e.g. `Table created.`, `1 row created.`, `2 rows selected.`), and exit cleanly via `EXIT` or `QUIT`.

## Tech Stack
- **Language**: Python 3.12+ (tested with Python 3.14)
- **CLI/Display**: `rich`
- **SQL Parsing/Transpilation**: `sqlglot` + Custom Oracle Preprocessor / AST Transformer
- **Storage Engine**: SQLite (`sqlite3` standard library)
- **Testing**: `pytest`
- **Linter/Formatter**: `ruff`

## Commands
- **Run CLI**: `python main.py`
- **Run Tests**: `pytest`
- **Run Linter**: `ruff check .`
- **Format Code**: `ruff format .`

## Project Structure
```
oracli/
├── app/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── terminal.py         # Interactive terminal loop, input handling
│   │   ├── command_router.py   # Routes input to SQL or SQL*Plus handler
│   │   ├── sqlplus_commands.py # Handles EXIT, QUIT, etc.
│   │   ├── formatter.py        # Oracle SQL*Plus table & feedback formatting
│   │   └── session.py          # Session configuration & state
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── sql_parser.py       # SQLGlot integration & dialect parsing
│   │   ├── sqlplus_parser.py   # SQL*Plus command parser
│   │   └── buffer.py           # Multiline SQL & PL/SQL buffer tracker
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── executor.py         # Execution coordinator
│   │   ├── translator.py       # Oracle-to-SQLite SQL transpiler
│   │   ├── oracle_types.py     # Oracle datatype mappings
│   │   ├── functions.py        # Oracle function emulation
│   │   └── errors.py           # Error mapper (SQLite -> ORA-xxxxx)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── adapter.py          # Abstract database adapter
│   │   ├── sqlite_adapter.py   # SQLite concrete implementation
│   │   ├── connection.py       # Connection management
│   │   └── metadata.py         # Metadata extraction
│   └── config/
│       ├── __init__.py
│       └── settings.py         # Settings & defaults
├── tests/
│   ├── __init__.py
│   ├── cli/
│   │   ├── test_buffer.py
│   │   ├── test_formatter.py
│   │   └── test_command_router.py
│   ├── engine/
│   │   ├── test_translator.py
│   │   └── test_errors.py
│   ├── database/
│   │   └── test_sqlite_adapter.py
│   └── integration/
│       └── test_end_to_end.py
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── architecture.md
│   └── compatibility.md
└── main.py
```

## Code Style
- PEP 8 compliant, formatted with `ruff format`.
- Strict typing with type annotations on all public functions/methods.
- Clean separation between presentation (`cli`), routing (`command_router`), compilation (`engine/translator`), and persistence (`database`).

## Testing Strategy
- Unit tests for multiline statement parsing (semicolons in strings vs statement terminator).
- Unit tests for SQL translator (Oracle types `NUMBER`, `VARCHAR2`, `DATE` mapping to SQLite equivalents).
- Unit tests for SQL*Plus output formatter (header uppercase, dash underline length equal to column width, right-aligned numbers, left-aligned strings).
- Integration test executing:
  1. `CREATE TABLE student (rollno NUMBER, name VARCHAR2(50), cgpa NUMBER(3,2));`
  2. `INSERT INTO student VALUES (101, 'Rahul', 8.7);`
  3. `SELECT * FROM student;`
  Verifying real SQLite table creation, row insertion, and query output matching SQL*Plus.

## Boundaries
- **Always do**: Transpile Oracle DDL/DML accurately; quote-aware multiline collection; test every module.
- **Ask first**: Adding new third-party dependencies outside `sqlglot`, `rich`, `pytest`, `ruff`.
- **Never do**: Fake SQL execution with string templating; leak raw SQLite internal exceptions to user; execute unsafe shell commands.

## Success Criteria
1. `pytest` passes with 100% success across all unit and integration tests.
2. `ruff check .` reports 0 errors.
3. Interactive execution of `python main.py` supports:
   - SQL*Plus 10g header banner.
   - `SQL>` multiline editing with numbered line continuation prompt (`  2  `).
   - `CREATE TABLE student (...)`, `INSERT INTO student ...`, `SELECT * FROM student`.
   - Formatted output with right-aligned numbers, left-aligned strings, dashed column lines, row feedback (`Table created.`, `1 row created.`, `1 row selected.`).
   - `EXIT` / `QUIT` cleanly terminating session.
