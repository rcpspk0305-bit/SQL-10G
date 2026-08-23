"""Unit tests for SQLiteAdapter."""

from app.database.sqlite_adapter import SQLiteAdapter


def test_sqlite_adapter_crud():
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()

    # Create table
    adapter.execute("CREATE TABLE t (id INTEGER, val TEXT);")

    # Insert row
    res = adapter.execute("INSERT INTO t VALUES (1, 'hello');")
    assert res.row_count == 1

    # Select row
    res = adapter.execute("SELECT * FROM t;")
    assert res.row_count == 1
    assert len(res.rows) == 1
    assert res.rows[0] == [1, "hello"]

    adapter.close()


def test_sqlite_adapter_dual_table():
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()

    res = adapter.execute("SELECT 1 FROM DUAL;")
    assert res.rows == [[1]]

    adapter.close()


def test_sqlite_adapter_custom_functions():
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()

    res = adapter.execute("SELECT NVL(NULL, 'default') FROM DUAL;")
    assert res.rows == [["default"]]

    res2 = adapter.execute("SELECT SYSDATE() FROM DUAL;")
    assert len(res2.rows) == 1
    assert len(res2.rows[0][0]) > 0

    adapter.close()
