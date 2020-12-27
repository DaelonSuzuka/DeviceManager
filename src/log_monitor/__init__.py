from .log_widget import LogMonitorWidget


from .log_database_handler import DatabaseHandler
import logging


def install():
    logger = logging.getLogger()
    logger.setLevel(1)
    logger.addHandler(DatabaseHandler())