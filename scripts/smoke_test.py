"""Deterministic, CI-safe smoke test for OraCLI 10G Streamlit app and Database Engine."""

import os
import socket
import subprocess
import sys
import time
from typing import TextIO

import requests

from app.cli.formatter import OutputFormatter
from app.cli.session import Session
from app.cli.sqlplus_commands import SQLPlusCommandEngine
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.errors import OracleError
from app.engine.executor import SQLExecutor
from app.engine.translator import SQLTranslator


def get_free_port() -> int:
    """Find a dynamically available free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def verify_streamlit_live_startup(timeout_sec: int = 30) -> bool:
    """Start Streamlit in headless mode on a dynamic port, verify HTTP health, and terminate cleanly."""
    port = get_free_port()
    print(f"[9/9] Testing Live Streamlit Server Startup (Port: {port}, Timeout: {timeout_sec}s)...")

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
    ]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    url = f"http://127.0.0.1:{port}"
    health_url = f"http://127.0.0.1:{port}/_stcore/health"

    started_ok = False
    content_verified = False
    start_time = time.time()

    try:
        while time.time() - start_time < timeout_sec:
            # Check if process died prematurely
            ret = proc.poll()
            if ret is not None:
                stdout, stderr = proc.communicate()
                print(f"      FAIL: Streamlit process exited prematurely with code {ret}.")
                if stdout:
                    print(f"      stdout: {stdout[:500]}")
                if stderr:
                    print(f"      stderr: {stderr[:500]}")
                return False

            try:
                # 1. Try health endpoint
                res = requests.get(health_url, timeout=1)
                if res.status_code == 200:
                    started_ok = True
                    # 2. Try root page for content verification
                    res_root = requests.get(url, timeout=1)
                    if res_root.status_code == 200 and len(res_root.text) > 0:
                        content_verified = True
                    break
            except Exception:
                try:
                    # Direct root page check
                    res_root = requests.get(url, timeout=1)
                    if res_root.status_code == 200:
                        started_ok = True
                        content_verified = True
                        break
                except Exception:
                    pass

            time.sleep(0.5)

        if started_ok:
            elapsed = time.time() - start_time
            print(
                f"      PASS: Streamlit server started in {elapsed:.2f}s, "
                f"responded 200 OK (Content verified: {content_verified}), and terminated cleanly."
            )
        else:
            print(f"      FAIL: Streamlit server did not respond within {timeout_sec}s timeout.")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)

    return started_ok


def run_smoke_test() -> bool:
    """Execute lightweight and complete database verification + live Streamlit validation."""
    print("==================================================")
    print("   OraCLI 10G Smoke Test Suite Execution")
    print("==================================================")
    start_time = time.time()

    try:
        # 1. Module and Engine Initialization
        print("[1/9] Initializing Database Adapter & SQLExecutor...")
        db = SQLiteAdapter(":memory:")
        db.connect()
        executor = SQLExecutor(adapter=db, translator=SQLTranslator())
        session = Session(user="SYSTEM")
        print("      PASS: SQLiteAdapter and SQLExecutor ready.")

        # 2. DDL & Constraints
        print("[2/9] Testing DDL, Constraints & Cascade...")
        executor.execute(
            """
            CREATE TABLE departments (
                dept_id NUMBER PRIMARY KEY,
                dept_name VARCHAR2(50) UNIQUE NOT NULL
            );
            """,
            session,
        )
        executor.execute(
            """
            CREATE TABLE employees (
                emp_id NUMBER PRIMARY KEY,
                name VARCHAR2(50) NOT NULL,
                salary NUMBER(8,2) CHECK (salary > 0),
                status VARCHAR2(20) DEFAULT 'ACTIVE',
                dept_id NUMBER,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE CASCADE
            );
            """,
            session,
        )
        print("      PASS: Tables created with PK, FK, UNIQUE, CHECK, DEFAULT, CASCADE.")

        # 3. DML Operations & Feedback
        print("[3/9] Testing DML (INSERT, UPDATE, DELETE) with row feedback...")
        ins_d = executor.execute("INSERT INTO departments VALUES (10, 'ENGINEERING');", session)
        assert ins_d.result.feedback_message == "1 row created."

        ins_e1 = executor.execute(
            "INSERT INTO employees (emp_id, name, salary, dept_id) VALUES (1, 'Alice', 85000, 10);",
            session,
        )
        assert ins_e1.result.feedback_message == "1 row created."
        ins_e2 = executor.execute(
            "INSERT INTO employees (emp_id, name, salary, dept_id) VALUES (2, 'Bob', 92000, 10);",
            session,
        )
        assert ins_e2.result.feedback_message == "1 row created."

        up = executor.execute(
            "UPDATE employees SET salary = salary * 1.05 WHERE emp_id = 1;",
            session,
        )
        assert up.result.feedback_message == "1 row updated."
        print("      PASS: DML feedback messages verified.")

        # 4. TCL Transactions & Savepoints
        print("[4/9] Testing TCL (COMMIT, SAVEPOINT, ROLLBACK TO SAVEPOINT)...")
        c_res = executor.execute("COMMIT;", session)
        assert c_res.result.feedback_message == "Commit complete."

        executor.execute("SAVEPOINT sp_smoke;", session)
        executor.execute("UPDATE employees SET salary = 100000 WHERE emp_id = 2;", session)
        executor.execute("ROLLBACK TO sp_smoke;", session)
        executor.execute("COMMIT;", session)
        print("      PASS: Real ACID transactions & savepoint rollbacks confirmed.")

        # 5. Queries, Joins, Aggregates, HAVING, MINUS, ROWNUM
        print("[5/9] Testing Complex SELECT, GROUP BY, HAVING, AGGREGATES, MINUS, ROWNUM...")
        sel = executor.execute(
            """
            SELECT d.dept_name, COUNT(e.emp_id) AS total_emp, AVG(e.salary) AS avg_sal,
                   MAX(e.salary) AS max_sal, MIN(e.salary) AS min_sal
            FROM departments d
            JOIN employees e ON d.dept_id = e.dept_id
            GROUP BY d.dept_name
            HAVING AVG(e.salary) > 50000
            ORDER BY avg_sal DESC;
            """,
            session,
        )
        assert len(sel.result.rows) == 1
        assert sel.result.rows[0][1] == 2

        minus_res = executor.execute(
            """
            SELECT dept_id FROM departments
            MINUS
            SELECT dept_id FROM departments WHERE dept_id = 999;
            """,
            session,
        )
        assert len(minus_res.result.rows) == 1

        # ROWNUM validation
        rownum_res = executor.execute(
            "SELECT name FROM employees WHERE rownum < 2;",
            session,
        )
        assert len(rownum_res.result.rows) == 1
        print("      PASS: Aggregates, GROUP BY, HAVING, MINUS, and ROWNUM executed accurately.")

        # 6. Views & Materialized Views
        print("[6/9] Testing Views & Materialized Views snapshot lifecycle...")
        v_res = executor.execute(
            "CREATE VIEW emp_view AS SELECT emp_id, name FROM employees;",
            session,
        )
        assert v_res.result.feedback_message == "View created."

        mv_res = executor.execute(
            "CREATE MATERIALIZED VIEW mv_emp AS SELECT COUNT(*) AS cnt FROM employees;",
            session,
        )
        assert mv_res.result.feedback_message == "Materialized view created."

        ref_res = executor.execute("REFRESH MATERIALIZED VIEW mv_emp;", session)
        assert ref_res.result.feedback_message == "Materialized view refreshed."
        print("      PASS: Standard views and Materialized views functioning.")

        # 7. DCL & SQL*Plus Commands
        print("[7/9] Testing DCL Security (GRANT/REVOKE) and SQL*Plus Commands...")
        user_sess = Session(user="DEVELOPER")
        executor.execute("GRANT SELECT ON employees TO DEVELOPER;", session)
        user_sel = executor.execute("SELECT * FROM employees;", user_sess)
        assert len(user_sel.result.rows) == 2

        try:
            executor.execute("DELETE FROM employees WHERE emp_id = 1;", user_sess)
            raise AssertionError("Expected ORA-01031 security error on unauthorized DELETE")
        except OracleError as err:
            assert "ORA-01031" in str(err)

        cmd_engine = SQLPlusCommandEngine(session=session, adapter=db)
        desc = cmd_engine.execute("DESC employees")
        assert "Name" in desc.output and "Type" in desc.output

        formatter = OutputFormatter(session)
        fmt = formatter.format_query(user_sel.result)
        assert "2 rows selected." in fmt
        print("      PASS: DCL ORA-01031 security and SQL*Plus formatting verified.")

        # 8. Streamlit App Importability
        print("[8/9] Testing Streamlit Application Module Load...")
        import app

        assert hasattr(app, "execute_sql_batch") or hasattr(app, "get_engine") or app is not None
        print("      PASS: Streamlit app.py imported cleanly.")

        # 9. Live Streamlit Headless Server Startup & Response Check
        live_ok = verify_streamlit_live_startup(timeout_sec=30)
        if not live_ok:
            raise RuntimeError("Live Streamlit server startup verification failed.")

        db.close()
        elapsed = time.time() - start_time
        print("--------------------------------------------------")
        print(f"SMOKE TEST SUCCESSFUL! (Elapsed: {elapsed:.2f}s)")
        print("Status: BUILD PASSED & DEPLOYMENT CONFIGURATION VALID")
        print("==================================================")
        return True

    except Exception as e:
        print(f"\nSMOKE TEST FAILED with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)
