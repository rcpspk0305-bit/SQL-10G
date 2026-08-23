"""SQLite database adapter implementation for OraCLI 10G."""

import sqlite3
from datetime import datetime
from pathlib import Path
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


def _oracle_instr(s: Any, sub: Any, start: int = 1, occurrence: int = 1) -> int:
    """Emulate Oracle INSTR function."""
    if s is None or sub is None:
        return 0
    s_str = str(s)
    sub_str = str(sub)
    if not sub_str:
        return 0

    search_pos = max(0, start - 1)
    count = 0

    while count < occurrence:
        found = s_str.find(sub_str, search_pos)
        if found == -1:
            return 0
        count += 1
        if count == occurrence:
            return found + 1
        search_pos = found + 1

    return 0


def _oracle_trunc(val: Any, decimals: int = 0) -> Any:
    """Emulate Oracle TRUNC for numbers."""
    if val is None:
        return None
    try:
        factor = 10**decimals
        return int(float(val) * factor) / factor
    except Exception:
        return val


class SQLiteAdapter(DatabaseAdapter):
    """SQLite backend adapter supporting in-memory and on-disk databases."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._in_transaction: bool = False

    def connect(self) -> None:
        """Establish SQLite connection and initialize Oracle environment objects."""
        if self._conn is None:
            if self.db_path != ":memory:":
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            self._conn = sqlite3.connect(
                self.db_path,
                isolation_level=None,  # Explicit transaction management
                check_same_thread=False,
            )
            # Enable foreign keys
            self._conn.execute("PRAGMA foreign_keys = ON;")

            # Register Oracle compatibility functions
            self._conn.create_function("NVL", 2, _oracle_nvl)
            self._conn.create_function("SYSDATE", 0, _oracle_sysdate)
            self._conn.create_function("INSTR", 2, _oracle_instr)
            self._conn.create_function("INSTR", 3, _oracle_instr)
            self._conn.create_function("INSTR", 4, _oracle_instr)
            self._conn.create_function("TRUNC", 1, _oracle_trunc)
            self._conn.create_function("TRUNC", 2, _oracle_trunc)

            # Initialize DUAL and system catalog tables
            self._init_dual()
            self._init_system_catalogs()

    def _init_dual(self) -> None:
        """Initialize Oracle standard DUAL dummy table."""
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS DUAL (DUMMY TEXT);")
            cursor.execute("SELECT COUNT(*) FROM DUAL;")
            row = cursor.fetchone()
            if row and row[0] == 0:
                cursor.execute("INSERT INTO DUAL VALUES ('X');")
            cursor.close()

    def _init_system_catalogs(self) -> None:
        """Initialize internal system tables for DCL privileges and Materialized Views."""
        if self._conn:
            cursor = self._conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS _oracli_privileges (
                    grantee TEXT NOT NULL,
                    privilege TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    grantor TEXT NOT NULL,
                    PRIMARY KEY (grantee, privilege, table_name)
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS _oracli_mviews (
                    mview_name TEXT PRIMARY KEY,
                    query_sql TEXT NOT NULL,
                    last_refreshed TIMESTAMP NOT NULL
                );
                """
            )
            cursor.close()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def begin_transaction(self) -> None:
        """Start an explicit transaction."""
        if self._conn and not self._in_transaction:
            try:
                self._conn.execute("BEGIN TRANSACTION;")
                self._in_transaction = True
            except sqlite3.OperationalError:
                pass

    def commit(self) -> None:
        """Commit active transaction."""
        if self._conn:
            try:
                self._conn.execute("COMMIT;")
            except sqlite3.OperationalError:
                pass
            self._in_transaction = False

    def rollback(self) -> None:
        """Rollback active transaction."""
        if self._conn:
            try:
                self._conn.execute("ROLLBACK;")
            except sqlite3.OperationalError:
                pass
            self._in_transaction = False

    def savepoint(self, name: str) -> None:
        """Create a savepoint."""
        if self._conn:
            if not self._in_transaction:
                self.begin_transaction()
            self._conn.execute(f"SAVEPOINT {name};")

    def rollback_to_savepoint(self, name: str) -> None:
        """Rollback to a named savepoint."""
        if self._conn:
            self._conn.execute(f"ROLLBACK TO SAVEPOINT {name};")

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> QueryResult:
        """Execute a transpiled SQL query and capture rows and feedback."""
        if self._conn is None:
            self.connect()

        assert self._conn is not None

        # Oracle transactional behavior: DML starts an implicit transaction if none active
        first_word = sql.strip().split()[0].upper() if sql.strip() else ""
        if first_word in ("INSERT", "UPDATE", "DELETE") and not self._in_transaction:
            self.begin_transaction()

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
                column_types = ["TEXT" for _ in cursor.description]
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

    def get_tables(self) -> list[str]:
        """Return list of user-created tables (excluding system catalogs and DUAL)."""
        res = self.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table'
              AND name NOT LIKE '\\_%' ESCAPE '\\'
              AND UPPER(name) != 'DUAL'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        )
        return [row[0] for row in res.rows]

    def get_views(self) -> list[str]:
        """Return list of user-created views."""
        res = self.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='view'
              AND name NOT LIKE '\\_%' ESCAPE '\\'
            ORDER BY name;
            """
        )
        return [row[0] for row in res.rows]
