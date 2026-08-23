"""Abstract database adapter interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class QueryResult:
    """Represents the outcome of a database execution."""

    columns: list[str]
    column_types: list[str]
    rows: list[list[Any]]
    row_count: int
    feedback_message: str


class DatabaseAdapter(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to database."""

    @abstractmethod
    def close(self) -> None:
        """Close connection to database."""

    @abstractmethod
    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> QueryResult:
        """Execute a single SQL statement."""

    @abstractmethod
    def commit(self) -> None:
        """Commit current transaction."""

    @abstractmethod
    def rollback(self) -> None:
        """Rollback current transaction."""
