"""Project-wide logging configuration using structlog."""

import logging
from pathlib import Path

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

if structlog:
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

    struct_logger = structlog.get_logger()
else:
    struct_logger = logging.getLogger("mange-ta-main")
