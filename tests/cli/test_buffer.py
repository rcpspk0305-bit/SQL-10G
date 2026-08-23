"""Unit tests for InputBuffer multiline collection and syntax awareness."""

from app.parser.buffer import InputBuffer, StatementType


def test_buffer_single_line_sql():
    buf = InputBuffer()
    assert buf.prompt == "SQL> "
    is_complete, stmt, stmt_type = buf.feed_line("SELECT 1 FROM DUAL;")
    assert is_complete is True
    assert stmt == "SELECT 1 FROM DUAL"
    assert stmt_type == StatementType.SQL
    assert buf.is_empty is True


def test_buffer_multiline_sql():
    buf = InputBuffer()
    assert buf.prompt == "SQL> "

    is_complete, stmt, stmt_type = buf.feed_line("CREATE TABLE student (")
    assert is_complete is False
    assert buf.prompt == "  2  "

    is_complete, stmt, stmt_type = buf.feed_line("    rollno NUMBER,")
    assert is_complete is False
    assert buf.prompt == "  3  "

    is_complete, stmt, stmt_type = buf.feed_line("    name VARCHAR2(50)")
    assert is_complete is False
    assert buf.prompt == "  4  "

    is_complete, stmt, stmt_type = buf.feed_line(");")
    assert is_complete is True
    assert stmt_type == StatementType.SQL
    assert "CREATE TABLE student" in stmt
    assert "rollno NUMBER" in stmt
    assert buf.is_empty is True


def test_buffer_semicolon_inside_single_quotes():
    buf = InputBuffer()
    is_complete, stmt, stmt_type = buf.feed_line("INSERT INTO t VALUES ('hello;world', 1);")
    assert is_complete is True
    assert stmt == "INSERT INTO t VALUES ('hello;world', 1)"
    assert stmt_type == StatementType.SQL


def test_buffer_multiline_semicolon_inside_string():
    buf = InputBuffer()
    is_complete, _, _ = buf.feed_line("INSERT INTO t VALUES ('multi;")
    assert is_complete is False
    assert buf.prompt == "  2  "

    is_complete, stmt, stmt_type = buf.feed_line("line;value');")
    assert is_complete is True
    assert stmt_type == StatementType.SQL
    assert "multi;\nline;value" in stmt


def test_buffer_sqlplus_commands():
    buf = InputBuffer()
    is_complete, stmt, stmt_type = buf.feed_line("EXIT")
    assert is_complete is True
    assert stmt == "EXIT"
    assert stmt_type == StatementType.SQLPLUS

    is_complete, stmt, stmt_type = buf.feed_line("SHOW USER;")
    assert is_complete is True
    assert stmt == "SHOW USER"
    assert stmt_type == StatementType.SQLPLUS


def test_buffer_slash_execution():
    buf = InputBuffer()
    buf.feed_line("SELECT * FROM student")
    is_complete, stmt, stmt_type = buf.feed_line("/")
    assert is_complete is True
    assert stmt == "SELECT * FROM student"
    assert stmt_type == StatementType.SQL
