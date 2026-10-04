import logging
import sys
from typing import Any, Sequence

def setup_logger(name: str = "SPSSParser", level: int = logging.DEBUG) -> logging.Logger:
    """Configures and returns a custom logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers if logger is imported multiple times
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Custom format showing level, module, function name, and message
        formatter = logging.logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ) if hasattr(logging, "logging") else logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Default logger instance for export
logger = setup_logger()

def log_list(title: str, items: Sequence[Any], level: int = logging.INFO) -> None:
    """Formats and logs a header along with each item in a list/sequence."""
    logger.log(level, f"{title} ({len(items)} items):")
    for idx, item in enumerate(items):
        logger.log(level, f"  [{idx}] {item}")