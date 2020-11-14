import os
from main.src.domain_model import StatusDetails
from json import loads

import redis


class EventStatusManager(object):
    def __init__(self):
        host = os.environ.get("REDIS_HOST")
        port = os.environ.get("REDIS_PORT")
        self._r = redis.StrictRedis(host=host, port=port, db=0)

    def set(self, event_id: str, status_details: StatusDetails):
        self._r.set(name=f"event:{event_id}", value=str(status_details))

    def get(self, event_id: str) -> str:
        res = self._r.get(name=f"event:{event_id}")
        status_details = StatusDetails(**loads(res.decode("utf-8"))) if res else StatusDetails()
        return status_details

    def delete(self, event_id: str):
        self._r.delete(f"event:{event_id}")
