from threading import Thread
from queue import Queue
from main.src.logger import Logger
from main.src.operator import Operator


class EventHandler(Operator):
    def __init__(self, logger: Logger, source_queue: Queue = None):
        super(EventHandler, self).__init__(
            name=__name__,
            logger=logger,
            source_queue=source_queue
        )

    def process(self):
        try:
            processed_counter = 0
            while True:
                event = self.get_source()
                if event is not None:
                    print(f"Get {processed_counter}: {event.event_id}")
                    processed_counter += 1
                    if processed_counter == 16:
                        break
        finally:
            print("Processor done")
            self.source_queue.task_done()
