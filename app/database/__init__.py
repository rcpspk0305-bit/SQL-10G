"""Database adapter package for OraCLI 10G."""

from app.database.adapter import DatabaseAdapter, QueryResult
from app.database.sqlite_adapter import SQLiteAdapter

__all__ = ["DatabaseAdapter", "QueryResult", "SQLiteAdapter"]
