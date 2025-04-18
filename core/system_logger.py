import logging
import os
import traceback
import sys
import logging.config

from concurrent_log_handler import ConcurrentRotatingFileHandler

from .settings import settings


def get_log_directory():
    """Return the appropriate log directory based on environment"""
    if settings.ENVIRONMENT == "remote":
        return '/var/log/'
    else:
        path = os.path.join(settings.TEMP_DIR, 'logs')
        os.makedirs(path, exist_ok=True)
        return path


log_file_dir = get_log_directory()
if log_file_dir is None:
    raise ValueError("LOCAL_LOG_DIR must be set in settings.py")

os.makedirs(log_file_dir, exist_ok=True)
LOG_FILENAME = f"matrx-{settings.APP_NAME}-{settings.APP_VERSION}.log"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(levelname)s %(asctime)s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": settings.LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "DEBUG",
            "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
            "filename": os.path.join(log_file_dir, LOG_FILENAME),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "standard",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}



class SystemLogger:
    def __init__(self):
        self.logger = logging.getLogger('app')
        os.makedirs(log_file_dir, exist_ok=True)
        self.console_handler = None
        self.configure_logging()
        level_name = logging.getLevelName(self.logger.getEffectiveLevel())

    def configure_logging(self):
        try:
            logging_config = LOGGING
            if logging_config:
                logging.config.dictConfig(logging_config)
                return
        except (ImportError, AttributeError):
            pass

        # Default configuration if settings.LOGGING is not available
        self.logger.setLevel(logging.DEBUG)

        # Console Handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(console_formatter)
        self.logger.addHandler(self.console_handler)

        # File Handler (Concurrent rotation)
        file_handler = ConcurrentRotatingFileHandler(
            f"{log_file_dir}/appdev.log",
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def disable_console_logging(self):
        if self.console_handler and self.console_handler in self.logger.handlers:
            self.logger.removeHandler(self.console_handler)

    def enable_console_logging(self):
        if self.console_handler and self.console_handler not in self.logger.handlers:
            self.logger.addHandler(self.console_handler)

    def _log(self, level, message, *args, **kwargs):
        extra = kwargs.pop('extra', {})
        exc_info = kwargs.pop('exc_info', None)
        if exc_info:
            extra['traceback'] = traceback.format_exc()
        try:
            self.logger.log(level, message, *args, extra=extra, exc_info=exc_info, **kwargs)
        except Exception as e:
            print(f"Logging error: {str(e)}")

    def debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)


# Create a global instance of the logger
system_logger = SystemLogger()


# Function to get the logger instance
def get_logger():
    return system_logger
