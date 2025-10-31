"""Project-wide logging configuration using structlog."""

import logging
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised implicitly when structlog missing
    import structlog
    from structlog.dev import ConsoleRenderer
except ImportError:  # pragma: no cover - triggered in doc builds without structlog
    structlog = None
    ConsoleRenderer = None

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))

debug_handler = logging.FileHandler(LOG_DIR / "debug.log")
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

error_handler = logging.FileHandler(LOG_DIR / "error.log")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, debug_handler, error_handler],
)


class _KeywordFriendlyLogger:
    """Fallback logger that accepts keyword arguments like structlog."""

    def __init__(self, base_logger: logging.Logger):
        self._logger = base_logger

    def _log(self, level: int, msg: Any, *args: Any, **kwargs: Any) -> None:
        if kwargs:
            formatted = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            msg = f"{msg} | {formatted}" if msg else formatted
        self._logger.log(level, msg, *args)

    def bind(self, **kwargs: Any) -> "_KeywordFriendlyLogger":
        if kwargs:
            self._logger = logging.LoggerAdapter(self._logger, kwargs)
        return self

    def info(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, *args, **kwargs)

    def exception(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, *args, exc_info=True, **kwargs)

    def debug(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def __getattr__(self, item: str) -> Any:
        return getattr(self._logger, item)


if structlog is not None and ConsoleRenderer is not None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    struct_logger: Any = structlog.get_logger()
else:
    struct_logger = _KeywordFriendlyLogger(logging.getLogger("mange-ta-main"))
