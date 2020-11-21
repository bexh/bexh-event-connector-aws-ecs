import os
from queue import Queue

from src.connector import FootballConnector
from src.event_handler import EventHandler
from src.logger import LoggerFactory


class Core:
    def __init__(self):
        log_level = os.environ.get("LOG_LEVEL", None)
        self.logger = LoggerFactory().get_logger(name=__name__, log_level=log_level)

    def run(self):
        event_queue = Queue()

        football_connector = FootballConnector(logger=self.logger, sink_queue=event_queue)
        event_handler = EventHandler(logger=self.logger, source_queue=event_queue)

        event_handler.start()
        football_connector.start()

        event_handler.join()
        football_connector.join()
