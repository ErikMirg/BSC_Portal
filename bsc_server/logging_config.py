import logging
import logging.config
from pathlib import Path

# Создаём директорию для логов, если она ещё не существует
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "filename": str(LOG_DIR / "app.log"),
            "when": "W6",  # еженедельная ротация
            "interval": 1,
            "backupCount": 8,
            "encoding": "utf-8",
            "level": "INFO"
        }
    },

    "loggers": {
        "auth": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "crud": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "exception": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False
        },
        "security": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "profiles": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "app_logger": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True
        }
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    }
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
