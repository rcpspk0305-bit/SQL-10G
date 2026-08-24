"""Unit and integration tests for Oracle ROWNUM pseudo-column and persistent runtime storage."""

import os
from pathlib import Path

from app.cli.session import Session
from app.config.settings import Settings
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.executor import SQLExecutor
from app.engine.translator import SQLTranslator


def test_oracle_rownum_where_clause_transpilation():
    """Test ROWNUM in WHERE clause transpiles to LIMIT in SQLite."""
    translator = SQLTranslator()

    t1 = translator.transpile("SELECT sname FROM student WHERE rownum < 3;")
    assert "LIMIT 2" in t1.sqlite_sql.upper()

    t2 = translator.transpile("SELECT * FROM student WHERE rownum <= 5;")
    assert "LIMIT 5" in t2.sqlite_sql.upper()

    t3 = translator.transpile("SELECT sname FROM student WHERE cgpa > 8 AND rownum < 3;")
    assert "LIMIT 2" in t3.sqlite_sql.upper()
    assert "CGPA > 8" in t3.sqlite_sql.upper()

    t4 = translator.transpile("SELECT sname FROM student WHERE rownum = 1;")
    assert "LIMIT 1" in t4.sqlite_sql.upper()


def test_oracle_rownum_select_expression_transpilation():
    """Test ROWNUM in SELECT list transpiles to ROW_NUMBER() window function."""
    translator = SQLTranslator()

    t = translator.transpile("SELECT rownum, sname FROM student;")
    assert "ROW_NUMBER()" in t.sqlite_sql.upper()


def test_oracle_rownum_execution_end_to_end():
    """Test executing ROWNUM queries against real data in SQLite."""
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()
    executor = SQLExecutor(adapter)
    session = Session()

    executor.execute("CREATE TABLE student (rollno INT, sname VARCHAR2(20), cgpa NUMBER);", session)
    executor.execute("INSERT INTO student VALUES (1, 'One', 9.1);", session)
    executor.execute("INSERT INTO student VALUES (2, 'Two', 9.5);", session)
    executor.execute("INSERT INTO student VALUES (3, 'Three', 8.4);", session)
    executor.execute("INSERT INTO student VALUES (4, 'Four', 7.9);", session)

    res = executor.execute("SELECT sname FROM student WHERE rownum < 3;", session)
    assert len(res.result.rows) == 2
    assert res.result.rows[0][0] == "One"
    assert res.result.rows[1][0] == "Two"

    res_select = executor.execute("SELECT rownum, sname FROM student WHERE rownum <= 3;", session)
    assert len(res_select.result.rows) == 3

    adapter.close()


def test_persistent_database_storage_settings(tmp_path):
    """Test that default db_path in settings points to persistent file storage."""
    db_file = tmp_path / "test_persist.db"
    settings = Settings(db_path=db_file)

    adapter = SQLiteAdapter(str(settings.db_path))
    adapter.connect()
    executor = SQLExecutor(adapter)
    session = Session()

    executor.execute("CREATE TABLE test_persist (id INT, val VARCHAR2(20));", session)
    executor.execute("INSERT INTO test_persist VALUES (10, 'Persisted');", session)
    executor.execute("COMMIT;", session)
    adapter.close()

    assert db_file.exists()

    # Reopen same database file and verify data persists
    adapter2 = SQLiteAdapter(str(settings.db_path))
    adapter2.connect()
    executor2 = SQLExecutor(adapter2)
    res = executor2.execute("SELECT val FROM test_persist WHERE id = 10;", session)
    assert len(res.result.rows) == 1
    assert res.result.rows[0][0] == "Persisted"
    adapter2.close()
