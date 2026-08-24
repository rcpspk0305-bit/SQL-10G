"""Configuration settings for OraCLI 10G."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    """Application settings with persistent database storage by default."""

    app_name: str = "OraCLI 10G"
    version: str = "10.2.0.1.0"
    banner: str = "SQL*Plus: Release 10.2 Compatible Educational Edition"
    default_user: str = "SYSTEM"
    db_path: Path | str = os.getenv(
        "ORACLI_DB_PATH",
        str(Path(__file__).resolve().parent.parent.parent / "oracli_data.db"),
    )
    default_pagesize: int = 14
    default_linesize: int = 80
    default_heading: bool = True
    default_feedback: bool = True
    default_null: str = ""


settings = Settings()
