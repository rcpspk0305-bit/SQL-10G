"""Interactive SQL*Plus 10g terminal interface for OraCLI."""

import atexit
import sys
from pathlib import Path
from typing import TextIO

from app.cli.command_router import CommandRouter
from app.cli.session import Session
from app.config.settings import settings
from app.database.sqlite_adapter import SQLiteAdapter
from app.parser.buffer import InputBuffer

# Setup readline for command history and arrow key navigation
_readline_available = False
try:
    import readline

    _readline_available = True
except ImportError:
    try:
        import pyreadline3 as readline  # Windows fallback

        _readline_available = True
    except ImportError:
        readline = None


class Terminal:
    """Interactive SQL*Plus REPL terminal with persistent history."""

    def __init__(
        self,
        session: Session | None = None,
        adapter: SQLiteAdapter | None = None,
        router: CommandRouter | None = None,
        history_file: Path | str | None = None,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
    ) -> None:
        self.session = session or Session()
        self.adapter = adapter or SQLiteAdapter(str(settings.db_path))
        self.router = router or CommandRouter(self.session, self.adapter)
        self.buffer = InputBuffer()
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout

        # Setup local history storage
        default_hist = Path.home() / ".oracli_history"
        self.history_file = Path(history_file) if history_file else default_hist
        self._history_loaded = False
        self._session_history: list[str] = []

        self._init_history()

    def _init_history(self) -> None:
        """Initialize readline history from local storage."""
        if not _readline_available or readline is None:
            return

        try:
            if self.history_file.exists():
                readline.read_history_file(str(self.history_file))
            readline.set_history_length(1000)
            self._history_loaded = True
            atexit.register(self.save_history)
        except Exception:
            pass

    def save_history(self) -> None:
        """Persist command history to local file."""
        if _readline_available and readline is not None and self._history_loaded:
            try:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                readline.write_history_file(str(self.history_file))
                return
            except Exception:
                pass

        # Fallback file append if readline write fails or isn't active
        try:
            if self._session_history:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                existing = []
                if self.history_file.exists():
                    existing = self.history_file.read_text(encoding="utf-8").splitlines()
                combined = existing + self._session_history
                # Keep last 1000 items
                trimmed = combined[-1000:]
                self.history_file.write_text("\n".join(trimmed) + "\n", encoding="utf-8")
        except Exception:
            pass

    def print_banner(self) -> None:
        """Display the Oracle SQL*Plus startup banner."""
        banner_text = (
            f"\n{settings.banner}\n\n"
            f"Connected to:\n"
            f"{settings.app_name} Database Release {settings.version} - Educational Edition\n\n"
        )
        self.stdout.write(banner_text)
        self.stdout.flush()

    def _read_line(self, prompt: str) -> str | None:
        """Read a single line using interactive input or stream readline."""
        is_interactive = (
            self.stdin is sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        )

        if is_interactive:
            try:
                return input(prompt)
            except EOFError:
                return None
        else:
            self.stdout.write(prompt)
            self.stdout.flush()
            line = self.stdin.readline()
            if not line:
                return None
            return line.rstrip("\r\n")

    def run_repl(self) -> None:
        """Run the interactive Read-Eval-Print-Loop."""
        self.adapter.connect()
        self.print_banner()

        while True:
            prompt = self.buffer.prompt
            try:
                line = self._read_line(prompt)
                if line is None:
                    # End of file reached
                    break

                # Track non-empty lines in history
                if line.strip():
                    self._session_history.append(line)

                is_complete, statement, stmt_type = self.buffer.feed_line(line)
                if is_complete and statement:
                    result = self.router.route(statement, stmt_type)
                    if result.output:
                        self.stdout.write(result.output)
                        self.stdout.flush()
                    if result.should_exit:
                        break

            except KeyboardInterrupt:
                # Ctrl+C clears current input buffer
                self.buffer.clear()
                self.stdout.write("\n")
                self.stdout.flush()
                continue
            except EOFError:
                break

        self.save_history()
        self.adapter.close()
        self.stdout.write("Disconnected from Oracle Database.\n")
        self.stdout.flush()


def main() -> None:
    """Entry point for oracli command."""
    terminal = Terminal()
    terminal.run_repl()


if __name__ == "__main__":
    main()
