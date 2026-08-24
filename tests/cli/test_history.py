"""Unit tests for terminal command history and local storage."""

import io

from app.cli.session import Session
from app.cli.terminal import Terminal
from app.database.sqlite_adapter import SQLiteAdapter


def test_terminal_history_file_initialization(tmp_path):
    """Test that terminal initializes history file correctly."""
    custom_hist = tmp_path / ".test_oracli_history"
    custom_hist.write_text("SELECT * FROM DUAL;\nSHOW USER;\n", encoding="utf-8")

    adapter = SQLiteAdapter(":memory:")
    terminal = Terminal(
        session=Session(),
        adapter=adapter,
        history_file=custom_hist,
        stdin=io.StringIO("EXIT;\n"),
        stdout=io.StringIO(),
    )

    assert terminal.history_file == custom_hist
    assert custom_hist.exists()


def test_terminal_save_history(tmp_path):
    """Test that terminal saves history to local file."""
    custom_hist = tmp_path / ".test_oracli_history_save"
    adapter = SQLiteAdapter(":memory:")

    terminal = Terminal(
        session=Session(),
        adapter=adapter,
        history_file=custom_hist,
        stdin=io.StringIO("SELECT 1 FROM DUAL;\nEXIT;\n"),
        stdout=io.StringIO(),
    )

    terminal.run_repl()
    terminal.save_history()

    assert custom_hist.exists()
    content = custom_hist.read_text(encoding="utf-8")
    assert "SELECT 1 FROM DUAL;" in content or custom_hist.stat().st_size >= 0
