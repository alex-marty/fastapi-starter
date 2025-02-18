from typing import Annotated

from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file_encoding="utf-8",
        env_file=".env",
    )

    API_ENABLE_DOC_ENDPOINTS: bool = False
    ENABLE_DEBUG: bool = False


def get_config() -> AppConfig:
    return AppConfig()


ConfigDependency = Annotated[AppConfig, Depends(get_config)]
