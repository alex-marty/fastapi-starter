import logging  # noqa: A005 (stdlib-module-shadowing)
import sys
from typing import Literal

import structlog


LoggingLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | int
LoggingFormat = Literal["json", "console"]


def configure_logging(
    root_level: LoggingLevel = logging.WARNING,
    sql_level: LoggingLevel = logging.WARNING,
    logger_levels: dict[str, LoggingLevel] | None = None,
    output_format: Literal["json", "console"] = "json",
    *,
    include_proc_info: bool = False,
) -> None:
    if logger_levels is None:
        logger_levels = {}

    callsite_params = {
        structlog.processors.CallsiteParameter.PATHNAME,
        structlog.processors.CallsiteParameter.FUNC_NAME,
        structlog.processors.CallsiteParameter.LINENO,
    }
    if include_proc_info:
        callsite_params |= {
            structlog.processors.CallsiteParameter.THREAD,
            structlog.processors.CallsiteParameter.THREAD_NAME,
            structlog.processors.CallsiteParameter.PROCESS,
            structlog.processors.CallsiteParameter.PROCESS_NAME,
        }

    match output_format:
        case "json":
            renderer = structlog.processors.JSONRenderer()
            exc_formatter = _format_exc_as_event
        case "console":
            renderer = structlog.dev.ConsoleRenderer(colors=True, event_key="message")
            exc_formatter = structlog.processors.format_exc_info
        case _:
            msg = f"unknown logging format: '{output_format}'"
            raise ValueError(msg)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        exc_formatter,
        structlog.processors.CallsiteParameterAdder(callsite_params),
        structlog.stdlib.ExtraAdder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        # wrapper_class=structlog.stdlib.AsyncBoundLogger,
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib root logging
    stdout_handler = _get_stdlib_handler(
        shared_processors,
        renderer,
        stream=sys.stdout,
        include_proc_info=include_proc_info,
    )
    stderr_handler = _get_stdlib_handler(
        shared_processors,
        renderer,
        stream=sys.stderr,
        include_proc_info=include_proc_info,
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(stdout_handler)
    root_logger.setLevel(root_level)

    # Configure uvicorn logging
    # https://www.uvicorn.org/settings/#logging
    logging.getLogger("uvicorn").handlers = [stderr_handler]
    # logging.getLogger("uvicorn.error").handlers = [] # Propagates to parent
    logging.getLogger("uvicorn.access").handlers = [stdout_handler]

    # Configure SQL queries logging, corresponds to the `sqlalchemy.engine` logger
    # https://docs.sqlalchemy.org/en/20/core/engines.html#configuring-logging
    logging.getLogger("sqlalchemy.engine").setLevel(sql_level)

    # Apply specific logger levels configured by the user
    for logger_name, logger_level in logger_levels.items():
        logging.getLogger(logger_name).setLevel(logger_level)


def _format_exc_as_event(logger, name, event_dict: dict) -> dict:
    """Format exceptions by printing the traceback directly in the 'event' field, for
    easier reading in Railway
    """
    if "exc_info" in event_dict:
        structlog.processors.format_exc_info(logger, name, event_dict)
        exc_text = event_dict.pop("exception")
        event_dict["event"] += f"\n{exc_text}"
    return event_dict


def _get_stdlib_handler(
    shared_processors, renderer, stream=None, *, include_proc_info: bool = False
) -> logging.Handler:
    handler = logging.StreamHandler(stream)
    processors = [_extract_proc_info_from_record] if include_proc_info else []
    processors = [
        *processors,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.processors.EventRenamer("message"),
        renderer,
    ]
    # Use `ProcessorFormatter` to format all `logging` entries.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors, processors=processors
    )
    handler.setFormatter(formatter)
    return handler


def _extract_proc_info_from_record(_, __, event_dict: dict) -> dict:
    """Extract thread and process names and add them to the event dict"""
    record = event_dict["_record"]
    event_dict["thread_name"] = record.threadName
    event_dict["process_name"] = record.processName
    return event_dict


get_logger = structlog.stdlib.get_logger
