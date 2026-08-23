# OraCLI 10G Web

**Oracle 10g SQL\*Plus-Compatible Educational Web Environment & CLI**

OraCLI 10G is an independent, lightweight, browser-based and command-line educational database platform built specifically for university database laboratory coursework, examination preparation, and Oracle SQL skill development.

It reproduces the authentic command behavior, multiline prompts, Oracle SQL subset, datatypes, and formatted table output of **Oracle SQL\*Plus 10g** using an independent Python + FastAPI backend and React + TypeScript frontend on top of a local SQLite engine.

---

## 🌟 Key Features

- **🌐 SQL\*Plus Web Console (`/console`)**:
  - Full-featured SQL editor with multiline editing, line numbering, syntax hints, and `Ctrl+Enter` shortcut to run.
  - Authentic SQL*Plus monospace terminal output (uppercase headers, dashed underlines, right-aligned numbers, left-aligned strings, and feedback messages).
  - Dual view toggle: switch between **SQL*Plus Monospace Text** and interactive **Tabular Data Grid**.
- **📊 Database Explorer (`/tables`)**:
  - Visual schema inspector displaying user tables, columns, Oracle datatype representations, Primary Key indicators, and row counts.
  - Quick query generators (`SELECT *`, `DESC <table_name>`).
- **🎓 College Lab & Exam Mode (`/lab`)**:
  - Pre-loaded university laboratory exercises (DDL, Constraints, DML, Joins, Aggregates, Views).
  - Practice mode with step-by-step hints and timed Exam Mode with automated state validation.
- **📜 SQL Scripts Library (`/scripts`)**:
  - Pre-packaged schema scripts (`student_schema.sql`, `employee_dept.sql`) with download and one-click execution.
- **⚡ PL/SQL Workspace (`/plsql`)**:
  - Anonymous blocks (`DECLARE ... BEGIN ... END; /`), variables, and `DBMS_OUTPUT` capture buffer.
- **🕒 Query History (`/history`)**:
  - Audit log of executed statements with timestamps, execution duration, and instant re-run button.
- **🗃️ Oracle Datatype Emulation**:
  - Native parsing of `NUMBER`, `NUMBER(p,s)`, `VARCHAR2(size)`, `CHAR(size)`, `DATE`, `TIMESTAMP`, `CLOB`, `BLOB`, `INTEGER`.
- **🧮 Oracle Functions**:
  - `NVL`, `SYSDATE`, `UPPER`, `LOWER`, `LENGTH`, `SUBSTR`, `INSTR`, `ROUND`, `TRUNC`, `MOD`.
- **🚨 Canonical Oracle Error Codes**:
  - Maps database errors into standard Oracle codes (`ORA-00942`, `ORA-00904`, `ORA-00001`, `ORA-01400`, `ORA-00933`, `ORA-00955`).

---

## 🚀 Quickstart

### Prerequisites
- **Python**: 3.12+
- **Node.js**: 18+ (for frontend development)

### 1. Installation & Environment Setup

```bash
# Clone the repository
git clone https://github.com/rcpspk0305-bit/SQL-10G.git
cd SQL-10G

# Create and activate Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install backend dependencies
pip install -e .
```

---

### 2. Launching the Web Application (Recommended)

Start the unified server that hosts both the REST API and the React web application on port 8000:

```bash
python -m uvicorn app.api.server:app --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

### 3. Launching in Terminal REPL Mode

If you prefer the classic command-line SQL*Plus shell:

```bash
python main.py
```

**Example Terminal Session:**

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

## 🛠️ Frontend Development Mode (Vite Hot-Reload)

To run the frontend with hot-module reloading during development:

```bash
# Terminal 1: Start FastAPI backend
python -m uvicorn app.api.server:app --port 8000 --reload

# Terminal 2: Start Vite dev server
cd web
npm run dev
```

Navigate to: **`http://localhost:5173`**

To compile the production frontend bundle:

```bash
cd web
npm run build
```

---

## 🧪 Testing & Code Quality

```bash
# Run full automated test suite (27 passing tests)
pytest

# Run linter
ruff check .

# Format code
ruff format .
```

---

## 📚 Documentation & Architecture

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture, subsystem pipeline, and data flow.
- [ROADMAP.md](ROADMAP.md) — Project milestones and capabilities.
- [COMPATIBILITY.md](COMPATIBILITY.md) — Oracle 10g SQL & SQL*Plus compatibility matrix.
- [CAPABILITY-MAP.md](CAPABILITY-MAP.md) — Module decomposition and dependency graph.
- [CHANGELOG.md](CHANGELOG.md) — Version history and release notes.

---

## 📄 License

This is an educational open-source project designed for learning database concepts. It is an independent implementation and is not affiliated with or endorsed by Oracle Corporation.
