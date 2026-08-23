"""End-to-end integration tests for OraCLI 10G."""

from io import StringIO

from app.cli.command_router import CommandRouter
from app.cli.session import Session
from app.cli.terminal import Terminal
from app.database.sqlite_adapter import SQLiteAdapter
from app.parser.buffer import StatementType


def test_student_lifecycle_end_to_end():
    session = Session()
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()
    router = CommandRouter(session, adapter)

    # 1. CREATE TABLE student
    create_sql = """
    CREATE TABLE student (
        rollno NUMBER,
        name VARCHAR2(50),
        cgpa NUMBER(3,2)
    )
    """
    res1 = router.route(create_sql, StatementType.SQL)
    assert "Table created." in res1.output

    # 2. INSERT INTO student
    insert_sql = "INSERT INTO student VALUES (101, 'Rahul', 8.7)"
    res2 = router.route(insert_sql, StatementType.SQL)
    assert "1 row created." in res2.output

    insert_sql_2 = "INSERT INTO student VALUES (102, 'Priya', 9.1)"
    res2_2 = router.route(insert_sql_2, StatementType.SQL)
    assert "1 row created." in res2_2.output

    # 3. SELECT * FROM student
    select_sql = "SELECT * FROM student"
    res3 = router.route(select_sql, StatementType.SQL)

    assert "ROLLNO" in res3.output
    assert "NAME" in res3.output
    assert "CGPA" in res3.output
    assert "Rahul" in res3.output
    assert "Priya" in res3.output
    assert "8.7" in res3.output
    assert "9.1" in res3.output
    assert "2 rows selected." in res3.output

    adapter.close()


def test_terminal_session_script_simulation():
    stdin = StringIO(
        "CREATE TABLE student (\n"
        "rollno NUMBER,\n"
        "name VARCHAR2(50),\n"
        "cgpa NUMBER(3,2)\n"
        ");\n"
        "INSERT INTO student VALUES (101, 'Rahul', 8.7);\n"
        "SELECT * FROM student;\n"
        "EXIT\n"
    )
    stdout = StringIO()

    adapter = SQLiteAdapter(":memory:")
    terminal = Terminal(adapter=adapter, stdin=stdin, stdout=stdout)
    terminal.run_repl()

    output = stdout.getvalue()

    # Check banner
    assert "SQL*Plus: Release 10.2 Compatible Educational Edition" in output
    # Check table creation feedback
    assert "Table created." in output
    # Check insert feedback
    assert "1 row created." in output
    # Check select result and feedback
    assert "ROLLNO" in output
    assert "NAME" in output
    assert "CGPA" in output
    assert "Rahul" in output
    assert "1 row selected." in output
    # Check exit message
    assert "Disconnected from Oracle Database." in output
