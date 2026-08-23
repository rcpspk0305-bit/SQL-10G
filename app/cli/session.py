"""Session state management for OraCLI 10G."""

from dataclasses import dataclass, field
from typing import Any

from app.config.settings import settings


@dataclass
class Session:
    """Represents an active SQL*Plus user session."""

    user: str = field(default_factory=lambda: settings.default_user)
    pagesize: int = field(default_factory=lambda: settings.default_pagesize)
    linesize: int = field(default_factory=lambda: settings.default_linesize)
    heading: bool = field(default_factory=lambda: settings.default_heading)
    feedback: bool = field(default_factory=lambda: settings.default_feedback)
    null_value: str = field(default_factory=lambda: settings.default_null)
    echo: bool = False
    verify: bool = True
    serveroutput: bool = True
    spool_file: str | None = None
    column_formats: dict[str, dict[str, Any]] = field(default_factory=dict)
    last_sql: str | None = None
