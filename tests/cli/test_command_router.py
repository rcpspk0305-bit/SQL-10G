"""Unit tests for CommandRouter and SQLPlusCommandEngine."""

from app.cli.command_router import CommandRouter
from app.cli.session import Session
from app.database.sqlite_adapter import SQLiteAdapter
from app.parser.buffer import StatementType


def test_router_exit():
    session = Session()
    adapter = SQLiteAdapter(":memory:")
    router = CommandRouter(session, adapter)

    res = router.route("EXIT", StatementType.SQLPLUS)
    assert res.should_exit is True


def test_router_show_user():
    session = Session(user="HR")
    adapter = SQLiteAdapter(":memory:")
    router = CommandRouter(session, adapter)

    res = router.route("SHOW USER", StatementType.SQLPLUS)
    assert 'USER is "HR"' in res.output


def test_router_set_options():
    session = Session()
    adapter = SQLiteAdapter(":memory:")
    router = CommandRouter(session, adapter)

    router.route("SET PAGESIZE 50", StatementType.SQLPLUS)
    assert session.pagesize == 50

    router.route("SET HEADING OFF", StatementType.SQLPLUS)
    assert session.heading is False

    router.route("SET FEEDBACK OFF", StatementType.SQLPLUS)
    assert session.feedback is False
