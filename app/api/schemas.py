"""API schemas for OraCLI 10G Web."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = "ok"
    app_name: str = "OraCLI 10G Web"
    version: str = "10.2.0.1.0"
    database: str = "SQLite (Oracle 10g Compatible)"


class ExecuteRequest(BaseModel):
    """SQL statement execution request."""

    sql: str = Field(..., description="Oracle SQL statement or script to execute")
    session_user: str = Field("SYSTEM", description="Current session user")


class StatementResult(BaseModel):
    """Result of executing a single SQL statement."""

    original_sql: str
    translated_sql: str
    command_type: str
    is_query: bool
    is_error: bool = False
    columns: list[str] = Field(default_factory=list)
    column_types: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    row_count: int = 0
    feedback_message: str = ""
    formatted_output: str = ""
    execution_time_ms: float = 0.0


class ExecuteResponse(BaseModel):
    """Aggregated response for SQL execution."""

    success: bool
    results: list[StatementResult] = Field(default_factory=list)
    total_execution_time_ms: float = 0.0
    combined_formatted_output: str = ""


class TableColumnInfo(BaseModel):
    """Column metadata for a table."""

    name: str
    oracle_type: str
    nullable: bool
    is_primary_key: bool


class TableInfo(BaseModel):
    """Table schema information."""

    table_name: str
    columns: list[TableColumnInfo] = Field(default_factory=list)
    row_count: int = 0


class SchemaTablesResponse(BaseModel):
    """Response containing discovered user tables."""

    tables: list[TableInfo] = Field(default_factory=list)
