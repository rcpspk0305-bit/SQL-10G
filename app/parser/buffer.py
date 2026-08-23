"""Multiline input buffer tracker for SQL and SQL*Plus statements."""

from dataclasses import dataclass, field
from enum import Enum, auto


class StatementType(Enum):
    """Type of statement being collected."""

    UNKNOWN = auto()
    SQL = auto()
    PLSQL = auto()
    SQLPLUS = auto()
    EMPTY = auto()


@dataclass
class InputBuffer:
    """Manages multiline input collection for SQL*Plus shell."""

    lines: list[str] = field(default_factory=list)
    in_single_quote: bool = False
    in_double_quote: bool = False
    in_block_comment: bool = False

    def clear(self) -> None:
        """Reset the buffer state."""
        self.lines.clear()
        self.in_single_quote = False
        self.in_double_quote = False
        self.in_block_comment = False

    @property
    def line_number(self) -> int:
        """Current continuation line number (1-indexed for next line)."""
        return len(self.lines) + 1

    @property
    def is_empty(self) -> bool:
        """Check if buffer has no lines."""
        return len(self.lines) == 0

    @property
    def prompt(self) -> str:
        """Returns the appropriate prompt for the current line."""
        if self.is_empty:
            return "SQL> "
        # SQL*Plus continuation prompt format: '  2  ', '  3  ', etc.
        return f"{self.line_number:>3}  "

    def get_full_text(self) -> str:
        """Return the accumulated text separated by newlines."""
        return "\n".join(self.lines)

    def is_sqlplus_command(self, first_line: str) -> bool:
        """Check if the first line is a SQL*Plus native command."""
        cleaned = first_line.strip()
        if not cleaned:
            return False
        # Strip trailing semicolon if present
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        upper_first_word = cleaned.split()[0].upper()
        sqlplus_cmds = {
            "EXIT",
            "QUIT",
            "CONNECT",
            "DISCONNECT",
            "DESC",
            "DESCRIBE",
            "SHOW",
            "SET",
            "CLEAR",
            "LIST",
            "RUN",
            "SPOOL",
            "COLUMN",
            "HOST",
            "START",
            "HELP",
        }
        return upper_first_word in sqlplus_cmds or cleaned.startswith("@")

    def is_plsql_start(self, first_line: str) -> bool:
        """Check if the buffer begins a PL/SQL block."""
        first_word = first_line.strip().split()[0].upper() if first_line.strip() else ""
        return first_word in {"DECLARE", "BEGIN"}

    def feed_line(self, line: str) -> tuple[bool, str, StatementType]:
        """Feed a line of input into the buffer.

        Returns:
            (is_complete, full_statement, statement_type)
        """
        stripped = line.strip()

        # Handle empty line input on multiline
        if not stripped and not self.is_empty:
            # In SQL*Plus, blank line stops statement input and stores in buffer
            full_stmt = self.get_full_text()
            self.clear()
            return True, full_stmt, StatementType.SQL

        # Handle SQL*Plus slash command to execute buffer
        if stripped == "/":
            full_stmt = self.get_full_text()
            stmt_type = (
                StatementType.PLSQL
                if self.is_plsql_start(self.lines[0] if self.lines else "")
                else StatementType.SQL
            )
            self.clear()
            return True, full_stmt, stmt_type

        # Check for first-line SQL*Plus command
        if self.is_empty and self.is_sqlplus_command(line):
            # SQL*Plus command is executed immediately
            clean_cmd = line.strip()
            if clean_cmd.endswith(";"):
                clean_cmd = clean_cmd[:-1].strip()
            return True, clean_cmd, StatementType.SQLPLUS

        # Process characters in line to track quoting, comments, and termination
        ends_with_semicolon = False
        chars = list(line)
        i = 0
        n = len(chars)

        while i < n:
            c = chars[i]

            # Check inside block comment
            if self.in_block_comment:
                if c == "*" and i + 1 < n and chars[i + 1] == "/":
                    self.in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue

            # Check inside single quote literal
            if self.in_single_quote:
                if c == "'":
                    # Check escaped single quote ('' in SQL)
                    if i + 1 < n and chars[i + 1] == "'":
                        i += 2
                        continue
                    self.in_single_quote = False
                i += 1
                continue

            # Check inside double quote identifier
            if self.in_double_quote:
                if c == '"':
                    self.in_double_quote = False
                i += 1
                continue

            # Not in any quote or comment:
            # Check for line comment --
            if c == "-" and i + 1 < n and chars[i + 1] == "-":
                # Rest of line is comment
                break

            # Check for start of block comment /*
            if c == "/" and i + 1 < n and chars[i + 1] == "*":
                self.in_block_comment = True
                i += 2
                continue

            if c == "'":
                self.in_single_quote = True
                i += 1
                continue

            if c == '"':
                self.in_double_quote = True
                i += 1
                continue

            if c == ";":
                # Verify if semicolon is at effective end of statement
                # (ignoring trailing whitespace and comments)
                rest = "".join(chars[i + 1 :]).strip()
                if not rest or rest.startswith("--"):
                    ends_with_semicolon = True
                    # Remove the semicolon from the line to store clean SQL
                    line = "".join(chars[:i]) + rest
                    break

            i += 1

        self.lines.append(line)

        if ends_with_semicolon and not self.in_single_quote and not self.in_block_comment:
            full_stmt = self.get_full_text().strip()
            self.clear()
            return True, full_stmt, StatementType.SQL

        return False, "", StatementType.UNKNOWN
