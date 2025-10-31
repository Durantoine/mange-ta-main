# service/layers/logger.py
import logging
from typing import Any

try:  # pragma: no cover - exercised implicitly during doc builds
    import structlog
    from structlog.dev import ConsoleRenderer
except ImportError:  # pragma: no cover - triggered when structlog absent
    structlog = None
    ConsoleRenderer = None


class _KeywordFriendlyLogger:
    """Fallback logger compatible with structlog-style keyword arguments."""

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


logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
)

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
    struct_logger = _KeywordFriendlyLogger(logging.getLogger("mange-ta-main.frontend"))
