# import logging

# def setup_logger(name: str = "airguardian") -> logging.Logger:
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)

#     # Only add handlers once
#     if not logger.handlers:
#         formatter = logging.Formatter(
#             "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
#         )

#         # Terminal logs
#         stream_handler = logging.StreamHandler()
#         stream_handler.setFormatter(formatter)
#         logger.addHandler(stream_handler)

#         # File logs
#         file_handler = logging.FileHandler("app.log")
#         file_handler.setFormatter(formatter)
#         logger.addHandler(file_handler)

#     return logger

# logger = setup_logger()


import logging
import os


def setup_logger(name: str = "airguardian") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # ------------------------------------------------------------------
    # Stream (console) handler — Docker-friendly, always enabled
    # ------------------------------------------------------------------
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # ------------------------------------------------------------------
    # Optional file logging — only if LOG_TO_FILE=1
    # ------------------------------------------------------------------
    if os.getenv("LOG_TO_FILE") == "1":
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
