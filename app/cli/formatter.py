"""SQL*Plus-style output formatter for queries and command feedback."""

from decimal import Decimal
from typing import Any

from app.cli.session import Session
from app.database.adapter import QueryResult


class OutputFormatter:
    """Formats query results and messages in authentic Oracle SQL*Plus 10g style."""

    def __init__(self, session: Session | None = None) -> None:
        self.session = session or Session()

    @staticmethod
    def _is_numeric(val: Any) -> bool:
        """Determine if a value or string represents a number."""
        if val is None:
            return False
        if isinstance(val, (int, float, Decimal)):
            return True
        if isinstance(val, str):
            try:
                float(val)
                return True
            except ValueError:
                return False
        return False

    @staticmethod
    def _format_cell_value(val: Any, session: Session) -> tuple[str, bool]:
        """Convert cell value to string and return (formatted_string, is_numeric)."""
        if val is None:
            return session.null_value, False
        if isinstance(val, float):
            if val.is_integer():
                return str(int(val)), True
            return str(val), True
        if isinstance(val, int):
            return str(val), True
        if isinstance(val, str):
            try:
                float(val)
                return val, True
            except ValueError:
                return val, False
        return str(val), False

    def format_query(self, result: QueryResult, session: Session | None = None) -> str:
        """Convenience alias for format_query_result."""
        return self.format_query_result(result, session or self.session)

    def format_query_result(self, result: QueryResult, session: Session | None = None) -> str:
        """Render a QueryResult as a SQL*Plus formatted text table."""
        active_session = session or self.session

        if not result.columns:
            return ""

        if not result.rows:
            return "no rows selected\n"

        num_cols = len(result.columns)
        col_names = [col.upper() for col in result.columns]

        col_is_numeric = [True] * num_cols
        col_widths = [len(name) for name in col_names]

        formatted_rows: list[list[str]] = []
        for row in result.rows:
            formatted_row: list[str] = []
            for col_idx in range(num_cols):
                val = row[col_idx] if col_idx < len(row) else None
                cell_str, is_num = self._format_cell_value(val, active_session)
                formatted_row.append(cell_str)

                if val is not None and not is_num:
                    col_is_numeric[col_idx] = False

                col_widths[col_idx] = max(col_widths[col_idx], len(cell_str))
            formatted_rows.append(formatted_row)

        for idx in range(num_cols):
            if col_is_numeric[idx]:
                col_widths[idx] = max(col_widths[idx], len(col_names[idx]), 6)

        output_lines: list[str] = [""]

        def build_header() -> list[str]:
            if not active_session.heading:
                return []
            header_cells = []
            dash_cells = []
            for idx in range(num_cols):
                width = col_widths[idx]
                name = col_names[idx]
                if col_is_numeric[idx]:
                    header_cells.append(name.rjust(width))
                else:
                    header_cells.append(name.ljust(width))
                dash_cells.append("-" * width)
            return [" ".join(header_cells), " ".join(dash_cells)]

        header_block = build_header()
        if header_block:
            output_lines.extend(header_block)

        pagesize = active_session.pagesize if active_session.pagesize > 0 else 0
        rows_printed_on_page = 0

        for _row_idx, row in enumerate(formatted_rows):
            if pagesize > 0 and rows_printed_on_page >= pagesize and active_session.heading:
                output_lines.append("")
                output_lines.extend(header_block)
                rows_printed_on_page = 0

            row_cells = []
            for col_idx in range(num_cols):
                cell_str = row[col_idx]
                width = col_widths[col_idx]
                if col_is_numeric[col_idx]:
                    row_cells.append(cell_str.rjust(width))
                else:
                    row_cells.append(cell_str.ljust(width))
            output_lines.append(" ".join(row_cells))
            rows_printed_on_page += 1

        if active_session.feedback:
            output_lines.append("")
            count = len(result.rows)
            feedback_str = "1 row selected." if count == 1 else f"{count} rows selected."
            output_lines.append(feedback_str)

        return "\n".join(output_lines) + "\n"
