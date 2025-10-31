# service/layers/logger.py
import logging

try:  # pragma: no cover - exercised implicitly during doc builds
    import structlog
    from structlog.dev import ConsoleRenderer
except ImportError:  # pragma: no cover - triggered when structlog absent
    structlog = None
    ConsoleRenderer = None

logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
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
    struct_logger = logging.getLogger("mange-ta-main.frontend")
