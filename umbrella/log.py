import logging
import os
import sys
from logging import Logger, handlers
from pathlib import Path
from typing import TYPE_CHECKING, Optional, cast

import coloredlogs  # type: ignore

from umbrella.constants import LogConfig, TimeConfig

if TYPE_CHECKING:
    LoggerClass = Logger
else:
    LoggerClass = logging.getLoggerClass()


class BaseLogger(LoggerClass):
    """Custom implementation of the `Logger` class with an added `trace` method."""

    def trace(self, msg: str, *args, **kwargs) -> None:
        """
        Log 'msg % args' with severity 'TRACE'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.trace("Houston, we have an %s", "interesting problem", exc_info=1)
        """
        if self.isEnabledFor(LogConfig.trace_level):
            self.log(LogConfig.trace_level, msg, *args, **kwargs)


def get_logger(name: Optional[str] = None) -> BaseLogger:
    """Utility to make mypy recognise that logger is of type `BaseLogger`."""
    return cast(BaseLogger, logging.getLogger(name))


def setup() -> None:
    """Set up loggers."""
    logging.TRACE = LogConfig.trace_level
    logging.addLevelName(LogConfig.trace_level, "TRACE")
    logging.setLoggerClass(BaseLogger)

    root_logger = get_logger()

    log_format = logging.Formatter(
        LogConfig.string_format, TimeConfig.datetime_format_full
    )

    if LogConfig.file_logs:
        log_file = Path("logs", "umbrella.log")
        log_file.parent.mkdir(exist_ok=True)
        file_handler = handlers.RotatingFileHandler(
            log_file,
            maxBytes=LogConfig.max_bytes,
            backupCount=5,
            encoding=LogConfig.encoding,
        )
        file_handler.setFormatter(log_format)
        root_logger.addHandler(file_handler)

    if "COLOREDLOGS_LEVEL_STYLES" not in os.environ:
        coloredlogs.DEFAULT_LEVEL_STYLES = {
            **coloredlogs.DEFAULT_LEVEL_STYLES,
            "trace": {"color": 246},
            "critical": {"background": "red"},
            "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
        }

    if "COLOREDLOGS_LOG_FORMAT" not in os.environ:
        coloredlogs.DEFAULT_LOG_FORMAT = LogConfig.string_format

    coloredlogs.install(
        level=LogConfig.trace_level, logger=root_logger, stream=sys.stdout
    )

    root_logger.setLevel(
        logging.DEBUG if LogConfig.debug else logging.INFO
    )  # CHANGE TO DEBGU
    get_logger("discord").setLevel(logging.WARNING)
    get_logger("websockets").setLevel(logging.WARNING)
    get_logger("chardet").setLevel(logging.WARNING)
    get_logger("async_rediscache").setLevel(logging.WARNING)

    # Set back to the default of INFO even if asyncio's debug mode is enabled.
    get_logger("asyncio").setLevel(logging.INFO)
