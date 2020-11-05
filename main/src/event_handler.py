from threading import Thread


class EventHandler(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        try:
            processed_counter = 0
            while True:
                event = self.queue.get()
                if event is not None:
                    print(f"Get {processed_counter}: {event.event_id}")
                    processed_counter += 1
                    if processed_counter == 16:
                        break
        finally:
            print("Processor done")
            self.queue.task_done()
