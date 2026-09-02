import os

import bascenev1

from server.enums import Status
from tournament.brackets import Brackets
from tournament.webhook import Webhook


class Manager:
    """manager class for tournament matches."""

    def __init__(self):
        self.pending_matches = {}
        self.players = {}
        self.ready_players = {}

        self.active_match = None

    def initialize(self, season_id: str):
        """initializes the manager."""
        self.season_id = season_id
        self.brackets = Brackets(season_id=season_id)
        self.webhook = Webhook(season_id=season_id)
        self.load_pending_matches()

    def load_pending_matches(self):
        """load all pending matches from the database."""
        round_path = self.brackets.get_active_round_path()
        round_data = self.brackets.read(round_path)
        if not round_data:
            return

        # if the round is groupstage;
        if round_path.name == "group-stage.json":
            for g_key, group in round_data["groups"].items():
                for r_key, round in group["rounds"].items():
                    if round["status"] == Status.IN_PROGRESS:
                        for m_key, match in round["matches"].items():
                            if match["status"] == Status.PENDING:
                                self.register_pending_match(
                                    match_key=m_key,
                                    team1=match["team1"],
                                    team2=match["team2"],
                                    group_key=g_key,
                                    round_key=r_key,
                                )
        else:
            for m_key, match in round_data["matches"].items():
                if match["status"] == Status.PENDING:
                    self.register_pending_match(
                        match_key=m_key, team1=match["team1"], team2=match["team2"]
                    )

    def register_pending_match(
        self,
        match_key: str,
        team1: str,
        team2: str,
        group_key: str | None = None,
        round_key: str | None = None,
    ):
        """registers a pending match."""
        players1 = self.extract_from_team_players(team=team1, key="account_id")
        players2 = self.extract_from_team_players(team=team2, key="account_id")

        self.pending_matches[match_key] = {
            "team1": team1,
            "team2": team2,
            "uuids": self.extract_from_team_players(team=team1, key="device_uuid")
            + self.extract_from_team_players(team=team2, key="device_uuid"),
            "players": players1 + players2,
            "group_key": group_key,
            "round_key": round_key,
        }

        self.ready_players[match_key] = set()
        for team, players in ((team1, players1), (team2, players2)):
            for player in players:
                self.players[player] = [match_key, team]

    def extract_from_team_players(self, team: str, key: str) -> list:
        """extracts the key from team dict players."""
        return [member[key] for member in self.brackets.get_team(team_id=team)["members"]]

    def handle_player_ready(self, account_id: str) -> dict:
        """handles the player ready event."""
        match_key = self.players.get(account_id, [None, None])[0]
        if not match_key:
            return {
                "status": "error",
                "message": "You are not registered for any matches.",
            }

        # if a match is already active, we cannot accept the player.
        if self.active_match:
            return {"status": "error", "message": "A match is already active."}

        self.ready_players[match_key].add(account_id)
        match = self.pending_matches[match_key]

        # if all players of a match are ready, we can start the match.
        if self.ready_players[match_key] == set(match["players"]):
            self.active_match = {
                "match_key": match_key,
                "players": match["players"],
                "teams": [match["team1"], match["team2"]],
                "group_key": match["group_key"],
                "round_key": match["round_key"],
            }
            with bascenev1.ContextRef.empty():
                bascenev1.apptimer(2.0, self.start_tournament_session)
            return {
                "status": "success",
                "message": "You have been marked as ready.",
                "start": True,
            }

        return {"status": "success", "message": "You have been marked as ready."}

    def handle_player_leave(self, account_id: str) -> None:
        """handles the player leaving."""
        match_key = self.players.get(account_id)[0]
        if not match_key:
            return

        if self.active_match:
            return

        if account_id in self.ready_players.get(match_key, set()):
            self.ready_players[match_key].remove(account_id)

    def conclude_active_match(
        self, winner: bascenev1.SessionTeam, loser: bascenev1.SessionTeam
    ) -> None:
        """concludes the active match."""
        if not self.active_match:
            return

        if self.active_match["teams"].index(winner.name) == 0:
            score1, score2 = winner.score, loser.score
        else:
            score1, score2 = loser.score, winner.score
        match_key = self.active_match["match_key"]
        group_key = self.active_match["group_key"]
        round_key = self.active_match["round_key"]

        if group_key:
            self.brackets.update_gs_match(
                group_key=group_key,
                round_key=round_key,
                match_key=match_key,
                score1=score1,
                score2=score2,
            )
        else:
            self.brackets.update_ms_match(
                match_key=match_key, score1=score1, score2=score2
            )

        self.send_results(winner, loser, f"{group_key}-{round_key}-{match_key}")
        self.end_tournament_session()

    def send_players_dashboard(self) -> None:
        """sends the players dashboard."""
        row_template = "{rank:<2} {name:<10} {score:<3} {kills:<4} {deaths:<3} {games:>5}"
        header = row_template.format(
            rank="#", name="Name", score="Score", kills="Kills", deaths="Deaths", games="Games"
        )
        separator = "-" * len(header)
        standings_header = [header, separator]
        from stats import stats
        standings = list(stats.read().values())

        for index, player in enumerate(standings, start=1):
            standings_header.append(
                row_template.format(
                    rank=index,
                    name=player["name"][:10],
                    score=player["score"],
                    kills=player["kills"],
                    deaths=player["deaths"],
                    games=player["games"],
                )
            )
        body = "\n".join(standings_header)
        payload = {
            "embeds": [
                {
                    "title": f"Players Standings - Season {self.season_id}",
                    "image": {
                        "url": "https://cdn.discordapp.com/attachments/1539651471383986287/1543948505079488532/file_00000000656c82118b8a6c325fdcc35e.png?ex=6a980b18&is=6a96b998&hm=478f1273c9a682fadd849c0ed1359d8790e526fc9f47b1b9912516e32edde383&"
                    },
                    "description": f"```text\n{body}\n```",
                    "color": 10167990,
                    "footer": {
                        "text": "Updated after every match. Thank you for playing this tournament <3",
                    },
                }
            ]
        }

        data = self.webhook.get("players-standings")
        if data:
            # there is a message already sent.
            # we will edit it.
            self.webhook.edit("players-standings", payload)
            return

        # no message has been sent for this dashboard yet.
        self.webhook.send("dashboard", "players-standings", payload)

    def send_results(self, winner: bascenev1.SessionTeam, loser: bascenev1.SessionTeam, key: str) -> None:
        webhook_payload = {
            "embeds": [
                {
                    "color": 10167990,
                    "footer": {"text": f"Thank You for playing this match <3 [Season {self.season_id}]"},
                    "image": {
                        "url": "https://cdn.discordapp.com/attachments/1539651471383986287/1543948505490399232/file_0000000083708211964990ed39276938.png?ex=6a980b18&is=6a96b998&hm=ab034dd8a40dfb01dac8022655d25f29ccf4a4cdc8acdd735cec19261471b44d&"
                    },
                    "fields": [
                        {"name": "", "value": "", "inline": True},
                        {"name": f"{self.active_match['teams'][0]} vs {self.active_match['teams'][1]}", "value": "", "inline": True},
                        {"name": "", "value": "", "inline": True},
                        {"name": "WINNER:", "value": winner.name, "inline": True},
                        {"name": "", "value": "", "inline": True},
                        {"name": "LOSER:", "value": loser.name, "inline": True},
                        {"name": "", "value": "", "inline": True},
                        {
                            "name": "SERIES SCORE:",
                            "value": f"{winner.series} vs {loser.series}",
                            "inline": True,
                        },
                        {"name": "", "value": "", "inline": True},
                        {"name": "SCORE:", "value": str(winner.score), "inline": True},
                        {"name": "", "value": "", "inline": True},
                        {"name": "SCORE:", "value": str(loser.score), "inline": True},
                    ],
                }
            ]
        }
        self.webhook.send("results", key, webhook_payload)
        

    def start_tournament_session(self) -> None:
        """starts the tournament session."""
        # set os env to stop server from restarting in between a match.
        os.environ["BA_TOURNAMENT_MATCH"] = self.season_id
        from .activity import TournamentTransitionActivity

        session = bascenev1.get_foreground_host_session()
        with session.context:
            session.setactivity(bascenev1.newactivity(TournamentTransitionActivity))

    def end_tournament_session(self) -> None:
        """ends the tournament session."""
        self.send_players_dashboard()
        with bascenev1.ContextRef.empty():
            bascenev1.apptimer(10.0, bascenev1.app.classic.server._execute_shutdown)


manager = Manager()
