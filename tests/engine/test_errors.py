"""Unit tests for Oracle error mapping."""

import sqlite3

from app.engine.errors import (
    ORA00904InvalidIdentifier,
    ORA00942TableOrViewDoesNotExist,
    ORA00955NameAlreadyUsed,
    map_sqlite_error,
)


def test_map_sqlite_no_such_table():
    err = sqlite3.OperationalError("no such table: nonexistent")
    ora_err = map_sqlite_error(err)
    assert isinstance(ora_err, ORA00942TableOrViewDoesNotExist)
    assert ora_err.code == "ORA-00942"
    assert "table or view does not exist" in ora_err.message


def test_map_sqlite_no_such_column():
    err = sqlite3.OperationalError("no such column: dummy_col")
    ora_err = map_sqlite_error(err)
    assert isinstance(ora_err, ORA00904InvalidIdentifier)
    assert ora_err.code == "ORA-00904"
    assert "invalid identifier" in ora_err.message


def test_map_sqlite_table_already_exists():
    err = sqlite3.OperationalError("table student already exists")
    ora_err = map_sqlite_error(err)
    assert isinstance(ora_err, ORA00955NameAlreadyUsed)
    assert ora_err.code == "ORA-00955"
