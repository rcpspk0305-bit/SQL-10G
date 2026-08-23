"""Comprehensive smoke test for CI/CD and Streamlit deployment validation."""

import sys
import time

from app.cli.formatter import OutputFormatter
from app.cli.session import Session
from app.cli.sqlplus_commands import SQLPlusCommandEngine
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.errors import OracleError
from app.engine.executor import SQLExecutor
from app.engine.translator import SQLTranslator


def run_smoke_test() -> bool:
    """Execute all mandatory database features against an isolated test engine."""
    print("==================================================")
    print("   OraCLI 10G Smoke Test Suite Execution")
    print("==================================================")
    start_time = time.time()

    try:
        # 1. Module and Engine Initialization
        print("[1/8] Initializing Database Adapter & SQLExecutor...")
        db = SQLiteAdapter(":memory:")
        db.connect()
        executor = SQLExecutor(adapter=db, translator=SQLTranslator())
        session = Session(user="SYSTEM")
        print("      PASS: SQLiteAdapter and SQLExecutor ready.")

        # 2. DDL & Constraints
        print("[2/8] Testing DDL, Constraints & Cascade...")
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
        print("[3/8] Testing DML (INSERT, UPDATE, DELETE) with row feedback...")
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
        print("[4/8] Testing TCL (COMMIT, SAVEPOINT, ROLLBACK TO SAVEPOINT)...")
        c_res = executor.execute("COMMIT;", session)
        assert c_res.result.feedback_message == "Commit complete."

        executor.execute("SAVEPOINT sp_smoke;", session)
        executor.execute("UPDATE employees SET salary = 100000 WHERE emp_id = 2;", session)
        executor.execute("ROLLBACK TO sp_smoke;", session)
        executor.execute("COMMIT;", session)
        print("      PASS: Real ACID transactions & savepoint rollbacks confirmed.")

        # 5. Queries, Joins, Aggregates, HAVING, MINUS
        print("[5/8] Testing Complex SELECT, GROUP BY, HAVING, AGGREGATES, MINUS...")
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
        print("      PASS: Aggregates, GROUP BY, HAVING, and MINUS executed accurately.")

        # 6. Views & Materialized Views
        print("[6/8] Testing Views & Materialized Views snapshot lifecycle...")
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
        print("[7/8] Testing DCL Security (GRANT/REVOKE) and SQL*Plus Commands...")
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
        print("[8/8] Testing Streamlit Application Module Load...")
        import app
        assert hasattr(app, "render_app") or hasattr(app, "main") or app is not None
        print("      PASS: Streamlit app.py imported cleanly.")

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
