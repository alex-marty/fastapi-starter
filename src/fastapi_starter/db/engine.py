import time
from collections.abc import Generator
from contextlib import contextmanager
from functools import lru_cache
from typing import Annotated, Self
from urllib.parse import quote_plus

from fastapi import Depends
from pydantic.dataclasses import dataclass
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from fastapi_starter.__about__ import __version__
from fastapi_starter.config import AppConfig, ConfigDependency
from fastapi_starter.logging import get_logger


default_app_name = f"fastapi-starter {__version__}"
logger = get_logger(__name__)


@dataclass(frozen=True, eq=True)
class SQLAlchemyEngineConfig:
    engine: str
    user: str
    password: str
    host: str
    port: int
    name: str
    app_name: str | None = default_app_name

    @classmethod
    def from_app_config(cls, app_config: AppConfig) -> Self:
        return cls(
            engine=app_config.DB_ENGINE,
            user=app_config.DB_USER,
            password=app_config.DB_PASSWORD,
            host=app_config.DB_HOST,
            port=app_config.DB_PORT,
            name=app_config.DB_NAME,
        )

    def engine_url(self, *, hide_password: bool = False) -> str:
        password = "***" if hide_password else quote_plus(self.password)
        return (
            f"{self.engine}://{self.user}:{password}@{self.host}:{self.port}/{self.name}"
        )

    def connect_args(self) -> dict:
        return {"application_name": self.app_name} if self.app_name is not None else {}


def get_db_engine(config: SQLAlchemyEngineConfig) -> Engine:
    engine_url = config.engine_url()
    safe_engine_url = config.engine_url(hide_password=True)

    logger.info(f"Creating DB engine with URL '{safe_engine_url}'")
    return create_engine(
        engine_url, isolation_level="SERIALIZABLE", connect_args=config.connect_args()
    )


def wait_for_db(config: SQLAlchemyEngineConfig) -> None:
    logger.info("Connecting to DB")
    engine = get_db_engine(config)
    connection = None
    while connection is None:
        try:
            connection = engine.connect()
        except OperationalError as exc:
            logger.info("DB connection error: %s", str(exc))
            logger.warning("Failed connecting to DB, will keep retrying")
            time.sleep(1)
    connection.close()


@contextmanager
def get_db_session(engine: Engine) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations.

    This function is a generator that yields a new session object, and ensures that the
    session is committed if no exception is raised, otherwise it's rolled back and the
    exception is propagated.
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        else:
            session.commit()


# FastAPI dependencies
####


def get_sql_alchemy_config(app_config: ConfigDependency) -> SQLAlchemyEngineConfig:
    return SQLAlchemyEngineConfig.from_app_config(app_config)


SQLAlchemyEngineConfigDependency = Annotated[
    SQLAlchemyEngineConfig, Depends(get_sql_alchemy_config)
]


# lru_cache ensures we get the same engine instance throughout the lifetime of the app,
# and DB connections are reused.
@lru_cache
def _get_singleton_db_engine(sql_alchemy_config: SQLAlchemyEngineConfig) -> Engine:
    return get_db_engine(sql_alchemy_config)


def get_db_engine_dependency(
    sql_alchemy_config: SQLAlchemyEngineConfigDependency,
) -> Engine:
    return _get_singleton_db_engine(sql_alchemy_config)


DBEngineDependency = Annotated[Engine, Depends(get_db_engine_dependency)]


def get_db_session_dependency(
    engine: DBEngineDependency,
) -> Generator[Session, None, None]:
    with get_db_session(engine) as session:
        yield session


DBSessionDependency = Annotated[Session, Depends(get_db_session_dependency)]
