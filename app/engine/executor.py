"""Query execution coordinator for OraCLI 10G."""

from dataclasses import dataclass

from app.cli.session import Session
from app.database.adapter import DatabaseAdapter, QueryResult
from app.engine.dcl import DCLManager
from app.engine.mviews import MaterializedViewManager
from app.engine.translator import SQLCommandType, SQLTranslator, TranspiledQuery


@dataclass
class ExecutionOutput:
    """Consolidated output of a SQL execution."""

    transpiled: TranspiledQuery
    result: QueryResult
    is_query: bool


class SQLExecutor:
    """Coordinates transpilation, database execution, DCL/TCL, and Oracle feedback generation."""

    def __init__(self, adapter: DatabaseAdapter, translator: SQLTranslator | None = None) -> None:
        self.adapter = adapter
        self.translator = translator or SQLTranslator()
        self.dcl_mgr = DCLManager(adapter)
        self.mview_mgr = MaterializedViewManager(adapter)

    def execute(self, sql: str, session: Session) -> ExecutionOutput:
        """Transpile and execute an Oracle SQL statement with authorization and transactions."""
        transpiled = self.translator.transpile(sql)

        # 1. DCL Authorization Check for non-SYSTEM users on DML actions
        if transpiled.command_type in (
            SQLCommandType.SELECT,
            SQLCommandType.INSERT,
            SQLCommandType.UPDATE,
            SQLCommandType.DELETE,
        ):
            action_map = {
                SQLCommandType.SELECT: "SELECT",
                SQLCommandType.INSERT: "INSERT",
                SQLCommandType.UPDATE: "UPDATE",
                SQLCommandType.DELETE: "DELETE",
            }
            if transpiled.target_object:
                self.dcl_mgr.check_permission(
                    user=session.user,
                    table_name=transpiled.target_object,
                    action=action_map[transpiled.command_type],
                )

        # 2. Transaction Control (TCL) Handling
        if transpiled.command_type == SQLCommandType.COMMIT:
            self.adapter.commit()
            query_result = QueryResult([], [], [], 0, "Commit complete.")
            return ExecutionOutput(transpiled, query_result, is_query=False)

        if transpiled.command_type == SQLCommandType.ROLLBACK:
            self.adapter.rollback()
            query_result = QueryResult([], [], [], 0, "Rollback complete.")
            return ExecutionOutput(transpiled, query_result, is_query=False)

        if transpiled.command_type == SQLCommandType.SAVEPOINT:
            sp_name = transpiled.target_object or "sp1"
            if hasattr(self.adapter, "savepoint"):
                self.adapter.savepoint(sp_name)
            query_result = QueryResult([], [], [], 0, "Savepoint created.")
            return ExecutionOutput(transpiled, query_result, is_query=False)

        if transpiled.command_type == SQLCommandType.ROLLBACK_TO_SAVEPOINT:
            sp_name = transpiled.target_object or "sp1"
            if hasattr(self.adapter, "rollback_to_savepoint"):
                self.adapter.rollback_to_savepoint(sp_name)
            query_result = QueryResult([], [], [], 0, "Rollback complete.")
            return ExecutionOutput(transpiled, query_result, is_query=False)

        # 3. Data Control Language (DCL) Handling
        if transpiled.command_type == SQLCommandType.GRANT:
            meta = transpiled.extra_metadata or {}
            feedback = self.dcl_mgr.grant(
                grantee=meta.get("grantee", ""),
                privileges=meta.get("privileges", []),
                table_name=meta.get("table_name", ""),
                grantor=session.user,
            )
            query_result = QueryResult([], [], [], 0, feedback)
            return ExecutionOutput(transpiled, query_result, is_query=False)

        if transpiled.command_type == SQLCommandType.REVOKE:
            meta = transpiled.extra_metadata or {}
            feedback = self.dcl_mgr.revoke(
                grantee=meta.get("grantee", ""),
                privileges=meta.get("privileges", []),
                table_name=meta.get("table_name", ""),
            )
            query_result = QueryResult([], [], [], 0, feedback)
            return ExecutionOutput(transpiled, query_result, is_query=False)

        # 4. Materialized Views Subsystem Handling
        if transpiled.command_type == SQLCommandType.CREATE_MVIEW:
            meta = transpiled.extra_metadata or {}
            feedback = self.mview_mgr.create_mview(
                name=meta.get("mview_name", ""),
                select_sql=meta.get("select_sql", ""),
                transpiled_select_sql=meta.get("transpiled_select_sql", ""),
            )
            query_result = QueryResult([], [], [], 0, feedback)
            return ExecutionOutput(transpiled, query_result, is_query=False)

        if transpiled.command_type == SQLCommandType.REFRESH_MVIEW:
            meta = transpiled.extra_metadata or {}
            mview_name = meta.get("mview_name", "")
            cat = self.adapter.execute(
                "SELECT query_sql FROM _oracli_mviews WHERE mview_name = ?;",
                (mview_name.lower(),),
            )
            if not cat.rows:
                feedback = self.mview_mgr.refresh_mview(mview_name, "")
            else:
                select_sql = cat.rows[0][0]
                select_transpiled = self.translator.transpile(select_sql)
                feedback = self.mview_mgr.refresh_mview(mview_name, select_transpiled.sqlite_sql)

            query_result = QueryResult([], [], [], 0, feedback)
            return ExecutionOutput(transpiled, query_result, is_query=False)

        if transpiled.command_type == SQLCommandType.DROP_MVIEW:
            meta = transpiled.extra_metadata or {}
            feedback = self.mview_mgr.drop_mview(meta.get("mview_name", ""))
            query_result = QueryResult([], [], [], 0, feedback)
            return ExecutionOutput(transpiled, query_result, is_query=False)

        # 5. Multi-statement or Specialized ALTER TABLE Execution
        if transpiled.command_type == SQLCommandType.ALTER_TABLE:
            meta = transpiled.extra_metadata or {}
            alter_type = meta.get("alter_type")
            if alter_type == "add_columns":
                stmts = meta.get("statements", [transpiled.sqlite_sql])
                for stmt in stmts:
                    self.adapter.execute(stmt)
                feedback = self._generate_feedback(transpiled.command_type, 0)
                query_result = QueryResult([], [], [], 0, feedback)
                return ExecutionOutput(transpiled, query_result, is_query=False)
            elif alter_type == "add_constraint":
                self.adapter.execute(transpiled.sqlite_sql)
                feedback = self._generate_feedback(transpiled.command_type, 0)
                query_result = QueryResult([], [], [], 0, feedback)
                return ExecutionOutput(transpiled, query_result, is_query=False)

        # 6. Standard SQL Execution via Database Adapter
        query_result = self.adapter.execute(transpiled.sqlite_sql)

        # Generate Oracle SQL*Plus feedback message for DDL/DML
        feedback = self._generate_feedback(transpiled.command_type, query_result.row_count)
        query_result.feedback_message = feedback

        is_query = transpiled.command_type == SQLCommandType.SELECT
        return ExecutionOutput(
            transpiled=transpiled,
            result=query_result,
            is_query=is_query,
        )

    def _generate_feedback(self, cmd_type: SQLCommandType, row_count: int) -> str:
        """Generate canonical Oracle 10g feedback messages."""
        match cmd_type:
            case SQLCommandType.CREATE_TABLE:
                return "Table created."
            case SQLCommandType.DROP_TABLE:
                return "Table dropped."
            case SQLCommandType.ALTER_TABLE:
                return "Table altered."
            case SQLCommandType.RENAME_TABLE:
                return "Table renamed."
            case SQLCommandType.CREATE_VIEW:
                return "View created."
            case SQLCommandType.DROP_VIEW:
                return "View dropped."
            case SQLCommandType.CREATE_INDEX:
                return "Index created."
            case SQLCommandType.DROP_INDEX:
                return "Index dropped."
            case SQLCommandType.TRUNCATE_TABLE:
                return "Table truncated."
            case SQLCommandType.INSERT:
                return "1 row created." if row_count == 1 else f"{row_count} rows created."
            case SQLCommandType.UPDATE:
                return "1 row updated." if row_count == 1 else f"{row_count} rows updated."
            case SQLCommandType.DELETE:
                return "1 row deleted." if row_count == 1 else f"{row_count} rows deleted."
            case SQLCommandType.SELECT:
                return ""  # SELECT feedback is displayed after row listing
            case _:
                return "Statement processed."
