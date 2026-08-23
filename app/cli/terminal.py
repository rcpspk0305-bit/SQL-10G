"""Interactive SQL*Plus 10g terminal interface for OraCLI."""

import sys
from typing import TextIO

from app.cli.command_router import CommandRouter
from app.cli.session import Session
from app.config.settings import settings
from app.database.sqlite_adapter import SQLiteAdapter
from app.parser.buffer import InputBuffer


class Terminal:
    """Interactive SQL*Plus REPL terminal."""

    def __init__(
        self,
        session: Session | None = None,
        adapter: SQLiteAdapter | None = None,
        router: CommandRouter | None = None,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
    ) -> None:
        self.session = session or Session()
        self.adapter = adapter or SQLiteAdapter(str(settings.db_path))
        self.router = router or CommandRouter(self.session, self.adapter)
        self.buffer = InputBuffer()
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout

    def print_banner(self) -> None:
        """Display the Oracle SQL*Plus startup banner."""
        banner_text = (
            f"\n{settings.banner}\n\n"
            f"Connected to:\n"
            f"{settings.app_name} Database Release {settings.version} - Educational Edition\n\n"
        )
        self.stdout.write(banner_text)
        self.stdout.flush()

    def run_repl(self) -> None:
        """Run the interactive Read-Eval-Print-Loop."""
        self.adapter.connect()
        self.print_banner()

        while True:
            prompt = self.buffer.prompt
            try:
                self.stdout.write(prompt)
                self.stdout.flush()
                line = self.stdin.readline()
                if not line:
                    # End of file reached
                    break

                # Strip trailing newline
                line = line.rstrip("\r\n")

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

        self.adapter.close()
        self.stdout.write("Disconnected from Oracle Database.\n")
        self.stdout.flush()


def main() -> None:
    """Entry point for oracli command."""
    terminal = Terminal()
    terminal.run_repl()


if __name__ == "__main__":
    main()
