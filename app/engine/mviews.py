"""Materialized view snapshot management for OraCLI 10G."""

from datetime import datetime
from typing import Any

from app.database.adapter import DatabaseAdapter
from app.engine.errors import OracleError


class MaterializedViewManager:
    """Manages snapshot tables and manual refresh for Materialized Views."""

    def __init__(self, db_adapter: DatabaseAdapter) -> None:
        self.db_adapter = db_adapter

    def create_mview(self, name: str, select_sql: str, transpiled_select_sql: str) -> str:
        """Create a new materialized view physical snapshot table."""
        name_clean = name.strip().lower()

        # Check if table or mview already exists
        tables = self.db_adapter.get_tables()
        if name_clean in [t.lower() for t in tables]:
            raise OracleError(
                message=f'ORA-00955: name is already used by an existing object: "{name_clean}"',
                code="ORA-00955",
            )

        # Create physical snapshot table
        create_table_sql = f"CREATE TABLE {name_clean} AS {transpiled_select_sql};"
        self.db_adapter.execute(create_table_sql)

        # Record in catalog
        now = datetime.now().isoformat()
        self.db_adapter.execute(
            """
            INSERT OR REPLACE INTO _oracli_mviews (mview_name, query_sql, last_refreshed)
            VALUES (?, ?, ?);
            """,
            (name_clean, select_sql, now),
        )
        return "Materialized view created."

    def refresh_mview(self, name: str, transpiled_select_sql: str) -> str:
        """Refresh an existing materialized view snapshot."""
        name_clean = name.strip().lower()

        # Verify exists in catalog
        res = self.db_adapter.execute(
            "SELECT query_sql FROM _oracli_mviews WHERE mview_name = ?;",
            (name_clean,),
        )
        if not res.rows:
            raise OracleError(
                message=f'ORA-12003: materialized view "{name_clean}" does not exist',
                code="ORA-12003",
            )

        # Truncate snapshot and re-populate
        self.db_adapter.execute(f"DELETE FROM {name_clean};")
        self.db_adapter.execute(f"INSERT INTO {name_clean} {transpiled_select_sql};")

        # Update refresh timestamp
        now = datetime.now().isoformat()
        self.db_adapter.execute(
            "UPDATE _oracli_mviews SET last_refreshed = ? WHERE mview_name = ?;",
            (now, name_clean),
        )
        return "Materialized view refreshed."

    def drop_mview(self, name: str) -> str:
        """Drop a materialized view and its snapshot table."""
        name_clean = name.strip().lower()

        self.db_adapter.execute(f"DROP TABLE IF EXISTS {name_clean};")
        self.db_adapter.execute(
            "DELETE FROM _oracli_mviews WHERE mview_name = ?;",
            (name_clean,),
        )
        return "Materialized view dropped."

    def get_mviews(self) -> list[dict[str, Any]]:
        """List all registered materialized views."""
        res = self.db_adapter.execute(
            "SELECT mview_name, query_sql, last_refreshed FROM _oracli_mviews ORDER BY mview_name;"
        )
        return [
            {
                "name": row[0],
                "query_sql": row[1],
                "last_refreshed": row[2],
            }
            for row in res.rows
        ]
