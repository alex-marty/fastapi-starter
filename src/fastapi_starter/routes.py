from fastapi import APIRouter
from pydantic import BaseModel

from fastapi_starter.config import ConfigDependency


API_PREFIX = "/v1"

main_router = APIRouter(prefix=API_PREFIX, tags=["API"])


class HelloResponse(BaseModel):
    message: str
    debug_enabled: bool


@main_router.get("/hello")
def say_hello(name: str | None = None, *, config: ConfigDependency) -> HelloResponse:
    if name is None:
        name = "World"
    return HelloResponse(message=f"Hello, {name}!", debug_enabled=config.ENABLE_DEBUG)
