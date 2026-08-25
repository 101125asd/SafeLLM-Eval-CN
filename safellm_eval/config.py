from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "safellm_eval.db"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "latest_report.md"


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    timeout: int


def load_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv(PROJECT_ROOT / ".env")
    return Settings(
        api_key=os.getenv("LLM_API_KEY", ""),
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        model=os.getenv("LLM_MODEL", "deepseek-v4-flash"),
        timeout=int(os.getenv("LLM_TIMEOUT", "60")),
    )
