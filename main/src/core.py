from queue import Queue
import timeit
from main.src.connector import Connector
from main.src.event_handler import EventHandler
from main.src.logger import LoggerFactory
import os


class Core:
    def __init__(self):
        log_level = os.environ.get("LOG_LEVEL", None)
        self.logger = LoggerFactory().get_logger(name=__name__, log_level=log_level)

    def run(self):
        start = timeit.default_timer()

        event_queue = Queue()

        connector = Connector(event_queue)
        connector.start()

        event_handler = EventHandler(event_queue)
        event_handler.start()
        event_handler.join()

        self.logger.info(f"Duration: {timeit.default_timer() - start}")
