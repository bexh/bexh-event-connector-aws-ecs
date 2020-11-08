import os
from typing import Literal

import redis


class EventStatusManager(object):
    Status = Literal["ACTIVE", "INACTIVE"]

    def __init__(self):
        host = os.environ.get("REDIS_HOST")
        port = os.environ.get("REDIS_PORT")
        self._r = redis.StrictRedis(host=host, port=port, db=0)

    def set(self, event_id: str, status: Status):
        self._r.set(name=f"event:{event_id}", value=status)

    def get(self, event_id: str) -> str:
        res = self._r.get(name=f"event:{event_id}")
        return res.decode("utf-8") if res else None

    def delete(self, event_id: str):
        self._r.delete(f"event:{event_id}")
