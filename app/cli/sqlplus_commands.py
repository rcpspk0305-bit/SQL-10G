"""SQL*Plus built-in commands engine."""

from dataclasses import dataclass

from app.cli.session import Session
from app.database.adapter import DatabaseAdapter


@dataclass
class CommandResponse:
    """Outcome of a SQL*Plus command execution."""

    output: str = ""
    should_exit: bool = False


class SQLPlusCommandEngine:
    """Executes native SQL*Plus client commands."""

    def __init__(self, session: Session, adapter: DatabaseAdapter) -> None:
        self.session = session
        self.adapter = adapter

    def execute(self, cmd_line: str) -> CommandResponse:
        """Parse and execute a SQL*Plus command."""
        cleaned = cmd_line.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        if not cleaned:
            return CommandResponse()

        tokens = cleaned.split()
        cmd = tokens[0].upper()
        args = tokens[1:]

        match cmd:
            case "EXIT" | "QUIT":
                return CommandResponse(should_exit=True)

            case "SHOW":
                return self._handle_show(args)

            case "SET":
                return self._handle_set(args)

            case "CLEAR":
                return self._handle_clear(args)

            case "HOST":
                return CommandResponse(output="HOST command is disabled for security.")

            case "HELP":
                help_msg = (
                    "Available commands: EXIT, QUIT, SHOW USER, SET PAGESIZE, "
                    "SET LINESIZE, SET HEADING, SET FEEDBACK, SET NULL, CLEAR SCREEN\n"
                )
                return CommandResponse(output=help_msg)

            case _:
                return CommandResponse(
                    output=f'SP2-0042: unknown command "{cmd}" - rest of line ignored.\n'
                )

    def _handle_show(self, args: list[str]) -> CommandResponse:
        """Handle SHOW commands."""
        if not args:
            return CommandResponse(output="SP2-0158: unknown SHOW option.\n")

        subcmd = args[0].upper()
        match subcmd:
            case "USER":
                return CommandResponse(output=f'USER is "{self.session.user}"\n')
            case "PAGESIZE":
                return CommandResponse(output=f"pagesize {self.session.pagesize}\n")
            case "LINESIZE":
                return CommandResponse(output=f"linesize {self.session.linesize}\n")
            case "HEADING":
                val = "ON" if self.session.heading else "OFF"
                return CommandResponse(output=f"heading {val}\n")
            case "FEEDBACK":
                val = "ON" if self.session.feedback else "OFF"
                return CommandResponse(output=f"feedback {val}\n")
            case "NULL":
                return CommandResponse(output=f'null "{self.session.null_value}"\n')
            case _:
                return CommandResponse(output=f'SP2-0158: unknown SHOW option "{subcmd}"\n')

    def _handle_set(self, args: list[str]) -> CommandResponse:
        """Handle SET commands."""
        if len(args) < 2:
            return CommandResponse(output="SP2-0267: syntax error in SET command.\n")

        option = args[0].upper()
        value_str = " ".join(args[1:])

        match option:
            case "PAGESIZE":
                try:
                    self.session.pagesize = int(value_str)
                    return CommandResponse()
                except ValueError:
                    err_msg = f'SP2-0268: value "{value_str}" is invalid for SET PAGESIZE\n'
                    return CommandResponse(output=err_msg)

            case "LINESIZE":
                try:
                    self.session.linesize = int(value_str)
                    return CommandResponse()
                except ValueError:
                    err_msg = f'SP2-0268: value "{value_str}" is invalid for SET LINESIZE\n'
                    return CommandResponse(output=err_msg)

            case "HEADING":
                val = value_str.upper()
                if val in {"ON", "1", "TRUE"}:
                    self.session.heading = True
                elif val in {"OFF", "0", "FALSE"}:
                    self.session.heading = False
                else:
                    err_msg = f'SP2-0268: value "{value_str}" is invalid for SET HEADING\n'
                    return CommandResponse(output=err_msg)
                return CommandResponse()

            case "FEEDBACK":
                val = value_str.upper()
                if val in {"ON", "1", "TRUE"}:
                    self.session.feedback = True
                elif val in {"OFF", "0", "FALSE"}:
                    self.session.feedback = False
                else:
                    err_msg = f'SP2-0268: value "{value_str}" is invalid for SET FEEDBACK\n'
                    return CommandResponse(output=err_msg)
                return CommandResponse()

            case "NULL":
                clean_val = value_str.strip()
                if clean_val.startswith('"') and clean_val.endswith('"'):
                    clean_val = clean_val[1:-1]
                elif clean_val.startswith("'") and clean_val.endswith("'"):
                    clean_val = clean_val[1:-1]
                self.session.null_value = clean_val
                return CommandResponse()

            case _:
                return CommandResponse(output=f'SP2-0158: unknown SET option "{option}"\n')

    def _handle_clear(self, args: list[str]) -> CommandResponse:
        """Handle CLEAR commands."""
        if args and args[0].upper() in {"SCREEN", "SCR"}:
            # ANSI escape sequence to clear terminal
            return CommandResponse(output="\033[2J\033[H")
        return CommandResponse()
