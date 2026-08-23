"""Unit tests for SQLTranslator."""

from app.engine.translator import SQLCommandType, SQLTranslator


def test_translate_create_table():
    translator = SQLTranslator()
    sql = """
    CREATE TABLE student (
        rollno NUMBER,
        name VARCHAR2(50),
        cgpa NUMBER(3,2)
    )
    """
    res = translator.transpile(sql)
    assert res.command_type == SQLCommandType.CREATE_TABLE
    assert "CREATE TABLE student" in res.sqlite_sql
    assert "REAL" in res.sqlite_sql
    assert "TEXT" in res.sqlite_sql


def test_translate_insert():
    translator = SQLTranslator()
    sql = "INSERT INTO student VALUES (101, 'Rahul', 8.7)"
    res = translator.transpile(sql)
    assert res.command_type == SQLCommandType.INSERT
    assert "INSERT INTO student" in res.sqlite_sql


def test_translate_select():
    translator = SQLTranslator()
    sql = "SELECT rollno, name FROM student WHERE cgpa > 8.0"
    res = translator.transpile(sql)
    assert res.command_type == SQLCommandType.SELECT
    assert "SELECT" in res.sqlite_sql
    assert "FROM student" in res.sqlite_sql
