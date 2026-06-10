import logging
import logging.handlers
import uuid
from datetime import datetime, timezone
from flask import g, has_request_context
from config import config


class RequestIDFilter(logging.Filter):
    """Inject request_id into every log record during a request."""
    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, 'request_id', '-')
        else:
            record.request_id = '-'
        return True


def setup_logging(app):
    """Configure structured logging for the application.

    Writes JSON lines to rotating log files and human-readable output to console.
    """
    config.log_dir.mkdir(parents=True, exist_ok=True)

    # Reset root logger
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # JSON file handler with rotation
    json_handler = logging.handlers.RotatingFileHandler(
        str(config.log_dir / "app.jsonl"),
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    json_handler.setLevel(logging.INFO)
    json_handler.addFilter(RequestIDFilter())
    json_formatter = logging.Formatter(
        '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(name)s","request_id":"%(request_id)s","message":"%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    json_handler.setFormatter(json_formatter)
    root.addHandler(json_handler)

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    console_handler.addFilter(RequestIDFilter())
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s [%(request_id)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root.addHandler(console_handler)

    # Quiet noisy libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('ultralytics').setLevel(logging.WARNING)
    logging.getLogger('mysql.connector').setLevel(logging.WARNING)

    logging.getLogger(__name__).info("Logging initialized")
