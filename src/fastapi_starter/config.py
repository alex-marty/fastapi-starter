from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastapi_starter.logging import LoggingFormat, LoggingLevel, configure_logging
from fastapi_starter.utils import git_root_path


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file_encoding="utf-8",
        env_file=".env",
    )

    ENABLE_DEBUG: bool = False
    STORAGE_DIR: Path = git_root_path(Path(__file__).parent) / ".storage"

    # Logging settings
    # Global logging level
    LOGGING_LEVEL: LoggingLevel = "WARNING"
    # Specific logging level for SQL queries, for debugging purposes
    # Corresponds to the `sqlalchemy.engine` logger
    # https://docs.sqlalchemy.org/en/20/core/engines.html#configuring-logging
    LOGGING_SQL_LEVEL: LoggingLevel = "WARNING"
    # Custom levels for specific loggers, override all previous settings
    LOGGING_LOGGER_LEVELS: dict[str, LoggingLevel] = {}
    LOGGING_FORMAT: LoggingFormat = "json"
    LOGGING_INCLUDE_PROC_INFO: bool = False

    # Database connection settings, defaults to Supabase local development config
    DB_ENGINE: str = "postgresql+psycopg"
    DB_HOST: str = "localhost"
    DB_PORT: int = 54322
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "postgres"

    API_ENABLE_DOC_ENDPOINTS: bool = False


@dataclass
class ConfigState:
    config: AppConfig | None


_config_state = ConfigState(config=None)


def set_config(config: AppConfig) -> AppConfig:
    """Set the global config object and update any dependent state."""
    _config_state.config = config

    # Configure logging based on the new config
    configure_logging(
        root_level=config.LOGGING_LEVEL,
        sql_level=config.LOGGING_SQL_LEVEL,
        logger_levels=config.LOGGING_LOGGER_LEVELS,
        output_format=config.LOGGING_FORMAT,
        include_proc_info=config.LOGGING_INCLUDE_PROC_INFO,
    )
    # Ensure the storage directory exists
    config.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return config


def get_config() -> AppConfig:
    if _config_state.config is None:
        return set_config(AppConfig())
    else:
        return _config_state.config


ConfigDependency = Annotated[AppConfig, Depends(get_config)]
