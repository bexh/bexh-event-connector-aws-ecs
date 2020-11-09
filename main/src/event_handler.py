import os
from json import dumps
from queue import Queue

import boto3

from main.src.domain_model import Event
from main.src.event_status_manager import EventStatusManager
from main.src.logger import Logger
from main.src.operator import Operator
from main.src.utils import get_current_utc_iso, dt_to_iso


class EventHandler(Operator):
    def __init__(self, logger: Logger, source_queue: Queue = None):
        self.esm = EventStatusManager()
        self.kinesis_client = boto3.client("kinesis", region_name="us-east-1", endpoint_url=os.environ.get("ENDPOINT_URL"))
        super(EventHandler, self).__init__(
            name=__name__,
            logger=logger,
            source_queue=source_queue
        )

    def process(self):
        while True:
            event = self.get_source()
            if event is not None:
                self.logger.debug("Get event")
                status = "ACTIVE" if event.winning_team_abbrev is None else "INACTIVE"
                cached_status = self.esm.get(event.event_id)

                # NEW EVENT to exchange
                if not cached_status and status == "ACTIVE":
                    self.handle_new_event(event=event, status=status)
                # EVENT to be removed from exchange and send winner to outgoing kinesis
                elif cached_status == "ACTIVE" and status == "INACTIVE":
                    self.handle_inactive_event(event=event, status=status)

    def handle_new_event(self, event: Event, status: str):
        # update cache
        self.esm.set(event_id=event.event_id, status=status)

        # tell outgoing stream that new event is available
        payload = {
            "action": "ACTIVE_EVENT",
            "timestamp": get_current_utc_iso(),
            "value": {
                "event_id": event.event_id,
                "home_team_abbrev": event.home_team_abbrev,
                "away_team_abbrev": event.away_team_abbrev,
                "home_team_score": event.home_team_score,
                "away_team_score": event.away_team_score,
                "winning_team_abbrev": event.winning_team_abbrev,
                "losing_team_abbrev": event.losing_team_abbrev,
                "date": dt_to_iso(event.date)
            }
        }
        self.logger.debug(payload)
        try:
            self.kinesis_client.put_record(
                StreamName=os.environ.get("OUTGOING_KINESIS_STREAM_NAME"),
                Data=dumps(payload),
                PartitionKey=event.event_id
            )
        except Exception as e:
            self.esm.delete(event_id=event.event_id)
            raise e

    def handle_inactive_event(self, event: Event, status: str):
        # update cache
        self.esm.set(event_id=event.event_id, status=status)

        # poison pill the event for the incoming stream so that it cancels bets for that event
        payload = {
            "action": "INACTIVE_EVENT",
            "timestamp": get_current_utc_iso(),
            "value": {
                "event_id": event.event_id,
                "home_team_abbrev": event.home_team_abbrev,
                "away_team_abbrev": event.away_team_abbrev,
                "home_team_score": event.home_team_score,
                "away_team_score": event.away_team_score,
                "winning_team_abbrev": event.winning_team_abbrev,
                "losing_team_abbrev": event.losing_team_abbrev,
                "date": dt_to_iso(event.date)
            }
        }
        self.logger.debug(payload)
        try:
            self.kinesis_client.put_record(
                StreamName=os.environ.get("INCOMING_KINESIS_STREAM_NAME"),
                Data=dumps(payload),
                PartitionKey=event.event_id
            )
            self.kinesis_client.put_record(
                StreamName=os.environ.get("OUTGOING_KINESIS_STREAM_NAME"),
                Data=dumps(payload),
                PartitionKey=event.event_id
            )
        except Exception as e:
            # set back to active to revert update to cache
            self.esm.set(event_id=event.event_id, status="ACTIVE")
            raise e
