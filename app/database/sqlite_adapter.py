"""SQLite database adapter implementation for OraCLI 10G."""

import sqlite3
from datetime import datetime
from typing import Any

from app.database.adapter import DatabaseAdapter, QueryResult
from app.engine.errors import map_sqlite_error


def _oracle_nvl(val1: Any, val2: Any) -> Any:
    """Emulate Oracle NVL function."""
    return val2 if val1 is None else val1


def _oracle_sysdate() -> str:
    """Emulate Oracle SYSDATE function in DD-MON-YY format."""
    now = datetime.now()
    month_abbr = now.strftime("%b").upper()
    return f"{now.strftime('%d')}-{month_abbr}-{now.strftime('%y')}"


class SQLiteAdapter(DatabaseAdapter):
    """SQLite backend adapter supporting in-memory and on-disk databases."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Establish SQLite connection and initialize Oracle environment objects."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path,
                isolation_level=None,  # Autocommit mode by default; explicit transactions supported
                check_same_thread=False,
            )
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON;")

            # Register Oracle compatibility functions
            self._conn.create_function("NVL", 2, _oracle_nvl)
            self._conn.create_function("SYSDATE", 0, _oracle_sysdate)

            # Initialize DUAL table
            self._init_dual()

    def _init_dual(self) -> None:
        """Initialize Oracle standard DUAL dummy table."""
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS DUAL (DUMMY TEXT);")
            cursor.execute("SELECT COUNT(*) FROM DUAL;")
            row = cursor.fetchone()
            if row and row[0] == 0:
                cursor.execute("INSERT INTO DUAL VALUES ('X');")

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def commit(self) -> None:
        """Commit transaction."""
        if self._conn:
            self._conn.commit()

    def rollback(self) -> None:
        """Rollback transaction."""
        if self._conn:
            self._conn.rollback()

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> QueryResult:
        """Execute a transpiled SQL query and capture rows and feedback."""
        if self._conn is None:
            self.connect()

        assert self._conn is not None
        cursor = self._conn.cursor()

        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            columns: list[str] = []
            column_types: list[str] = []
            rows: list[list[Any]] = []

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                column_types = ["TEXT" for _ in cursor.description]  # Default fallback type
                rows = [list(row) for row in cursor.fetchall()]

            row_count = cursor.rowcount if cursor.rowcount >= 0 else len(rows)

            return QueryResult(
                columns=columns,
                column_types=column_types,
                rows=rows,
                row_count=row_count,
                feedback_message="",
            )

        except sqlite3.Error as e:
            raise map_sqlite_error(e) from e
        finally:
            cursor.close()
