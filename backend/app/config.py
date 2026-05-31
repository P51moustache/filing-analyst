from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    anthropic_api_key: str
    # Claude model used for analysis. Defaults to the current flagship; override via
    # ANTHROPIC_MODEL to trade quality for cost (e.g. claude-sonnet-4-6, claude-haiku-4-5).
    # Structured outputs require a current model (Opus 4.8 / Sonnet 4.6 / Haiku 4.5).
    anthropic_model: str = "claude-opus-4-8"
    # The Anthropic SDK auto-retries 429/5xx with exponential backoff up to this many times.
    anthropic_max_retries: int = 4
    # Token budget for the filing text sent to the model. If a filing exceeds this it is
    # trimmed transparently (with a logged warning), never silently truncated.
    max_input_tokens: int = 200000
    max_file_size: int = 20971520  # 20MB
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    reports_dir: str = "./reports"
    # SQLite file backing the analysis job store. State survives restarts and is pruned
    # by age rather than kept in memory forever.
    db_path: str = "./analyses.db"
    # Analyses older than this (and their uploaded file + Excel report) are pruned on
    # startup so the job store, upload dir, and reports dir do not grow without bound.
    retention_hours: int = 168  # 7 days

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
