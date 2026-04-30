import logging
import json


def setup_logger(service_name):
    logger = logging.getLogger(service_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # handler = logging.StreamHandler()
        # formatter = logging.Formatter(
        #     '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "%(name)s", "message": "%(message)s"}'
        # )
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)

    return logger
