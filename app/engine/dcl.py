"""Educational Data Control Language (DCL) management for OraCLI 10G."""

from app.database.adapter import DatabaseAdapter
from app.engine.errors import OracleError


class DCLManager:
    """Manages educational GRANT/REVOKE privileges and authorization validation."""

    def __init__(self, db_adapter: DatabaseAdapter) -> None:
        self.db_adapter = db_adapter

    def grant(
        self,
        grantee: str,
        privileges: list[str],
        table_name: str,
        grantor: str = "SYSTEM",
    ) -> str:
        """Grant specified privileges on a table to a user."""
        grantee_clean = grantee.strip().upper()
        table_clean = table_name.strip().lower()
        grantor_clean = grantor.strip().upper()

        for priv in privileges:
            priv_clean = priv.strip().upper()
            self.db_adapter.execute(
                """
                INSERT OR REPLACE INTO _oracli_privileges (grantee, privilege, table_name, grantor)
                VALUES (?, ?, ?, ?);
                """,
                (grantee_clean, priv_clean, table_clean, grantor_clean),
            )
        return "Grant succeeded."

    def revoke(
        self,
        grantee: str,
        privileges: list[str],
        table_name: str,
    ) -> str:
        """Revoke specified privileges on a table from a user."""
        grantee_clean = grantee.strip().upper()
        table_clean = table_name.strip().lower()

        for priv in privileges:
            priv_clean = priv.strip().upper()
            if priv_clean == "ALL":
                self.db_adapter.execute(
                    """
                    DELETE FROM _oracli_privileges
                    WHERE grantee = ? AND table_name = ?;
                    """,
                    (grantee_clean, table_clean),
                )
            else:
                self.db_adapter.execute(
                    """
                    DELETE FROM _oracli_privileges
                    WHERE grantee = ? AND table_name = ? AND privilege = ?;
                    """,
                    (grantee_clean, table_clean, priv_clean),
                )
        return "Revoke succeeded."

    def check_permission(self, user: str, table_name: str, action: str) -> None:
        """Check if user has permission to perform action on table.

        Raises OracleError ORA-01031 if unauthorized.
        """
        user_clean = user.strip().upper()
        table_clean = table_name.strip().lower()
        action_clean = action.strip().upper()

        # SYSTEM or internal tables always have full access
        if user_clean in ("SYSTEM", "SYS") or table_clean.startswith("_") or table_clean == "dual":
            return

        res = self.db_adapter.execute(
            """
            SELECT COUNT(*) FROM _oracli_privileges
            WHERE grantee = ? AND table_name = ? AND (privilege = ? OR privilege = 'ALL');
            """,
            (user_clean, table_clean, action_clean),
        )

        has_priv = res.rows and res.rows[0][0] > 0
        if not has_priv:
            msg = (
                f'ORA-01031: insufficient privileges for user "{user_clean}" '
                f'on table "{table_clean}"'
            )
            raise OracleError(message=msg, code="ORA-01031")
