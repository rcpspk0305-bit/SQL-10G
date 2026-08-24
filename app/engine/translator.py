"""Oracle SQL to SQLite transpiler using SQLGlot and custom AST transforms."""

import re
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
    RENAME_TABLE = auto()
    CREATE_VIEW = auto()
    DROP_VIEW = auto()
    CREATE_INDEX = auto()
    DROP_INDEX = auto()
    CREATE_MVIEW = auto()
    REFRESH_MVIEW = auto()
    DROP_MVIEW = auto()
    GRANT = auto()
    REVOKE = auto()
    COMMIT = auto()
    ROLLBACK = auto()
    SAVEPOINT = auto()
    ROLLBACK_TO_SAVEPOINT = auto()
    OTHER = auto()


@dataclass
class TranspiledQuery:
    """Represents a transpiled SQL query ready for SQLite execution."""

    original_sql: str
    sqlite_sql: str
    command_type: SQLCommandType
    target_object: str | None = None
    extra_metadata: dict | None = None


class SQLTranslator:
    """Translates Oracle SQL statements into SQLite compatible SQL."""

    def __init__(self) -> None:
        self.oracle_dialect = "oracle"
        self.sqlite_dialect = "sqlite"

    def detect_command_type(self, sql: str) -> SQLCommandType:
        """Quickly detect the primary SQL command type."""
        tokens = sql.strip().split()
        if not tokens:
            return SQLCommandType.OTHER

        first = tokens[0].upper()
        second = tokens[1].upper() if len(tokens) > 1 else ""
        third = tokens[2].upper() if len(tokens) > 2 else ""

        if first == "SELECT":
            return SQLCommandType.SELECT
        if first == "INSERT":
            return SQLCommandType.INSERT
        if first == "UPDATE":
            return SQLCommandType.UPDATE
        if first == "DELETE":
            return SQLCommandType.DELETE
        if first == "COMMIT":
            return SQLCommandType.COMMIT
        if first == "ROLLBACK":
            if second and second not in ("", ";", "WORK"):
                return SQLCommandType.ROLLBACK_TO_SAVEPOINT
            return SQLCommandType.ROLLBACK
        if first == "SAVEPOINT" or (first == "SAVE" and second == "POINT"):
            return SQLCommandType.SAVEPOINT
        if first == "GRANT":
            return SQLCommandType.GRANT
        if first == "REVOKE":
            return SQLCommandType.REVOKE
        if first == "REFRESH" and second == "MATERIALIZED" and third == "VIEW":
            return SQLCommandType.REFRESH_MVIEW
        if first == "CREATE":
            if second == "TABLE":
                return SQLCommandType.CREATE_TABLE
            if second == "VIEW" or (second == "OR" and third == "REPLACE"):
                return SQLCommandType.CREATE_VIEW
            if second == "MATERIALIZED" and third == "VIEW":
                return SQLCommandType.CREATE_MVIEW
            if second == "INDEX" or (second == "UNIQUE" and third == "INDEX"):
                return SQLCommandType.CREATE_INDEX
            return SQLCommandType.OTHER
        if first == "DROP":
            if second == "TABLE":
                return SQLCommandType.DROP_TABLE
            if second == "VIEW":
                return SQLCommandType.DROP_VIEW
            if second == "MATERIALIZED" and third == "VIEW":
                return SQLCommandType.DROP_MVIEW
            if second == "INDEX":
                return SQLCommandType.DROP_INDEX
            return SQLCommandType.OTHER
        if first == "ALTER":
            return SQLCommandType.ALTER_TABLE
        if first == "TRUNCATE":
            return SQLCommandType.TRUNCATE_TABLE
        if first == "RENAME":
            return SQLCommandType.RENAME_TABLE

        return SQLCommandType.OTHER

    def _parse_alter_table(self, sql: str) -> dict | None:
        """Parse Oracle ALTER TABLE statements including ADD column(s) and ADD CONSTRAINT."""
        m = re.match(r"^ALTER\s+TABLE\s+(\w+)\s+ADD\s*(.*)$", sql, re.IGNORECASE | re.DOTALL)
        if not m:
            return None
        tbl_name, body = m.groups()
        body = body.strip()
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1].strip()

        # Check if purely table-level constraint
        if re.match(
            r"^(CONSTRAINT\b|FOREIGN\s+KEY\b|PRIMARY\s+KEY\b|UNIQUE\b|CHECK\b)", body, re.IGNORECASE
        ):
            return {
                "table": tbl_name,
                "alter_type": "add_constraint",
                "constraint": body,
                "columns": [],
            }

        # Split by comma outside parentheses
        parts = []
        current = []
        paren_depth = 0
        for char in body:
            if char == "(":
                paren_depth += 1
                current.append(char)
            elif char == ")":
                paren_depth -= 1
                current.append(char)
            elif char == "," and paren_depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current:
            parts.append("".join(current).strip())

        cols = []
        constraints = []
        for p in parts:
            if re.match(
                r"^(CONSTRAINT\b|FOREIGN\s+KEY\b|PRIMARY\s+KEY\b|UNIQUE\b|CHECK\b)",
                p,
                re.IGNORECASE,
            ):
                constraints.append(p)
            else:
                tokens = p.split()
                if not tokens:
                    continue
                cname = tokens[0]
                raw_type = tokens[1] if len(tokens) > 1 else "VARCHAR2(50)"
                base_type = re.sub(r"\(.*?\)", "", raw_type).upper()
                sqlite_type = map_oracle_type_to_sqlite(base_type)
                cols.append({"name": cname, "type": sqlite_type, "full": p})

        return {
            "table": tbl_name,
            "alter_type": "add_columns",
            "columns": cols,
            "constraints": constraints,
        }

    def _transform_data_types(self, expression: exp.Expression) -> exp.Expression:
        """Walk AST and transform Oracle data types and functions for SQLite."""

        def transform(node: exp.Expression) -> exp.Expression:
            if isinstance(node, exp.DataType):
                type_name = (
                    node.this.value
                    if hasattr(node.this, "value")
                    else (node.this.name if hasattr(node.this, "name") else str(node.this))
                )
                mapped = map_oracle_type_to_sqlite(str(type_name))
                return exp.DataType.build(mapped)
            if isinstance(node, exp.Trunc):
                # Preserve TRUNC(val, decimals) for SQLite custom function
                args = [node.this]
                if node.args.get("decimals"):
                    args.append(node.args["decimals"])
                return exp.Anonymous(this="TRUNC", expressions=args)
            return node

        return expression.transform(transform)

    def transpile(self, sql: str) -> TranspiledQuery:
        """Transpile Oracle SQL string to SQLite SQL string."""
        cleaned_sql = sql.strip()
        if cleaned_sql.endswith(";"):
            cleaned_sql = cleaned_sql[:-1].strip()

        # Pre-normalize Oracle syntactic variations
        if re.match(r"^SAVE\s+POINT\b", cleaned_sql, re.IGNORECASE):
            cleaned_sql = re.sub(r"^SAVE\s+POINT\b", "SAVEPOINT", cleaned_sql, flags=re.IGNORECASE)
        if re.match(r"^DELETE\s+(?!FROM\b)", cleaned_sql, re.IGNORECASE):
            cleaned_sql = re.sub(r"^DELETE\s+", "DELETE FROM ", cleaned_sql, flags=re.IGNORECASE)

        cmd_type = self.detect_command_type(cleaned_sql)
        tokens = cleaned_sql.split()

        # Handle specialized commands that do not need full SQLGlot AST
        if cmd_type == SQLCommandType.COMMIT:
            return TranspiledQuery(cleaned_sql, "COMMIT;", cmd_type)
        if cmd_type == SQLCommandType.ROLLBACK:
            return TranspiledQuery(cleaned_sql, "ROLLBACK;", cmd_type)
        if cmd_type == SQLCommandType.SAVEPOINT:
            sp_name = (
                tokens[2]
                if len(tokens) > 2 and tokens[0].upper() == "SAVE" and tokens[1].upper() == "POINT"
                else (tokens[1] if len(tokens) > 1 else "sp1")
            )
            return TranspiledQuery(
                cleaned_sql,
                f"SAVEPOINT {sp_name};",
                cmd_type,
                target_object=sp_name,
            )
        if cmd_type == SQLCommandType.ROLLBACK_TO_SAVEPOINT:
            # ROLLBACK [TO] [SAVEPOINT] <name>
            if len(tokens) > 3 and tokens[1].upper() == "TO" and tokens[2].upper() == "SAVEPOINT":
                sp_name = tokens[3]
            elif len(tokens) > 2 and tokens[1].upper() == "TO":
                sp_name = tokens[2]
            elif len(tokens) > 1 and tokens[1].upper() not in ("TO", "WORK"):
                sp_name = tokens[1]
            else:
                sp_name = "sp1"
            return TranspiledQuery(
                cleaned_sql,
                f"ROLLBACK TO SAVEPOINT {sp_name};",
                cmd_type,
                target_object=sp_name,
            )

        if cmd_type == SQLCommandType.ALTER_TABLE:
            alter_info = self._parse_alter_table(cleaned_sql)
            if alter_info:
                target_table = alter_info["table"]
                if alter_info["alter_type"] == "add_constraint":
                    return TranspiledQuery(
                        cleaned_sql,
                        f"SELECT 1 FROM {target_table} LIMIT 0;",
                        cmd_type,
                        target_object=target_table,
                        extra_metadata=alter_info,
                    )
                elif alter_info["alter_type"] == "add_columns":
                    cols = alter_info["columns"]
                    if cols:
                        stmts = [
                            f"ALTER TABLE {target_table} ADD COLUMN {c['name']} {c['type']};"
                            for c in cols
                        ]
                        return TranspiledQuery(
                            cleaned_sql,
                            stmts[0],
                            cmd_type,
                            target_object=target_table,
                            extra_metadata={
                                "alter_type": "add_columns",
                                "statements": stmts,
                                "table": target_table,
                            },
                        )

        if cmd_type == SQLCommandType.CREATE_INDEX:
            # CREATE [UNIQUE] INDEX <name> ON <table> (<cols>)
            # SQLite does not support NULLS LAST / FIRST in indices
            idx_sql = re.sub(r"\s+NULLS\s+(LAST|FIRST)", "", cleaned_sql, flags=re.IGNORECASE)
            idx_name = tokens[2] if tokens[1].upper() == "INDEX" else tokens[3]
            return TranspiledQuery(
                cleaned_sql,
                idx_sql + ";",
                cmd_type,
                target_object=idx_name,
            )

        if cmd_type == SQLCommandType.DROP_INDEX:
            idx_name = tokens[2] if len(tokens) > 2 else tokens[1]
            return TranspiledQuery(
                cleaned_sql,
                f"DROP INDEX IF EXISTS {idx_name};",
                cmd_type,
                target_object=idx_name,
            )

        if cmd_type == SQLCommandType.TRUNCATE_TABLE:
            table_name = tokens[2] if len(tokens) > 2 else tokens[1]
            return TranspiledQuery(
                cleaned_sql,
                f"DELETE FROM {table_name};",
                cmd_type,
                target_object=table_name,
            )

        if cmd_type == SQLCommandType.RENAME_TABLE:
            old_table = tokens[1]
            new_table = tokens[3] if len(tokens) > 3 else tokens[2]
            return TranspiledQuery(
                cleaned_sql,
                f"ALTER TABLE {old_table} RENAME TO {new_table};",
                cmd_type,
                target_object=new_table,
            )

        if cmd_type == SQLCommandType.GRANT:
            m = re.match(r"GRANT\s+(.+?)\s+ON\s+(\w+)\s+TO\s+(\w+)", cleaned_sql, re.IGNORECASE)
            if m:
                privs_str, table_name, user = m.groups()
                privs = [p.strip().upper() for p in privs_str.split(",")]
                return TranspiledQuery(
                    cleaned_sql,
                    cleaned_sql,
                    cmd_type,
                    target_object=table_name,
                    extra_metadata={
                        "privileges": privs,
                        "grantee": user,
                        "table_name": table_name,
                    },
                )

        if cmd_type == SQLCommandType.REVOKE:
            m = re.match(r"REVOKE\s+(.+?)\s+ON\s+(\w+)\s+FROM\s+(\w+)", cleaned_sql, re.IGNORECASE)
            if m:
                privs_str, table_name, user = m.groups()
                privs = [p.strip().upper() for p in privs_str.split(",")]
                return TranspiledQuery(
                    cleaned_sql,
                    cleaned_sql,
                    cmd_type,
                    target_object=table_name,
                    extra_metadata={
                        "privileges": privs,
                        "grantee": user,
                        "table_name": table_name,
                    },
                )

        if cmd_type == SQLCommandType.CREATE_MVIEW:
            pattern = r"CREATE\s+MATERIALIZED\s+VIEW\s+(\w+)\s+AS\s+(.+)"
            m = re.match(pattern, cleaned_sql, re.IGNORECASE | re.DOTALL)
            if m:
                mview_name, select_sql = m.groups()
                select_transpiled = self.transpile(select_sql)
                return TranspiledQuery(
                    cleaned_sql,
                    "",
                    cmd_type,
                    target_object=mview_name,
                    extra_metadata={
                        "mview_name": mview_name,
                        "select_sql": select_sql,
                        "transpiled_select_sql": select_transpiled.sqlite_sql,
                    },
                )

        if cmd_type == SQLCommandType.REFRESH_MVIEW:
            mview_name = tokens[3] if len(tokens) > 3 else tokens[1]
            return TranspiledQuery(
                cleaned_sql,
                "",
                cmd_type,
                target_object=mview_name,
                extra_metadata={"mview_name": mview_name},
            )

        if cmd_type == SQLCommandType.DROP_MVIEW:
            mview_name = tokens[3] if len(tokens) > 3 else tokens[1]
            return TranspiledQuery(
                cleaned_sql,
                "",
                cmd_type,
                target_object=mview_name,
                extra_metadata={"mview_name": mview_name},
            )

        # Standard SQL transpilation via SQLGlot
        try:
            parsed = sqlglot.parse_one(cleaned_sql, read=self.oracle_dialect)
        except Exception as e:
            raise ORA00933SQLCommandNotProperlyEnded(str(e)) from e

        # Extract target object
        target_obj = None
        if isinstance(parsed, exp.Create):
            if parsed.this and hasattr(parsed.this, "name"):
                target_obj = parsed.this.name
        elif isinstance(parsed, (exp.Insert, exp.Update, exp.Delete)):
            if parsed.this and hasattr(parsed.this, "name"):
                target_obj = parsed.this.name
        elif isinstance(parsed, exp.Drop):
            if parsed.this and hasattr(parsed.this, "name"):
                target_obj = parsed.this.name
        elif isinstance(parsed, exp.Select):
            from_clause = parsed.find(exp.From)
            if from_clause and from_clause.this and hasattr(from_clause.this, "name"):
                target_obj = from_clause.this.name

        # Transform Oracle datatypes to SQLite equivalents
        transformed = self._transform_data_types(parsed)

        # Transpile to SQLite dialect
        sqlite_sql = transformed.sql(dialect=self.sqlite_dialect)

        # Clean up SQLite unsupported constructs
        sqlite_sql = re.sub(r"\s+NULLS\s+(LAST|FIRST)", "", sqlite_sql, flags=re.IGNORECASE)

        return TranspiledQuery(
            original_sql=cleaned_sql,
            sqlite_sql=sqlite_sql,
            command_type=cmd_type,
            target_object=target_obj,
        )
