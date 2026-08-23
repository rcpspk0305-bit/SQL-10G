"""Oracle datatype definitions and conversions."""

from enum import Enum


class OracleDataType(Enum):
    """Supported Oracle data types."""

    NUMBER = "NUMBER"
    VARCHAR2 = "VARCHAR2"
    CHAR = "CHAR"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    CLOB = "CLOB"
    BLOB = "BLOB"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"


# Mapping from Oracle data types to SQLite storage types
ORACLE_TO_SQLITE_TYPES = {
    "NUMBER": "NUMERIC",
    "NUMERIC": "NUMERIC",
    "DECIMAL": "NUMERIC",
    "VARCHAR2": "TEXT",
    "VARCHAR": "TEXT",
    "CHAR": "TEXT",
    "TEXT": "TEXT",
    "DATE": "TEXT",
    "TIMESTAMP": "TEXT",
    "CLOB": "TEXT",
    "BLOB": "BLOB",
    "INTEGER": "INTEGER",
    "INT": "INTEGER",
    "BIGINT": "INTEGER",
    "SMALLINT": "INTEGER",
    "FLOAT": "REAL",
    "REAL": "REAL",
    "DOUBLE": "REAL",
    "DOUBLE PRECISION": "REAL",
}


def map_oracle_type_to_sqlite(oracle_type: str) -> str:
    """Map an Oracle datatype string (e.g. VARCHAR2(50) or NUMBER(3,2)) to SQLite."""
    upper_type = oracle_type.strip().upper()
    base_type = upper_type.split("(")[0].strip()
    return ORACLE_TO_SQLITE_TYPES.get(base_type, "NUMERIC" if "NUM" in base_type else "TEXT")
