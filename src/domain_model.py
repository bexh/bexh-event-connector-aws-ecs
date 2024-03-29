from datetime import datetime
from json import dumps
from typing import Literal


class Team:
    def __init__(self, name: str, abbrev: str):
        self.name = name
        self.abbrev = abbrev


class Event:
    Sport = Literal["basketball", "football", "hockey", "baseball"]

    def __init__(
            self,
            event_id: str,
            sport: Sport,
            home_team_abbrev: str,
            away_team_abbrev: str,
            home_team_name: str,
            away_team_name: str,
            home_team_score: int,
            away_team_score: int,
            winning_team_abbrev: str,
            losing_team_abbrev: str,
            date: datetime
    ):
        self.event_id = event_id
        self.sport = sport
        self.home_team_abbrev = home_team_abbrev
        self.away_team_abbrev = away_team_abbrev
        self.home_team_name = home_team_name
        self.away_team_name = away_team_name
        self.home_team_score = home_team_score
        self.away_team_score = away_team_score
        self.winning_team_abbrev = winning_team_abbrev
        self.losing_team_abbrev = losing_team_abbrev
        self.date = date


class StatusDetails:
    Status = Literal["ACTIVE", "INACTIVE"]

    def __init__(self, status: Status = None, home_team_abbrev: str = None, away_team_abbrev: str = None):
        self.status = status
        self.home_team_abbrev = home_team_abbrev
        self.away_team_abbrev = away_team_abbrev

    def __str__(self):
        dict_form = {
            "status": self.status,
            "home_team_abbrev": self.home_team_abbrev,
            "away_team_abbrev": self.away_team_abbrev
        }
        return dumps(dict_form)
