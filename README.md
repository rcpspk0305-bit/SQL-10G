# OraCLI 10G

**Oracle 10g SQL\*Plus-Compatible Educational Database Environment**

OraCLI 10G is a lightweight, local, offline educational tool designed for database laboratory practice and college coursework. It reproduces the authentic command behavior, multiline prompts, Oracle SQL subset, datatypes, and formatted table output of Oracle SQL*Plus 10g using an independent Python architecture and SQLite storage engine.

---

## Key Features

- **SQL\*Plus Interactive Terminal**: True SQL*Plus experience with banner, `SQL>` prompt, continuation line numbering (`  2  `, `  3  `), and semicolon/slash completion.
- **Oracle Datatype Emulation**: Native parsing of Oracle types including `NUMBER`, `NUMBER(p,s)`, `VARCHAR2(size)`, `CHAR(size)`, `DATE`, `TIMESTAMP`, `CLOB`, `BLOB`, `INTEGER`.
- **Oracle SQL Subset**: Full support for DDL (`CREATE TABLE`, `DROP TABLE`, `ALTER TABLE`, `TRUNCATE TABLE`) and DML (`INSERT`, `SELECT`, `UPDATE`, `DELETE`).
- **SQL\*Plus Client Commands**: `EXIT`, `QUIT`, `SHOW USER`, `SET PAGESIZE`, `SET LINESIZE`, `SET HEADING`, `SET FEEDBACK`, `SET NULL`, `CLEAR SCREEN`.
- **Authentic Formatted Output**: Uppercase table headers, exact underline dashes, right-aligned numeric data, left-aligned strings, and feedback messages (`Table created.`, `1 row created.`, `N rows selected.`).
- **Oracle Error Mapping**: Translates internal database errors into standard Oracle codes (`ORA-00942`, `ORA-00904`, `ORA-00001`, `ORA-01400`, `ORA-00933`).

---

## Quickstart

### Prerequisites
- Python 3.12+

### Installation & Execution

```bash
# Clone the repository
git clone https://github.com/yourusername/oracli.git
cd oracli

# Create virtual environment & install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Launch SQL*Plus terminal
python main.py
```

### Example Session

```sql
SQL*Plus: Release 10.2 Compatible Educational Edition

Connected to:
OraCLI 10G Database Release 10.2.0.1.0 - Educational Edition

SQL> CREATE TABLE student (
  2  rollno NUMBER,
  3  name VARCHAR2(50),
  4  cgpa NUMBER(3,2)
  5  );

Table created.

SQL> INSERT INTO student VALUES (101, 'Rahul', 8.7);

1 row created.

SQL> SELECT * FROM student;

    ROLLNO NAME                 CGPA
---------- -------------------- -----
       101 Rahul                8.70

1 row selected.

SQL> EXIT
Disconnected from Oracle Database.
```

---

## Testing & Quality

```bash
# Run test suite
pytest

# Run linter
ruff check .
```

---

## Architecture & Roadmap

For deep dives into the project design, please check:
- [CAPABILITY-MAP.md](CAPABILITY-MAP.md) - Initiative decomposition and build order.
- [SPEC-core.md](SPEC-core.md) - Core engine specification.
- [docs/architecture.md](docs/architecture.md) - Architectural design & subsystem pipeline.
- [docs/compatibility.md](docs/compatibility.md) - Oracle 10g compatibility matrix.
