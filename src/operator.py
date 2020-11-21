from abc import ABC, abstractmethod
from threading import Thread
from queue import Queue
from src.logger import Logger


class Operator(ABC, Thread):
    def __init__(self, name: str, logger: Logger, source_queue: Queue = None, sink_queue: Queue = None):
        Thread.__init__(self)
        self.logger = logger
        self.source_queue = source_queue
        self.sink_queue = sink_queue
        self.name = name
        self.logger.info(f"Starting Operator: {name}")

    def run(self):
        while True:
            try:
                self.process()
            except Exception as e:
                self.logger.error(f"Error in Operator- {self.name}: {e}")
                raise e

    def get_source(self):
        if self.source_queue:
            return self.source_queue.get()

    def put_sink(self, record):
        if self.sink_queue:
            self.sink_queue.put(record)

    @abstractmethod
    def process(self):
        pass
