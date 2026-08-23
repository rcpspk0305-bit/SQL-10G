"""SQL*Plus built-in commands engine."""

from dataclasses import dataclass

from app.cli.session import Session
from app.database.adapter import DatabaseAdapter


@dataclass
class CommandResponse:
    """Outcome of a SQL*Plus command execution."""

    output: str = ""
    should_exit: bool = False


def _sqlite_type_to_oracle(t: str) -> str:
    """Convert SQLite column types back to Oracle canonical representations for DESCRIBE."""
    t_up = t.upper()
    if any(k in t_up for k in ("DECIMAL", "REAL", "INT", "NUM", "FLOAT", "DOUBLE")):
        return "NUMBER"
    if any(k in t_up for k in ("TEXT", "CHAR", "VARCHAR")):
        return "VARCHAR2(50)"
    if "BLOB" in t_up:
        return "BLOB"
    if "CLOB" in t_up:
        return "CLOB"
    return t_up if t_up else "VARCHAR2(50)"


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

            case "DESC" | "DESCRIBE":
                return self._handle_describe(args)

            case "SHOW":
                return self._handle_show(args)

            case "SET":
                return self._handle_set(args)

            case "CLEAR":
                return self._handle_clear(args)

            case "LIST" | "L":
                return CommandResponse(output="  1* SELECT * FROM DUAL\n")

            case "RUN" | "R":
                return CommandResponse(output="Running previous statement buffer...\n")

            case "SPOOL":
                spool_arg = args[0] if args else "OFF"
                return CommandResponse(output=f"Spooling set to: {spool_arg}\n")

            case "COLUMN" | "COL":
                return CommandResponse(output="Column format registered.\n")

            case "HOST":
                return CommandResponse(output="HOST command is disabled for security.")

            case "HELP":
                help_msg = (
                    "Available commands: DESC, DESCRIBE, EXIT, QUIT, SHOW USER, SET PAGESIZE, "
                    "SET LINESIZE, SET HEADING, SET FEEDBACK, SET NULL, CLEAR SCREEN, LIST, "
                    "RUN, SPOOL\n"
                )
                return CommandResponse(output=help_msg)

            case _:
                return CommandResponse(
                    output=f'SP2-0042: unknown command "{cmd}" - rest of line ignored.\n'
                )

    def _handle_describe(self, args: list[str]) -> CommandResponse:
        """Handle DESCRIBE table or view command."""
        if not args:
            return CommandResponse(
                output="SP2-0044: For a list of known options, enter: HELP DESCRIBE\n"
            )

        table_name = args[0].strip().lower()

        # Query PRAGMA table_info
        try:
            res = self.adapter.execute(f"PRAGMA table_info({table_name});")
            if not res.rows:
                return CommandResponse(
                    output=f'ORA-04043: object "{table_name.upper()}" does not exist\n'
                )

            # Format Oracle-style table describe:
            # Name       Null?       Type
            # ---------- ----------- ---------------
            headers = ["Name", "Null?", "Type"]
            rows_data: list[list[str]] = []

            for r in res.rows:
                # r: (cid, name, type, notnull, dflt_value, pk)
                col_name = str(r[1]).upper()
                is_not_null = "NOT NULL" if r[3] == 1 or r[5] == 1 else ""
                raw_type = str(r[2]).upper()
                col_type = _sqlite_type_to_oracle(raw_type)
                rows_data.append([col_name, is_not_null, col_type])

            col_widths = [10, 11, 15]
            for r in rows_data:
                col_widths[0] = max(col_widths[0], len(r[0]))
                col_widths[1] = max(col_widths[1], len(r[1]))
                col_widths[2] = max(col_widths[2], len(r[2]))

            out_lines: list[str] = []
            header_str = (
                headers[0].ljust(col_widths[0])
                + " "
                + headers[1].ljust(col_widths[1])
                + " "
                + headers[2].ljust(col_widths[2])
            )
            dashes_str = "-" * col_widths[0] + " " + "-" * col_widths[1] + " " + "-" * col_widths[2]
            out_lines.append(header_str)
            out_lines.append(dashes_str)

            for r in rows_data:
                line = (
                    r[0].ljust(col_widths[0])
                    + " "
                    + r[1].ljust(col_widths[1])
                    + " "
                    + r[2].ljust(col_widths[2])
                )
                out_lines.append(line)

            return CommandResponse(output="\n".join(out_lines) + "\n")

        except Exception as e:
            return CommandResponse(output=f"Error executing DESCRIBE: {e}\n")

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
            return CommandResponse(output="\033[2J\033[H")
        return CommandResponse()
