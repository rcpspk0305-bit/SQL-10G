"""Query execution coordinator for OraCLI 10G."""

from dataclasses import dataclass

from app.cli.session import Session
from app.database.adapter import DatabaseAdapter, QueryResult
from app.engine.translator import SQLCommandType, SQLTranslator, TranspiledQuery


@dataclass
class ExecutionOutput:
    """Consolidated output of a SQL execution."""

    transpiled: TranspiledQuery
    result: QueryResult
    is_query: bool


class SQLExecutor:
    """Coordinates transpilation, database execution, and Oracle feedback generation."""

    def __init__(self, adapter: DatabaseAdapter, translator: SQLTranslator | None = None) -> None:
        self.adapter = adapter
        self.translator = translator or SQLTranslator()

    def execute(self, sql: str, session: Session) -> ExecutionOutput:
        """Transpile and execute an Oracle SQL statement."""
        transpiled = self.translator.transpile(sql)
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
