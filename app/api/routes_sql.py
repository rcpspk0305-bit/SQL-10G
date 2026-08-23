"""SQL Execution and Schema routes for OraCLI 10G Web API."""

import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.schemas import (
    ExecuteRequest,
    ExecuteResponse,
    SchemaTablesResponse,
    StatementResult,
    TableColumnInfo,
    TableInfo,
)
from app.cli.formatter import OutputFormatter
from app.cli.session import Session
from app.cli.sqlplus_commands import SQLPlusCommandEngine
from app.config.settings import settings
from app.database.sqlite_adapter import SQLiteAdapter
from app.engine.errors import OracleError
from app.engine.executor import SQLExecutor
from app.parser.buffer import InputBuffer, StatementType

router = APIRouter(tags=["SQL Engine"])

db_target = str(settings.db_path) if settings.db_path != ":memory:" else "data/oracli_web.db"
_shared_adapter = SQLiteAdapter(db_target)
_shared_adapter.connect()
_shared_executor = SQLExecutor(_shared_adapter)
_shared_formatter = OutputFormatter()
_shared_session = Session()
_shared_sqlplus = SQLPlusCommandEngine(_shared_session, _shared_adapter)

# Query history buffer
_query_history: list[dict[str, Any]] = []


def get_components() -> dict[str, Any]:
    return {
        "adapter": _shared_adapter,
        "executor": _shared_executor,
        "formatter": _shared_formatter,
        "session": _shared_session,
        "sqlplus": _shared_sqlplus,
    }


ComponentsDep = Annotated[dict[str, Any], Depends(get_components)]


def split_statements(sql_text: str) -> list[tuple[str, StatementType]]:
    """Split a SQL script into discrete executable statements with type detection."""
    buffer = InputBuffer()
    statements: list[tuple[str, StatementType]] = []

    for line in sql_text.splitlines():
        is_complete, stmt, stmt_type = buffer.feed_line(line)
        if is_complete and stmt.strip():
            statements.append((stmt.strip(), stmt_type))

    # If anything remains un-terminated in buffer
    if not buffer.is_empty:
        rem = buffer.get_full_text().strip()
        if rem:
            statements.append((rem, StatementType.SQL))
        buffer.clear()

    return statements


@router.post("/api/sql/execute", response_model=ExecuteResponse)
def execute_sql(req: ExecuteRequest, comp: ComponentsDep) -> ExecuteResponse:
    """Execute one or more Oracle SQL statements or SQL*Plus commands."""
    statements = split_statements(req.sql)
    if not statements:
        return ExecuteResponse(
            success=True,
            results=[],
            total_execution_time_ms=0.0,
            combined_formatted_output="",
        )

    results: list[StatementResult] = []
    combined_outputs: list[str] = []
    overall_start = time.perf_counter()
    all_success = True

    for stmt_str, stmt_type in statements:
        start_time = time.perf_counter()
        # Handle SQL*Plus commands
        if stmt_type == StatementType.SQLPLUS or buffer_is_sqlplus(stmt_str):
            cmd_res = comp["sqlplus"].execute(stmt_str)
            elapsed = (time.perf_counter() - start_time) * 1000.0
            out_text = cmd_res.output or "\n"
            combined_outputs.append(out_text)

            res = StatementResult(
                original_sql=stmt_str,
                translated_sql=stmt_str,
                command_type="SQLPLUS",
                is_query=False,
                is_error=False,
                columns=[],
                column_types=[],
                rows=[],
                row_count=0,
                feedback_message="",
                formatted_output=out_text,
                execution_time_ms=round(elapsed, 2),
            )
            results.append(res)
            continue

        # Handle SQL statements
        try:
            exec_out = comp["executor"].execute(stmt_str, comp["session"])
            elapsed = (time.perf_counter() - start_time) * 1000.0

            formatted = ""
            if exec_out.is_query:
                formatted = comp["formatter"].format_query_result(exec_out.result, comp["session"])
            else:
                feedback = exec_out.result.feedback_message
                formatted = f"\n{feedback}\n\n" if feedback else "\n"

            combined_outputs.append(formatted)

            res = StatementResult(
                original_sql=stmt_str,
                translated_sql=exec_out.transpiled.sqlite_sql,
                command_type=exec_out.transpiled.command_type.name,
                is_query=exec_out.is_query,
                is_error=False,
                columns=exec_out.result.columns,
                column_types=exec_out.result.column_types,
                rows=exec_out.result.rows,
                row_count=exec_out.result.row_count,
                feedback_message=exec_out.result.feedback_message,
                formatted_output=formatted,
                execution_time_ms=round(elapsed, 2),
            )
            results.append(res)

            _query_history.append({
                "sql": stmt_str,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_ms": round(elapsed, 2),
                "success": True,
                "rows": exec_out.result.row_count,
            })

        except OracleError as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            all_success = False
            err_text = f"\n{e}\n\n"
            combined_outputs.append(err_text)

            res = StatementResult(
                original_sql=stmt_str,
                translated_sql="",
                command_type="ERROR",
                is_query=False,
                is_error=True,
                columns=[],
                column_types=[],
                rows=[],
                row_count=0,
                feedback_message=str(e),
                formatted_output=err_text,
                execution_time_ms=round(elapsed, 2),
            )
            results.append(res)

            _query_history.append({
                "sql": stmt_str,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_ms": round(elapsed, 2),
                "success": False,
                "error": str(e),
                "rows": 0,
            })

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            all_success = False
            err_text = f"\nORA-00600: internal error code, arguments: [{e}]\n\n"
            combined_outputs.append(err_text)

            res = StatementResult(
                original_sql=stmt_str,
                translated_sql="",
                command_type="ERROR",
                is_query=False,
                is_error=True,
                columns=[],
                column_types=[],
                rows=[],
                row_count=0,
                feedback_message=str(e),
                formatted_output=err_text,
                execution_time_ms=round(elapsed, 2),
            )
            results.append(res)

    total_elapsed = (time.perf_counter() - overall_start) * 1000.0
    return ExecuteResponse(
        success=all_success,
        results=results,
        total_execution_time_ms=round(total_elapsed, 2),
        combined_formatted_output="".join(combined_outputs),
    )


def buffer_is_sqlplus(stmt: str) -> bool:
    first_word = stmt.strip().split()[0].upper() if stmt.strip() else ""
    return first_word in {
        "EXIT", "QUIT", "SHOW", "SET", "CLEAR", "HELP", "DESC", "DESCRIBE", "HOST"
    }


@router.get("/api/schema/tables", response_model=SchemaTablesResponse)
def get_schema_tables(comp: ComponentsDep) -> SchemaTablesResponse:
    """Discover all user tables and column metadata."""
    adapter: SQLiteAdapter = comp["adapter"]
    # Get all user tables (ignoring sqlite internal and DUAL)
    query = (
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'DUAL' "
        "ORDER BY name;"
    )
    res = adapter.execute(query)

    tables: list[TableInfo] = []
    for row in res.rows:
        tname = str(row[0])
        # Get column details via pragma
        col_res = adapter.execute(f"PRAGMA table_info({tname});")
        cols: list[TableColumnInfo] = []
        for col_row in col_res.rows:
            c_name = str(col_row[1])
            c_type = str(col_row[2]).upper() or "VARCHAR2"
            if "REAL" in c_type or "NUM" in c_type:
                ora_type = "NUMBER"
            elif "INT" in c_type:
                ora_type = "INTEGER"
            elif "TEXT" in c_type:
                ora_type = "VARCHAR2"
            else:
                ora_type = c_type

            not_null = bool(col_row[3])
            is_pk = bool(col_row[5])
            cols.append(
                TableColumnInfo(
                    name=c_name,
                    oracle_type=ora_type,
                    nullable=not not_null,
                    is_primary_key=is_pk,
                )
            )

        count_res = adapter.execute(f"SELECT COUNT(*) FROM {tname};")
        row_cnt = count_res.rows[0][0] if count_res.rows else 0

        tables.append(TableInfo(table_name=tname, columns=cols, row_count=row_cnt))

    return SchemaTablesResponse(tables=tables)


@router.get("/api/history")
def get_history() -> list[dict[str, Any]]:
    """Return recent query history."""
    return _query_history[::-1]


@router.post("/api/database/reset")
def reset_database(comp: ComponentsDep) -> dict[str, str]:
    """Drop all user tables for a clean slate."""
    adapter: SQLiteAdapter = comp["adapter"]
    query = (
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'DUAL';"
    )
    res = adapter.execute(query)
    for row in res.rows:
        tname = str(row[0])
        adapter.execute(f"DROP TABLE IF EXISTS {tname};")
    _query_history.clear()
    return {"status": "Database reset successfully."}
