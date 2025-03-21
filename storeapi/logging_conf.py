import logging
from logging.config import dictConfig

from storeapi.config import DevConfig, config, ProdConfig


def obfuscated(email: str, obfuscated_length: int) -> str:
    character = email[:obfuscated_length]
    first, second = email.split("@")
    return character + "*" * (len(first) - obfuscated_length) + "@" + second


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2):
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True

handlers = ["default", "rotating_file"]
if isinstance(config, ProdConfig):
    handlers.append("logtail")


def configure_logging():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "format": "(%(correlation_id)s) %(asctime)s %(levelname)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "class": "logging.Formatter",
                },
                "file": {
                    "format": "%(asctime)s %(msecs)03d %(levelname)-8s %(correlation_id)s %(name)s %(lineno)d %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                },
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "formatter": "console",
                    "class": "rich.logging.RichHandler",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating_file": {
                    "level": "DEBUG",
                    "formatter": "file",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "storeapi.log",
                    "maxBytes": 1024 * 1024 * 5,
                    "backupCount": 3,
                    "encoding": "utf8",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "logtail": {
                    "level": "DEBUG",
                    "formatter": "console",
                    "class": "logtail.LogtailHandler",
                    "source_token": config.LOGTAIL_API_KEY,
                    "filters": ["correlation_id", "email_obfuscation"],
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file", "logtail"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default", "rotating_file", "logtail"],
                    "level": "INFO",
                    "propagate": False,
                },
                "storeapi": {
                    "handlers": handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "database": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
            },
        }
    )
