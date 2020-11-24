from queue import Queue
from time import time, sleep

from sportsreference.nfl.schedule import Schedule
from sportsreference.nfl.teams import Teams

from src.domain_model import Team, Event
from src.logger import Logger
from src.operator import Operator


class FootballConnector(Operator):
    def __init__(self, logger: Logger, sink_queue: Queue = None):
        self.teams = []
        self.sport = "football"
        sleep(0.01)
        api_teams = Teams()
        for team in api_teams:
            self.teams.append(
                Team(
                    name=team.name,
                    abbrev=team.abbreviation
                )
            )

        super(FootballConnector, self).__init__(
            name=__name__,
            logger=logger,
            sink_queue=sink_queue,
        )

    def process(self):
        while True:
            min_duration = 60 * 5
            start = time()
            self.get_events()
            end = time()
            duration = end - start
            if duration < min_duration:
                sleep_time = min_duration - duration
                self.logger.info(f"Waiting {sleep_time} seconds")
                sleep(sleep_time)

    def get_events(self):
        self.logger.info("Getting events")

        for team in self.teams:
            team_abbrev = team.abbrev
            sleep(0.01)
            schedule = Schedule(team_abbrev)
            for event in schedule:
                home_team_abbrev = team_abbrev if event.location == "Home" else event.opponent_abbr
                away_team_abbrev = event.opponent_abbr if event.location == "Home" else team_abbrev

                home_team_score = event.points_scored if home_team_abbrev == team_abbrev else event.points_allowed
                away_team_score = event.points_allowed if home_team_abbrev == team_abbrev else event.points_scored

                if home_team_score is None or away_team_score is None:
                    home_team_score = None
                    away_team_score = None
                    winning_team_abbrev = None
                    losing_team_abbrev = None
                else:
                    winning_team_abbrev = home_team_abbrev if home_team_abbrev == event.boxscore.winning_abbr else away_team_abbrev
                    losing_team_abbrev = away_team_abbrev if home_team_abbrev == event.boxscore.winning_abbr else home_team_abbrev

                self.logger.debug("Put event")
                self.put_sink(
                    Event(
                        event_id=event.boxscore_index,
                        sport=self.sport,
                        home_team_abbrev=home_team_abbrev,
                        away_team_abbrev=away_team_abbrev,
                        home_team_score=home_team_score,
                        away_team_score=away_team_score,
                        winning_team_abbrev=winning_team_abbrev,
                        losing_team_abbrev=losing_team_abbrev,
                        date=event.datetime
                    )
                )
