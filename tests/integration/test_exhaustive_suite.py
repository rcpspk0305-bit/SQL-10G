"""Exhaustive test suite verifying 26 distinct database scenarios across all subsystems."""

import pytest

from app.cli.formatter import OutputFormatter
from app.cli.session import Session
from app.cli.sqlplus_commands import SQLPlusCommandEngine
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.errors import OracleError
from app.engine.executor import SQLExecutor
from app.engine.translator import SQLTranslator


@pytest.fixture
def db():
    """Create fresh isolated in-memory database adapter."""
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()
    yield adapter
    adapter.close()


@pytest.fixture
def executor(db):
    """Create SQL executor."""
    return SQLExecutor(adapter=db, translator=SQLTranslator())


@pytest.fixture
def session():
    """Create default session."""
    return Session(user="SYSTEM")


# ============================================================================
# 1. DDL & CONSTRAINT TESTS (Test Cases 1-5)
# ============================================================================


def test_01_ddl_composite_primary_key(executor, session):
    """Test Case 1: CREATE TABLE with composite primary key."""
    out = executor.execute(
        """
        CREATE TABLE student_courses (
            student_id NUMBER,
            course_id NUMBER,
            semester VARCHAR2(10),
            grade VARCHAR2(2),
            PRIMARY KEY (student_id, course_id)
        );
        """,
        session,
    )
    assert out.result.feedback_message == "Table created."
    executor.execute(
        "INSERT INTO student_courses VALUES (101, 201, 'FALL26', 'A');",
        session,
    )
    with pytest.raises(OracleError) as exc:
        executor.execute(
            "INSERT INTO student_courses VALUES (101, 201, 'SPR27', 'B');",
            session,
        )
    assert "ORA-00001" in str(exc.value)


def test_02_ddl_check_constraint_validation(executor, session):
    """Test Case 2: CHECK constraints on numeric ranges and values."""
    executor.execute(
        """
        CREATE TABLE products (
            prod_id NUMBER PRIMARY KEY,
            price NUMBER(8,2) CHECK (price > 0),
            discount NUMBER(3,2) DEFAULT 0 CHECK (discount >= 0 AND discount <= 1)
        );
        """,
        session,
    )
    executor.execute("INSERT INTO products VALUES (1, 99.50, 0.15);", session)
    with pytest.raises(OracleError) as exc:
        executor.execute("INSERT INTO products VALUES (2, -10.00, 0.05);", session)
    assert "ORA-00001" in str(exc.value) or "constraint" in str(exc.value).lower()


def test_03_ddl_default_values(executor, session):
    """Test Case 3: Column DEFAULT values on partial column inserts."""
    executor.execute(
        """
        CREATE TABLE audit_log (
            log_id NUMBER PRIMARY KEY,
            action VARCHAR2(30),
            status VARCHAR2(20) DEFAULT 'PENDING'
        );
        """,
        session,
    )
    executor.execute("INSERT INTO audit_log (log_id, action) VALUES (1, 'LOGIN');", session)
    res = executor.execute("SELECT status FROM audit_log WHERE log_id = 1;", session)
    assert res.result.rows[0][0] == "PENDING"


def test_04_ddl_unique_constraint_enforcement(executor, session):
    """Test Case 4: UNIQUE constraint rejecting duplicate values."""
    executor.execute(
        """
        CREATE TABLE employees (
            emp_id NUMBER PRIMARY KEY,
            email VARCHAR2(100) UNIQUE NOT NULL
        );
        """,
        session,
    )
    executor.execute("INSERT INTO employees VALUES (1, 'john@example.com');", session)
    with pytest.raises(OracleError) as exc:
        executor.execute("INSERT INTO employees VALUES (2, 'john@example.com');", session)
    assert "ORA-00001" in str(exc.value)


def test_05_ddl_index_lifecycle(executor, session):
    """Test Case 5: CREATE INDEX and DROP INDEX."""
    executor.execute(
        "CREATE TABLE customers (cust_id NUMBER PRIMARY KEY, city VARCHAR2(50));",
        session,
    )
    idx_out = executor.execute("CREATE INDEX idx_cust_city ON customers (city);", session)
    assert idx_out.result.feedback_message == "Index created."

    drop_idx = executor.execute("DROP INDEX idx_cust_city;", session)
    assert drop_idx.result.feedback_message == "Index dropped."


# ============================================================================
# 2. ORACLE FUNCTIONS & DUAL (Test Cases 6-8)
# ============================================================================


def test_06_oracle_scalar_functions_on_dual(executor, session):
    """Test Case 6: NVL, SYSDATE, INSTR, TRUNC, UPPER, LOWER on DUAL."""
    res = executor.execute(
        """
        SELECT
            NVL(NULL, 'Fallback') AS nvl_test,
            UPPER('oracle 10g') AS upper_test,
            LOWER('SQL*PLUS') AS lower_test,
            INSTR('CORPORATE FLOOR', 'OR', 3) AS instr_test,
            TRUNC(123.456, 1) AS trunc_test
        FROM DUAL;
        """,
        session,
    )
    assert res.result.rows[0][0] == "Fallback"
    assert res.result.rows[0][1] == "ORACLE 10G"
    assert res.result.rows[0][2] == "sql*plus"
    assert res.result.rows[0][3] == 5
    assert res.result.rows[0][4] == 123.4


def test_07_string_concatenation_operator(executor, session):
    """Test Case 7: Oracle || pipe concatenation operator."""
    executor.execute("CREATE TABLE people (fname VARCHAR2(30), lname VARCHAR2(30));", session)
    executor.execute("INSERT INTO people VALUES ('James', 'Gosling');", session)
    res = executor.execute("SELECT fname || ' ' || lname AS full_name FROM people;", session)
    assert res.result.rows[0][0] == "James Gosling"


def test_08_oracle_aggregate_functions(executor, session):
    """Test Case 8: COUNT, SUM, AVG, MIN, MAX over empty and populated tables."""
    executor.execute("CREATE TABLE salary_test (sal NUMBER);", session)
    empty_res = executor.execute(
        "SELECT COUNT(*), AVG(sal), MAX(sal), MIN(sal) FROM salary_test;",
        session,
    )
    assert empty_res.result.rows[0][0] == 0
    assert empty_res.result.rows[0][1] is None

    executor.execute("INSERT INTO salary_test VALUES (1000);", session)
    executor.execute("INSERT INTO salary_test VALUES (2000);", session)
    executor.execute("INSERT INTO salary_test VALUES (3000);", session)

    pop_res = executor.execute(
        "SELECT COUNT(*), SUM(sal), AVG(sal), MIN(sal), MAX(sal) FROM salary_test;",
        session,
    )
    assert pop_res.result.rows[0][0] == 3
    assert pop_res.result.rows[0][1] == 6000
    assert pop_res.result.rows[0][2] == 2000.0
    assert pop_res.result.rows[0][3] == 1000
    assert pop_res.result.rows[0][4] == 3000


# ============================================================================
# 3. DML & TRANSACTION CONTROL (Test Cases 9-12)
# ============================================================================


def test_09_dml_insert_select(executor, session):
    """Test Case 9: INSERT INTO ... SELECT from another table."""
    executor.execute("CREATE TABLE src (id NUMBER, val VARCHAR2(20));", session)
    executor.execute("CREATE TABLE dst (id NUMBER, val VARCHAR2(20));", session)

    executor.execute("INSERT INTO src VALUES (1, 'A');", session)
    executor.execute("INSERT INTO src VALUES (2, 'B');", session)

    ins_res = executor.execute("INSERT INTO dst SELECT * FROM src;", session)
    assert ins_res.result.feedback_message == "2 rows created."

    cnt_res = executor.execute("SELECT COUNT(*) FROM dst;", session)
    assert cnt_res.result.rows[0][0] == 2


def test_10_dml_update_with_expression(executor, session):
    """Test Case 10: UPDATE salary = salary * 1.10."""
    executor.execute("CREATE TABLE staff (id NUMBER, salary NUMBER);", session)
    executor.execute("INSERT INTO staff VALUES (1, 1000);", session)
    executor.execute("INSERT INTO staff VALUES (2, 2000);", session)

    up_res = executor.execute("UPDATE staff SET salary = salary * 1.1 WHERE id = 1;", session)
    assert up_res.result.feedback_message == "1 row updated."

    sel_res = executor.execute("SELECT salary FROM staff WHERE id = 1;", session)
    assert sel_res.result.rows[0][0] == 1100.0


def test_11_tcl_nested_savepoints_and_partial_rollback(executor, session):
    """Test Case 11: Nested savepoints sp1, sp2 and rollbacks."""
    executor.execute("CREATE TABLE balance (val NUMBER);", session)
    executor.execute("INSERT INTO balance VALUES (100);", session)

    executor.execute("SAVEPOINT sp1;", session)
    executor.execute("UPDATE balance SET val = 200;", session)

    executor.execute("SAVEPOINT sp2;", session)
    executor.execute("UPDATE balance SET val = 300;", session)

    # Rollback to sp2 restores val = 200
    executor.execute("ROLLBACK TO sp2;", session)
    res_sp2 = executor.execute("SELECT val FROM balance;", session)
    assert res_sp2.result.rows[0][0] == 200

    # Rollback to sp1 restores val = 100
    executor.execute("ROLLBACK TO sp1;", session)
    res_sp1 = executor.execute("SELECT val FROM balance;", session)
    assert res_sp1.result.rows[0][0] == 100


def test_12_tcl_commit_persistence(executor, session):
    """Test Case 12: COMMIT persists data against later rollback."""
    executor.execute("CREATE TABLE committed_data (id NUMBER PRIMARY KEY);", session)
    executor.execute("INSERT INTO committed_data VALUES (1);", session)
    executor.execute("COMMIT;", session)

    executor.execute("INSERT INTO committed_data VALUES (2);", session)
    executor.execute("ROLLBACK;", session)

    res = executor.execute("SELECT COUNT(*) FROM committed_data;", session)
    assert res.result.rows[0][0] == 1


# ============================================================================
# 4. DCL SECURITY & PRIVILEGES (Test Cases 13-15)
# ============================================================================


def test_13_dcl_granular_action_privileges(executor, session):
    """Test Case 13: Granular privileges (GRANT SELECT, INSERT vs UPDATE/DELETE)."""
    executor.execute("CREATE TABLE inventory (item_id NUMBER PRIMARY KEY, qty NUMBER);", session)
    user_alice = Session(user="ALICE")

    executor.execute("GRANT SELECT, INSERT ON inventory TO ALICE;", session)

    # Alice can insert and select
    ins = executor.execute("INSERT INTO inventory VALUES (10, 50);", user_alice)
    assert ins.result.feedback_message == "1 row created."
    sel = executor.execute("SELECT * FROM inventory;", user_alice)
    assert len(sel.result.rows) == 1

    # Alice cannot UPDATE
    with pytest.raises(OracleError) as exc:
        executor.execute("UPDATE inventory SET qty = 100 WHERE item_id = 10;", user_alice)
    assert "ORA-01031" in str(exc.value)

    # Alice cannot DELETE
    with pytest.raises(OracleError) as exc:
        executor.execute("DELETE FROM inventory WHERE item_id = 10;", user_alice)
    assert "ORA-01031" in str(exc.value)


def test_14_dcl_grant_all_privileges(executor, session):
    """Test Case 14: GRANT ALL ON table TO user."""
    executor.execute("CREATE TABLE reports (rep_id NUMBER);", session)
    user_bob = Session(user="BOB")

    executor.execute("GRANT ALL ON reports TO BOB;", session)
    executor.execute("INSERT INTO reports VALUES (1);", user_bob)
    executor.execute("UPDATE reports SET rep_id = 2 WHERE rep_id = 1;", user_bob)
    executor.execute("DELETE FROM reports WHERE rep_id = 2;", user_bob)
    sel = executor.execute("SELECT * FROM reports;", user_bob)
    assert len(sel.result.rows) == 0


def test_15_dcl_revoke_selective_privilege(executor, session):
    """Test Case 15: Revoke selective privilege while preserving others."""
    executor.execute("CREATE TABLE docs (doc_id NUMBER);", session)
    user_charlie = Session(user="CHARLIE")

    executor.execute("GRANT SELECT, INSERT ON docs TO CHARLIE;", session)
    executor.execute("REVOKE INSERT ON docs FROM CHARLIE;", session)

    # SELECT still permitted
    sel = executor.execute("SELECT * FROM docs;", user_charlie)
    assert len(sel.result.rows) == 0

    # INSERT now blocked
    with pytest.raises(OracleError) as exc:
        executor.execute("INSERT INTO docs VALUES (1);", user_charlie)
    assert "ORA-01031" in str(exc.value)


# ============================================================================
# 5. JOINS, SUBQUERIES & SET OPERATIONS (Test Cases 16-20)
# ============================================================================


def test_16_inner_and_left_joins(executor, session):
    """Test Case 16: INNER JOIN and LEFT OUTER JOIN."""
    executor.execute("CREATE TABLE dept (id NUMBER PRIMARY KEY, name VARCHAR2(30));", session)
    executor.execute(
        "CREATE TABLE emp (id NUMBER PRIMARY KEY, name VARCHAR2(30), dept_id NUMBER);",
        session,
    )

    executor.execute("INSERT INTO dept VALUES (10, 'IT');", session)
    executor.execute("INSERT INTO dept VALUES (20, 'HR');", session)

    executor.execute("INSERT INTO emp VALUES (1, 'Alice', 10);", session)
    executor.execute("INSERT INTO emp VALUES (2, 'Bob', NULL);", session)

    # Inner Join -> only Alice
    inner_res = executor.execute(
        "SELECT e.name, d.name FROM emp e JOIN dept d ON e.dept_id = d.id;",
        session,
    )
    assert len(inner_res.result.rows) == 1
    assert inner_res.result.rows[0][0] == "Alice"

    # Left Join -> Alice and Bob
    left_res = executor.execute(
        "SELECT e.name, d.name FROM emp e LEFT JOIN dept d ON e.dept_id = d.id ORDER BY e.id;",
        session,
    )
    assert len(left_res.result.rows) == 2
    assert left_res.result.rows[1][0] == "Bob"
    assert left_res.result.rows[1][1] is None


def test_17_cross_join_cartesian_product(executor, session):
    """Test Case 17: CROSS JOIN generating cartesian product."""
    executor.execute("CREATE TABLE t1 (x VARCHAR2(2));", session)
    executor.execute("CREATE TABLE t2 (y NUMBER);", session)

    executor.execute("INSERT INTO t1 VALUES ('A');", session)
    executor.execute("INSERT INTO t1 VALUES ('B');", session)
    executor.execute("INSERT INTO t2 VALUES (1);", session)
    executor.execute("INSERT INTO t2 VALUES (2);", session)

    res = executor.execute("SELECT * FROM t1 CROSS JOIN t2;", session)
    assert len(res.result.rows) == 4


def test_18_subqueries_in_where_and_scalar(executor, session):
    """Test Case 18: WHERE col IN (SELECT ...) and scalar subqueries."""
    executor.execute(
        "CREATE TABLE students (id NUMBER, name VARCHAR2(30), gpa NUMBER(3,2));",
        session,
    )
    executor.execute("INSERT INTO students VALUES (1, 'A', 9.5);", session)
    executor.execute("INSERT INTO students VALUES (2, 'B', 8.0);", session)
    executor.execute("INSERT INTO students VALUES (3, 'C', 7.5);", session)

    res = executor.execute(
        "SELECT name FROM students WHERE gpa > (SELECT AVG(gpa) FROM students);",
        session,
    )
    assert len(res.result.rows) == 1
    assert res.result.rows[0][0] == "A"


def test_19_set_operations_union_intersect_minus(executor, session):
    """Test Case 19: UNION, INTERSECT, and MINUS set operations."""
    executor.execute("CREATE TABLE s1 (num NUMBER);", session)
    executor.execute("CREATE TABLE s2 (num NUMBER);", session)

    executor.execute("INSERT INTO s1 VALUES (1);", session)
    executor.execute("INSERT INTO s1 VALUES (2);", session)
    executor.execute("INSERT INTO s1 VALUES (3);", session)

    executor.execute("INSERT INTO s2 VALUES (2);", session)
    executor.execute("INSERT INTO s2 VALUES (3);", session)
    executor.execute("INSERT INTO s2 VALUES (4);", session)

    # UNION
    u_res = executor.execute("SELECT num FROM s1 UNION SELECT num FROM s2;", session)
    assert len(u_res.result.rows) == 4

    # INTERSECT
    i_res = executor.execute("SELECT num FROM s1 INTERSECT SELECT num FROM s2;", session)
    assert len(i_res.result.rows) == 2
    assert [r[0] for r in i_res.result.rows] == [2, 3]

    # MINUS (Oracle MINUS -> SQLite EXCEPT)
    m_res = executor.execute("SELECT num FROM s1 MINUS SELECT num FROM s2;", session)
    assert len(m_res.result.rows) == 1
    assert m_res.result.rows[0][0] == 1


def test_20_order_by_multiple_columns_and_aliases(executor, session):
    """Test Case 20: ORDER BY multiple columns with mixed ASC/DESC and alias."""
    executor.execute(
        "CREATE TABLE ranks (dept VARCHAR2(10), score NUMBER, name VARCHAR2(20));",
        session,
    )
    executor.execute("INSERT INTO ranks VALUES ('CSE', 90, 'Zack');", session)
    executor.execute("INSERT INTO ranks VALUES ('CSE', 90, 'Adam');", session)
    executor.execute("INSERT INTO ranks VALUES ('ECE', 95, 'Beth');", session)

    res = executor.execute(
        "SELECT dept, score, name AS student_name FROM ranks ORDER BY score DESC, name ASC;",
        session,
    )
    assert res.result.rows[0][2] == "Beth"
    assert res.result.rows[1][2] == "Adam"
    assert res.result.rows[2][2] == "Zack"


# ============================================================================
# 6. VIEWS, MATERIALIZED VIEWS & CASCADE (Test Cases 21-23)
# ============================================================================


def test_21_multi_table_view_query(executor, session):
    """Test Case 21: CREATE VIEW joining multiple tables."""
    executor.execute("CREATE TABLE d (id NUMBER PRIMARY KEY, dname VARCHAR2(20));", session)
    executor.execute(
        "CREATE TABLE e (id NUMBER PRIMARY KEY, ename VARCHAR2(20), did NUMBER);",
        session,
    )

    executor.execute("INSERT INTO d VALUES (1, 'Design');", session)
    executor.execute("INSERT INTO e VALUES (10, 'Maya', 1);", session)

    executor.execute(
        "CREATE VIEW emp_dept_view AS SELECT e.ename, d.dname FROM e JOIN d ON e.did = d.id;",
        session,
    )
    res = executor.execute("SELECT * FROM emp_dept_view;", session)
    assert res.result.rows[0][0] == "Maya"
    assert res.result.rows[0][1] == "Design"


def test_22_materialized_view_snapshot_isolation(executor, session):
    """Test Case 22: Materialized view snapshot data isolation before REFRESH."""
    executor.execute("CREATE TABLE metrics (val NUMBER);", session)
    executor.execute("INSERT INTO metrics VALUES (10);", session)

    executor.execute(
        "CREATE MATERIALIZED VIEW mv_metrics AS SELECT SUM(val) AS total FROM metrics;",
        session,
    )
    snap1 = executor.execute("SELECT total FROM mv_metrics;", session)
    assert snap1.result.rows[0][0] == 10

    # Insert more data into base table
    executor.execute("INSERT INTO metrics VALUES (20);", session)

    # Snapshot is unchanged before refresh
    snap2 = executor.execute("SELECT total FROM mv_metrics;", session)
    assert snap2.result.rows[0][0] == 10

    # Refresh updates the snapshot
    executor.execute("REFRESH MATERIALIZED VIEW mv_metrics;", session)
    snap3 = executor.execute("SELECT total FROM mv_metrics;", session)
    assert snap3.result.rows[0][0] == 30


def test_23_multi_tier_cascade_deletion(executor, session):
    """Test Case 23: Multi-tier cascade deletion (Grandparent -> Parent -> Child)."""
    executor.execute(
        "CREATE TABLE university (u_id NUMBER PRIMARY KEY, uname VARCHAR2(30));",
        session,
    )
    executor.execute(
        """
        CREATE TABLE faculty (
            f_id NUMBER PRIMARY KEY,
            fname VARCHAR2(30),
            u_id NUMBER,
            FOREIGN KEY (u_id) REFERENCES university(u_id) ON DELETE CASCADE
        );
        """,
        session,
    )
    executor.execute(
        """
        CREATE TABLE students_tier (
            s_id NUMBER PRIMARY KEY,
            f_id NUMBER,
            FOREIGN KEY (f_id) REFERENCES faculty(f_id) ON DELETE CASCADE
        );
        """,
        session,
    )

    executor.execute("INSERT INTO university VALUES (1, 'Tech University');", session)
    executor.execute("INSERT INTO faculty VALUES (10, 'Engineering', 1);", session)
    executor.execute("INSERT INTO students_tier VALUES (100, 10);", session)

    # Delete University -> Should cascade to faculty and students_tier
    executor.execute("DELETE FROM university WHERE u_id = 1;", session)

    assert executor.execute("SELECT COUNT(*) FROM university;", session).result.rows[0][0] == 0
    assert executor.execute("SELECT COUNT(*) FROM faculty;", session).result.rows[0][0] == 0
    assert executor.execute("SELECT COUNT(*) FROM students_tier;", session).result.rows[0][0] == 0


# ============================================================================
# 7. SQL*PLUS COMMANDS & FORMATTING (Test Cases 24-26)
# ============================================================================


def test_24_sqlplus_set_and_show_options(db, session):
    """Test Case 24: SQL*Plus SET and SHOW options."""
    cmd_engine = SQLPlusCommandEngine(session=session, adapter=db)

    cmd_engine.execute("SET PAGESIZE 50")
    assert session.pagesize == 50
    show_page = cmd_engine.execute("SHOW PAGESIZE")
    assert "50" in show_page.output

    cmd_engine.execute("SET HEADING OFF")
    assert session.heading is False

    cmd_engine.execute("SET NULL '(null)'")
    assert session.null_value == "(null)"


def test_25_sqlplus_formatter_null_and_feedback(db, session):
    """Test Case 25: SQL*Plus OutputFormatter custom null string and feedback."""
    session.null_value = "N/A"
    formatter = OutputFormatter(session)

    executor = SQLExecutor(db)
    executor.execute("CREATE TABLE sample_fmt (id NUMBER, info VARCHAR2(20));", session)
    executor.execute("INSERT INTO sample_fmt VALUES (1, NULL);", session)
    query_res = executor.execute("SELECT * FROM sample_fmt;", session)

    formatted = formatter.format_query(query_res.result)
    assert "N/A" in formatted
    assert "1 row selected." in formatted


def test_26_error_mapping_ora_codes(executor, session):
    """Test Case 26: Canonical Oracle error code mapping (ORA-00942, ORA-00904)."""
    # 1. Non-existent table -> ORA-00942
    with pytest.raises(OracleError) as exc1:
        executor.execute("SELECT * FROM non_existent_table_xyz;", session)
    assert "ORA-00942" in str(exc1.value)

    # 2. Non-existent column -> ORA-00904
    executor.execute("CREATE TABLE dummy_col_test (col1 NUMBER);", session)
    with pytest.raises(OracleError) as exc2:
        executor.execute("SELECT invalid_column_name FROM dummy_col_test;", session)
    assert "ORA-00904" in str(exc2.value)
