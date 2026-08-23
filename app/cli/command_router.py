"""Command routing and dispatching for OraCLI 10G."""

from dataclasses import dataclass

from app.cli.formatter import OutputFormatter
from app.cli.session import Session
from app.cli.sqlplus_commands import SQLPlusCommandEngine
from app.database.adapter import DatabaseAdapter
from app.engine.errors import OracleError
from app.engine.executor import SQLExecutor
from app.parser.buffer import StatementType


@dataclass
class RouterResult:
    """Outcome of processing a user statement."""

    output: str
    should_exit: bool = False
    is_error: bool = False


class CommandRouter:
    """Routes statements between SQL*Plus client command engine and SQL database executor."""

    def __init__(
        self,
        session: Session,
        adapter: DatabaseAdapter,
        executor: SQLExecutor | None = None,
        sqlplus_engine: SQLPlusCommandEngine | None = None,
        formatter: OutputFormatter | None = None,
    ) -> None:
        self.session = session
        self.adapter = adapter
        self.executor = executor or SQLExecutor(adapter)
        self.sqlplus_engine = sqlplus_engine or SQLPlusCommandEngine(session, adapter)
        self.formatter = formatter or OutputFormatter()

    def route(self, statement: str, stmt_type: StatementType) -> RouterResult:
        """Route a statement to the appropriate execution subsystem."""
        statement = statement.strip()
        if not statement:
            return RouterResult(output="")

        # Route SQL*Plus commands
        if stmt_type == StatementType.SQLPLUS:
            res = self.sqlplus_engine.execute(statement)
            return RouterResult(output=res.output, should_exit=res.should_exit)

        # Route SQL statements
        try:
            exec_output = self.executor.execute(statement, self.session)
            if exec_output.is_query:
                formatted = self.formatter.format_query_result(exec_output.result, self.session)
                return RouterResult(output=formatted)
            else:
                feedback = exec_output.result.feedback_message
                return RouterResult(output=f"\n{feedback}\n\n" if feedback else "\n")

        except OracleError as e:
            return RouterResult(output=f"{e}\n", is_error=True)
        except Exception as e:
            msg = f"ORA-00600: internal error code, arguments: [{e}]\n"
            return RouterResult(output=msg, is_error=True)
