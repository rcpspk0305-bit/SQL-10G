"""Unit and integration tests for Oracle-specific ALTER TABLE, DML without FROM, and TCL syntax."""

from app.cli.session import Session
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.executor import SQLExecutor
from app.engine.translator import SQLCommandType, SQLTranslator


def test_oracle_tcl_syntax_variations():
    """Test SAVE POINT and ROLLBACK savepoint variations."""
    translator = SQLTranslator()

    t1 = translator.transpile("SAVE POINT s1;")
    assert t1.command_type == SQLCommandType.SAVEPOINT
    assert "SAVEPOINT s1" in t1.sqlite_sql

    t2 = translator.transpile("savepoint s1;")
    assert t2.command_type == SQLCommandType.SAVEPOINT
    assert "SAVEPOINT s1" in t2.sqlite_sql

    t3 = translator.transpile("ROLLBACK s1;")
    assert t3.command_type == SQLCommandType.ROLLBACK_TO_SAVEPOINT
    assert "ROLLBACK TO SAVEPOINT s1" in t3.sqlite_sql

    t4 = translator.transpile("rollback to s1;")
    assert t4.command_type == SQLCommandType.ROLLBACK_TO_SAVEPOINT
    assert "ROLLBACK TO SAVEPOINT s1" in t4.sqlite_sql


def test_oracle_delete_without_from():
    """Test DELETE without FROM keyword."""
    translator = SQLTranslator()
    t = translator.transpile("DELETE student WHERE cgpa < 7;")
    assert t.command_type == SQLCommandType.DELETE
    assert "FROM" in t.sqlite_sql


def test_oracle_alter_table_add_constraint_and_columns_execution():
    """Test executing Oracle ALTER TABLE ADD variations end-to-end."""
    adapter = SQLiteAdapter(":memory:")
    adapter.connect()
    executor = SQLExecutor(adapter)
    session = Session()

    # Create tables
    executor.execute("CREATE TABLE Dept (Did INT PRIMARY KEY, DName VARCHAR2(30));", session)
    executor.execute(
        "CREATE TABLE student (Sid INT PRIMARY KEY, SName VARCHAR2(50), CGPA NUMBER);", session
    )

    # 1. ALTER TABLE ADD CONSTRAINT
    res1 = executor.execute(
        "ALTER TABLE student ADD CONSTRAINT abc FOREIGN KEY (Did) REFERENCES Dept(Did);", session
    )
    assert res1.result.feedback_message == "Table altered."

    # 2. ALTER TABLE ADD (col type) with parens
    res2 = executor.execute("ALTER TABLE student ADD (Email VARCHAR2(50));", session)
    assert res2.result.feedback_message == "Table altered."

    # 3. ALTER TABLE ADD with inline constraint
    res3 = executor.execute(
        "ALTER TABLE student ADD (Did INT CONSTRAINT fk_dept "
        "FOREIGN KEY (Did) REFERENCES Dept(Did));",
        session,
    )
    assert res3.result.feedback_message == "Table altered."

    # Verify column added
    cols_res = executor.execute("SELECT * FROM student;", session)
    assert "EMAIL" in [c.upper() for c in cols_res.result.columns]
    assert "DID" in [c.upper() for c in cols_res.result.columns]

    adapter.close()
