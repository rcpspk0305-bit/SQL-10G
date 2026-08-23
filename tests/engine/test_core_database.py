"""Comprehensive unit and integration test suite for mandatory core database features."""

import pytest

from app.cli.session import Session
from app.cli.sqlplus_commands import SQLPlusCommandEngine
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.errors import OracleError
from app.engine.executor import SQLExecutor
from app.engine.translator import SQLTranslator


@pytest.fixture
def db():
    """Create fresh in-memory SQLiteAdapter with system catalogs initialized."""
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()
    yield adapter
    adapter.close()


@pytest.fixture
def executor(db):
    """Create SQLExecutor."""
    return SQLExecutor(adapter=db, translator=SQLTranslator())


@pytest.fixture
def session():
    """Create SYSTEM session."""
    return Session(user="SYSTEM")


def test_ddl_and_dml_operations(executor, session):
    """Test CREATE TABLE, INSERT, UPDATE, DELETE, TRUNCATE, RENAME, DROP TABLE."""
    # 1. CREATE TABLE with Oracle types and constraints
    out1 = executor.execute(
        """
        CREATE TABLE student (
            rollno NUMBER PRIMARY KEY,
            name VARCHAR2(50) NOT NULL,
            cgpa NUMBER(3,2) CHECK (cgpa >= 0 AND cgpa <= 10)
        );
        """,
        session,
    )
    assert out1.result.feedback_message == "Table created."

    # 2. INSERT
    out2 = executor.execute("INSERT INTO student VALUES (101, 'Rahul', 8.7);", session)
    assert out2.result.feedback_message == "1 row created."

    # 3. UPDATE
    out3 = executor.execute("UPDATE student SET cgpa = 9.0 WHERE rollno = 101;", session)
    assert out3.result.feedback_message == "1 row updated."

    # 4. SELECT
    out4 = executor.execute("SELECT * FROM student;", session)
    assert out4.is_query is True
    assert len(out4.result.rows) == 1
    assert out4.result.rows[0][0] == 101

    # 5. RENAME TABLE
    out5 = executor.execute("RENAME student TO student_v2;", session)
    assert out5.result.feedback_message == "Table renamed."

    # 6. TRUNCATE TABLE
    out6 = executor.execute("TRUNCATE TABLE student_v2;", session)
    assert out6.result.feedback_message == "Table truncated."
    sel_empty = executor.execute("SELECT COUNT(*) FROM student_v2;", session)
    assert sel_empty.result.rows[0][0] == 0

    # 7. DROP TABLE
    out7 = executor.execute("DROP TABLE student_v2;", session)
    assert out7.result.feedback_message == "Table dropped."


def test_dcl_grant_and_revoke_privileges(executor, session):
    """Test educational DCL privilege model and ORA-01031 enforcement."""
    executor.execute("CREATE TABLE accounts (acc_id NUMBER PRIMARY KEY, balance NUMBER);", session)
    executor.execute("INSERT INTO accounts VALUES (1, 5000);", session)

    user1_session = Session(user="USER1")

    # Unauthorized access initially
    with pytest.raises(OracleError) as exc:
        executor.execute("SELECT * FROM accounts;", user1_session)
    assert "ORA-01031" in str(exc.value)

    with pytest.raises(OracleError) as exc:
        executor.execute("DELETE FROM accounts WHERE acc_id = 1;", user1_session)
    assert "ORA-01031" in str(exc.value)

    # GRANT SELECT
    grant_out = executor.execute("GRANT SELECT ON accounts TO USER1;", session)
    assert grant_out.result.feedback_message == "Grant succeeded."

    # USER1 can now SELECT
    sel_res = executor.execute("SELECT * FROM accounts;", user1_session)
    assert len(sel_res.result.rows) == 1

    # USER1 still cannot DELETE
    with pytest.raises(OracleError) as exc:
        executor.execute("DELETE FROM accounts WHERE acc_id = 1;", user1_session)
    assert "ORA-01031" in str(exc.value)

    # REVOKE SELECT
    rev_out = executor.execute("REVOKE SELECT ON accounts FROM USER1;", session)
    assert rev_out.result.feedback_message == "Revoke succeeded."

    # USER1 now blocked from SELECT again
    with pytest.raises(OracleError) as exc:
        executor.execute("SELECT * FROM accounts;", user1_session)
    assert "ORA-01031" in str(exc.value)


def test_tcl_transactions_and_savepoints(executor, session):
    """Test real transaction control: COMMIT, ROLLBACK, SAVEPOINT, ROLLBACK TO SAVEPOINT."""
    executor.execute("CREATE TABLE ledger (id NUMBER PRIMARY KEY, val VARCHAR2(20));", session)

    executor.execute("INSERT INTO ledger VALUES (1, 'Initial');", session)
    c_out = executor.execute("COMMIT;", session)
    assert c_out.result.feedback_message == "Commit complete."

    # Create savepoint, update, and rollback to savepoint
    sp_out = executor.execute("SAVEPOINT sp_before_update;", session)
    assert sp_out.result.feedback_message == "Savepoint created."

    executor.execute("UPDATE ledger SET val = 'Modified' WHERE id = 1;", session)
    check_mod = executor.execute("SELECT val FROM ledger WHERE id = 1;", session)
    assert check_mod.result.rows[0][0] == "Modified"

    rb_sp_out = executor.execute("ROLLBACK TO sp_before_update;", session)
    assert rb_sp_out.result.feedback_message == "Rollback complete."

    check_restored = executor.execute("SELECT val FROM ledger WHERE id = 1;", session)
    assert check_restored.result.rows[0][0] == "Initial"


def test_foreign_keys_and_on_delete_cascade(executor, session):
    """Test Foreign Key constraint with ON DELETE CASCADE."""
    executor.execute(
        """
        CREATE TABLE department (
            dept_id NUMBER PRIMARY KEY,
            dept_name VARCHAR2(50)
        );
        """,
        session,
    )
    executor.execute(
        """
        CREATE TABLE student (
            rollno NUMBER PRIMARY KEY,
            name VARCHAR2(50),
            dept_id NUMBER,
            FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE CASCADE
        );
        """,
        session,
    )

    executor.execute("INSERT INTO department VALUES (10, 'CSE');", session)
    executor.execute("INSERT INTO student VALUES (101, 'Rahul', 10);", session)
    executor.execute("INSERT INTO student VALUES (102, 'Priya', 10);", session)

    # Verify rows exist
    st_count = executor.execute("SELECT COUNT(*) FROM student WHERE dept_id = 10;", session)
    assert st_count.result.rows[0][0] == 2

    # DELETE department 10
    del_out = executor.execute("DELETE FROM department WHERE dept_id = 10;", session)
    assert del_out.result.feedback_message == "1 row deleted."

    # Check dependent students were cascade deleted
    st_count_after = executor.execute("SELECT COUNT(*) FROM student WHERE dept_id = 10;", session)
    assert st_count_after.result.rows[0][0] == 0


def test_views_and_materialized_views(executor, session):
    """Test standard VIEW and MATERIALIZED VIEW with snapshot refresh."""
    executor.execute("CREATE TABLE items (id NUMBER PRIMARY KEY, price NUMBER);", session)
    executor.execute("INSERT INTO items VALUES (1, 100);", session)
    executor.execute("INSERT INTO items VALUES (2, 200);", session)

    # 1. Standard VIEW
    v_sql = "CREATE VIEW expensive_items AS SELECT * FROM items WHERE price > 150;"
    v_out = executor.execute(v_sql, session)
    assert v_out.result.feedback_message == "View created."

    v_sel = executor.execute("SELECT * FROM expensive_items;", session)
    assert len(v_sel.result.rows) == 1
    assert v_sel.result.rows[0][0] == 2

    executor.execute("DROP VIEW expensive_items;", session)

    # 2. MATERIALIZED VIEW
    mv_sql = (
        "CREATE MATERIALIZED VIEW items_summary AS "
        "SELECT COUNT(*) AS cnt, SUM(price) AS total FROM items;"
    )
    mv_out = executor.execute(mv_sql, session)
    assert mv_out.result.feedback_message == "Materialized view created."

    mv_sel1 = executor.execute("SELECT cnt, total FROM items_summary;", session)
    assert mv_sel1.result.rows[0][0] == 2
    assert mv_sel1.result.rows[0][1] == 300

    # Insert new row into base table
    executor.execute("INSERT INTO items VALUES (3, 300);", session)

    # Before refresh, snapshot still shows 2 rows / 300 total
    mv_sel2 = executor.execute("SELECT cnt, total FROM items_summary;", session)
    assert mv_sel2.result.rows[0][0] == 2

    # REFRESH MATERIALIZED VIEW
    ref_out = executor.execute("REFRESH MATERIALIZED VIEW items_summary;", session)
    assert ref_out.result.feedback_message == "Materialized view refreshed."

    # After refresh, snapshot reflects 3 rows / 600 total
    mv_sel3 = executor.execute("SELECT cnt, total FROM items_summary;", session)
    assert mv_sel3.result.rows[0][0] == 3
    assert mv_sel3.result.rows[0][1] == 600

    # DROP MATERIALIZED VIEW
    drop_mv_out = executor.execute("DROP MATERIALIZED VIEW items_summary;", session)
    assert drop_mv_out.result.feedback_message == "Materialized view dropped."


def test_select_advanced_features(executor, session):
    """Test WHERE, GROUP BY, HAVING, ORDER BY, Aggregates, and MINUS."""
    executor.execute(
        """
        CREATE TABLE scores (
            sid NUMBER PRIMARY KEY,
            subject VARCHAR2(30),
            marks NUMBER
        );
        """,
        session,
    )
    executor.execute("INSERT INTO scores VALUES (1, 'Math', 95);", session)
    executor.execute("INSERT INTO scores VALUES (2, 'Math', 85);", session)
    executor.execute("INSERT INTO scores VALUES (3, 'Physics', 75);", session)
    executor.execute("INSERT INTO scores VALUES (4, 'Physics', 65);", session)

    # GROUP BY and HAVING with AGGREGATES
    agg_res = executor.execute(
        """
        SELECT subject, COUNT(*) AS cnt, AVG(marks) AS avg_marks,
               MAX(marks) AS max_marks, MIN(marks) AS min_marks
        FROM scores
        GROUP BY subject
        HAVING AVG(marks) >= 80
        ORDER BY avg_marks DESC;
        """,
        session,
    )
    assert len(agg_res.result.rows) == 1
    assert agg_res.result.rows[0][0] == "Math"
    assert agg_res.result.rows[0][1] == 2
    assert agg_res.result.rows[0][2] == 90.0

    # MINUS operator (Oracle MINUS -> SQLite EXCEPT)
    minus_res = executor.execute(
        """
        SELECT subject FROM scores WHERE marks > 70
        MINUS
        SELECT subject FROM scores WHERE marks > 90;
        """,
        session,
    )
    assert len(minus_res.result.rows) == 1
    assert minus_res.result.rows[0][0] == "Physics"


def test_sqlplus_describe_command(db, session):
    """Test SQL*Plus DESCRIBE command formatting."""
    executor = SQLExecutor(db)
    executor.execute(
        """
        CREATE TABLE test_desc (
            rollno NUMBER PRIMARY KEY,
            name VARCHAR2(50) NOT NULL,
            cgpa NUMBER(3,2)
        );
        """,
        session,
    )
    cmd_engine = SQLPlusCommandEngine(session=session, adapter=db)
    desc_res = cmd_engine.execute("DESC test_desc")
    assert "Name" in desc_res.output
    assert "Null?" in desc_res.output
    assert "Type" in desc_res.output
    assert "ROLLNO" in desc_res.output
    assert "NOT NULL" in desc_res.output
    assert "NUMBER" in desc_res.output


def test_mvp_acceptance_criteria_end_to_end(executor, session):
    """Execute the mandatory full MVP Acceptance multi-table scenario."""
    # 1. DDL
    executor.execute(
        """
        CREATE TABLE department (
            dept_id NUMBER PRIMARY KEY,
            dept_name VARCHAR2(50) UNIQUE
        );
        """,
        session,
    )
    executor.execute(
        """
        CREATE TABLE student (
            rollno NUMBER PRIMARY KEY,
            name VARCHAR2(50) NOT NULL,
            cgpa NUMBER(3,2),
            dept_id NUMBER,
            FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE CASCADE
        );
        """,
        session,
    )

    # 2. DML
    executor.execute("INSERT INTO department VALUES (10, 'CSE');", session)
    executor.execute("INSERT INTO department VALUES (20, 'ECE');", session)

    executor.execute("INSERT INTO student VALUES (101, 'Rahul', 8.7, 10);", session)
    executor.execute("INSERT INTO student VALUES (102, 'Priya', 9.1, 10);", session)
    executor.execute("INSERT INTO student VALUES (103, 'Arjun', 7.8, 20);", session)

    # 3. TCL COMMIT
    executor.execute("COMMIT;", session)

    # 4. SELECT with ORDER BY
    s_order = executor.execute("SELECT * FROM student ORDER BY cgpa DESC;", session)
    assert len(s_order.result.rows) == 3
    assert s_order.result.rows[0][1] == "Priya"

    # 5. AGGREGATES, GROUP BY, HAVING
    agg_res = executor.execute(
        """
        SELECT dept_id,
               COUNT(*) AS total_students,
               AVG(cgpa) AS average_cgpa,
               MAX(cgpa) AS highest_cgpa,
               MIN(cgpa) AS lowest_cgpa
        FROM student
        GROUP BY dept_id
        HAVING AVG(cgpa) > 8
        ORDER BY average_cgpa DESC;
        """,
        session,
    )
    assert len(agg_res.result.rows) == 1
    assert agg_res.result.rows[0][0] == 10

    # 6. VIEW
    v_res = executor.execute(
        """
        CREATE VIEW topper_view AS
        SELECT rollno, name, cgpa
        FROM student
        WHERE cgpa >= 8.5;
        """,
        session,
    )
    assert v_res.result.feedback_message == "View created."

    v_sel = executor.execute("SELECT * FROM topper_view;", session)
    assert len(v_sel.result.rows) == 2

    # 7. SAVEPOINT, DELETE, ROLLBACK TO SAVEPOINT, COMMIT
    executor.execute("SAVEPOINT before_delete;", session)
    executor.execute("DELETE FROM department WHERE dept_id = 10;", session)

    # Confirm dependent students cascade deleted
    st_count = executor.execute("SELECT COUNT(*) FROM student;", session)
    assert st_count.result.rows[0][0] == 1

    # Rollback to savepoint restores data
    executor.execute("ROLLBACK TO before_delete;", session)
    st_count_restored = executor.execute("SELECT COUNT(*) FROM student;", session)
    assert st_count_restored.result.rows[0][0] == 3

    executor.execute("COMMIT;", session)

    # 8. DCL GRANT & REVOKE
    g_res = executor.execute("GRANT SELECT ON student TO student_user;", session)
    assert g_res.result.feedback_message == "Grant succeeded."

    r_res = executor.execute("REVOKE SELECT ON student FROM student_user;", session)
    assert r_res.result.feedback_message == "Revoke succeeded."
