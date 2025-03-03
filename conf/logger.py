import logging
from logging.handlers import RotatingFileHandler


def configure_logging(level=logging.INFO):
    log_formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(log_formatter)

    file_handler = RotatingFileHandler(
        "debug.log", maxBytes=10 * 1024 * 1024, backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)

    logging.basicConfig(level=level, handlers=[console_handler, file_handler])


logger = logging.getLogger(__name__)
