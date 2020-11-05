from threading import Thread

from sportsreference.nfl.schedule import Schedule
from sportsreference.nfl.teams import Teams

from main.src.domain_model import Team, Event


class Connector(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        try:
            teams = []
            api_teams = Teams()
            for team in api_teams:
                teams.append(
                    Team(
                        name=team.name,
                        abbrev=team.abbreviation
                    )
                )

            for team in [teams[0]]:
                team_abbrev = team.abbrev
                schedule = Schedule(team_abbrev)
                event_counter = 0
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

                    print(f"Put {event_counter}: {event.boxscore_index}")
                    event_counter += 1

                    self.queue.put(
                        Event(
                            event_id=event.boxscore_index,
                            home_team_abbrev=home_team_abbrev,
                            away_team_abbrev=away_team_abbrev,
                            home_team_score=home_team_score,
                            away_team_score=away_team_score,
                            winning_team_abbrev=winning_team_abbrev,
                            losing_team_abbrev=losing_team_abbrev,
                            date=event.datetime
                        )
                    )
        finally:
            print("Connector done")
            self.queue.task_done()
