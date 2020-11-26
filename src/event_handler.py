import os
from json import dumps
from queue import Queue

import boto3
from src.domain_model import Event, StatusDetails
from src.event_status_manager import EventStatusManager
from src.logger import Logger
from src.operator import Operator
from src.utils import get_current_utc_iso, dt_to_iso


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
                status_details = StatusDetails(
                    status=status,
                    home_team_abbrev=event.home_team_abbrev,
                    away_team_abbrev=event.away_team_abbrev
                )
                cached_status_details = self.esm.get(event.event_id)

                # NEW EVENT to exchange
                if not cached_status_details.status and status_details.status == "ACTIVE":
                    self.handle_new_event(event=event, status_details=status_details)
                # EVENT to be removed from exchange and send winner to outgoing kinesis
                elif cached_status_details.status == "ACTIVE" and status_details.status == "INACTIVE":
                    self.handle_inactive_event(event=event, status_details=status_details)

    def handle_new_event(self, event: Event, status_details: StatusDetails):
        # update cache
        self.esm.set(event_id=event.event_id, status_details=status_details)

        # tell outgoing stream that new event is available
        payload = {
            "action": "ACTIVE_EVENT",
            "timestamp": get_current_utc_iso(),
            "value": {
                "event_id": event.event_id,
                "sport": event.sport,
                "home_team_abbrev": event.home_team_abbrev,
                "away_team_abbrev": event.away_team_abbrev,
                "home_team_name": event.home_team_name,
                "away_team_name": event.away_team_name,
                "home_team_score": event.home_team_score,
                "away_team_score": event.away_team_score,
                "winning_team_abbrev": event.winning_team_abbrev,
                "losing_team_abbrev": event.losing_team_abbrev,
                "date": dt_to_iso(event.date)
            }
        }
        self.logger.debug(f"New event: {payload}")
        try:
            self.kinesis_client.put_record(
                StreamName=os.environ.get("OUTGOING_EVENTS_KINESIS_STREAM_NAME"),
                Data=dumps(payload),
                PartitionKey=event.event_id
            )
        except Exception as e:
            self.esm.delete(event_id=event.event_id)
            raise e

    def handle_inactive_event(self, event: Event, status_details: StatusDetails):
        # update cache
        self.esm.set(event_id=event.event_id, status_details=status_details)

        # poison pill the event for the incoming stream so that it cancels bets for that event
        payload = {
            "action": "INACTIVE_EVENT",
            "timestamp": get_current_utc_iso(),
            "value": {
                "event_id": event.event_id,
                "sport": event.sport,
                "home_team_abbrev": event.home_team_abbrev,
                "away_team_abbrev": event.away_team_abbrev,
                "home_team_name": event.home_team_name,
                "away_team_name": event.away_team_name,
                "home_team_score": event.home_team_score,
                "away_team_score": event.away_team_score,
                "winning_team_abbrev": event.winning_team_abbrev,
                "losing_team_abbrev": event.losing_team_abbrev,
                "date": dt_to_iso(event.date)
            }
        }
        self.logger.debug(f"Inactive event: {payload}")
        try:
            self.kinesis_client.put_record(
                StreamName=os.environ.get("INCOMING_BETS_KINESIS_STREAM_NAME"),
                Data=dumps(payload),
                PartitionKey=event.event_id
            )
            self.kinesis_client.put_record(
                StreamName=os.environ.get("OUTGOING_EVENTS_KINESIS_STREAM_NAME"),
                Data=dumps(payload),
                PartitionKey=event.event_id
            )
        except Exception as e:
            # set back to active to revert update to cache
            status_details.status = "ACTIVE"
            self.esm.set(event_id=event.event_id, status_details=status_details)
            raise e
