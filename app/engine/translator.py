"""Oracle SQL to SQLite transpiler using SQLGlot and custom AST transforms."""

from dataclasses import dataclass
from enum import Enum, auto

import sqlglot
from sqlglot import exp

from app.engine.errors import ORA00933SQLCommandNotProperlyEnded
from app.engine.oracle_types import map_oracle_type_to_sqlite


class SQLCommandType(Enum):
    """Categorized SQL command type."""

    SELECT = auto()
    INSERT = auto()
    UPDATE = auto()
    DELETE = auto()
    CREATE_TABLE = auto()
    ALTER_TABLE = auto()
    DROP_TABLE = auto()
    TRUNCATE_TABLE = auto()
    CREATE_VIEW = auto()
    DROP_VIEW = auto()
    CREATE_INDEX = auto()
    DROP_INDEX = auto()
    OTHER = auto()


@dataclass
class TranspiledQuery:
    """Represents a transpiled SQL query ready for SQLite execution."""

    original_sql: str
    sqlite_sql: str
    command_type: SQLCommandType
    target_object: str | None = None


class SQLTranslator:
    """Translates Oracle SQL statements into SQLite compatible SQL."""

    def __init__(self) -> None:
        self.oracle_dialect = "oracle"
        self.sqlite_dialect = "sqlite"

    def detect_command_type(self, sql: str) -> SQLCommandType:
        """Quickly detect the primary SQL command type."""
        first_token = sql.strip().split()[0].upper() if sql.strip() else ""
        match first_token:
            case "SELECT":
                return SQLCommandType.SELECT
            case "INSERT":
                return SQLCommandType.INSERT
            case "UPDATE":
                return SQLCommandType.UPDATE
            case "DELETE":
                return SQLCommandType.DELETE
            case "CREATE":
                tokens = sql.strip().split()
                if len(tokens) > 1:
                    second = tokens[1].upper()
                    if second == "TABLE":
                        return SQLCommandType.CREATE_TABLE
                    if second == "VIEW":
                        return SQLCommandType.CREATE_VIEW
                    if second == "INDEX" or (
                        len(tokens) > 2
                        and tokens[1].upper() == "UNIQUE"
                        and tokens[2].upper() == "INDEX"
                    ):
                        return SQLCommandType.CREATE_INDEX
                return SQLCommandType.OTHER
            case "DROP":
                tokens = sql.strip().split()
                if len(tokens) > 1:
                    second = tokens[1].upper()
                    if second == "TABLE":
                        return SQLCommandType.DROP_TABLE
                    if second == "VIEW":
                        return SQLCommandType.DROP_VIEW
                    if second == "INDEX":
                        return SQLCommandType.DROP_INDEX
                return SQLCommandType.OTHER
            case "ALTER":
                return SQLCommandType.ALTER_TABLE
            case "TRUNCATE":
                return SQLCommandType.TRUNCATE_TABLE
            case _:
                return SQLCommandType.OTHER

    def _transform_data_types(self, expression: exp.Expression) -> exp.Expression:
        """Walk AST and transform Oracle data types to SQLite types."""

        def transform(node: exp.Expression) -> exp.Expression:
            if isinstance(node, exp.DataType):
                type_name = (
                    node.this.value
                    if hasattr(node.this, "value")
                    else (node.this.name if hasattr(node.this, "name") else str(node.this))
                )
                mapped = map_oracle_type_to_sqlite(str(type_name))
                return exp.DataType.build(mapped)
            return node

        return expression.transform(transform)

    def transpile(self, sql: str) -> TranspiledQuery:
        """Transpile Oracle SQL string to SQLite SQL string."""
        cleaned_sql = sql.strip()
        if cleaned_sql.endswith(";"):
            cleaned_sql = cleaned_sql[:-1].strip()

        cmd_type = self.detect_command_type(cleaned_sql)

        try:
            parsed = sqlglot.parse_one(cleaned_sql, read=self.oracle_dialect)
        except Exception as e:
            # Check if sqlglot error can be sanitized or fallback to basic parser
            raise ORA00933SQLCommandNotProperlyEnded(str(e)) from e

        # Extract target object if applicable
        target_obj = None
        if isinstance(parsed, exp.Create):
            if parsed.this and hasattr(parsed.this, "name"):
                target_obj = parsed.this.name
        elif isinstance(parsed, exp.Insert):
            if parsed.this and hasattr(parsed.this, "name"):
                target_obj = parsed.this.name
        elif isinstance(parsed, exp.Drop):
            if parsed.this and hasattr(parsed.this, "name"):
                target_obj = parsed.this.name

        # Transform Oracle datatypes to SQLite equivalents
        transformed = self._transform_data_types(parsed)

        # Transpile to SQLite dialect
        sqlite_sql = transformed.sql(dialect=self.sqlite_dialect)

        return TranspiledQuery(
            original_sql=cleaned_sql,
            sqlite_sql=sqlite_sql,
            command_type=cmd_type,
            target_object=target_obj,
        )
