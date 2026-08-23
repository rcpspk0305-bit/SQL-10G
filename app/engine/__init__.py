"""Execution engine package for OraCLI 10G."""

from app.engine.errors import OracleError, map_sqlite_error
from app.engine.executor import ExecutionOutput, SQLExecutor
from app.engine.oracle_types import OracleDataType, map_oracle_type_to_sqlite
from app.engine.translator import SQLCommandType, SQLTranslator, TranspiledQuery

__all__ = [
    "ExecutionOutput",
    "OracleDataType",
    "OracleError",
    "SQLCommandType",
    "SQLExecutor",
    "SQLTranslator",
    "TranspiledQuery",
    "map_oracle_type_to_sqlite",
    "map_sqlite_error",
]
