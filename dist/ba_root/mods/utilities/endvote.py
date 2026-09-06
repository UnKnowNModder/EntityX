"""utility for endvote"""

from server.clients import fetch_client
from server import utils
from time import monotonic


class EndVote:
    """EndVote class"""

    votes: int = 0
    players: set = set()
    min_votes: int = 0
    relaxation: float = 0

    @staticmethod
    def vote(player_id: str) -> bool:
        """votes for the end"""
        if player_id in EndVote.players:
            return False

        EndVote.votes += 1
        EndVote.players.add(player_id)
        return True

    @staticmethod
    def is_started() -> bool:
        """Starts the vote."""
        return any([EndVote.votes, EndVote.players, EndVote.min_votes])

    @staticmethod
    def end() -> None:
        """Ends the vote."""
        if EndVote.is_started():
            EndVote.votes = 0
            EndVote.players = set()
            EndVote.min_votes = 0
            EndVote.relaxation = monotonic() + 60

    @staticmethod
    def end_game() -> None:
        """Ends the vote and ends the game."""
        EndVote.end()
        from bascenev1 import get_foreground_host_activity

        try:
            activity = get_foreground_host_activity()
            with activity.context:
                activity.end_game()
        except:
            pass

    @staticmethod
    def set_min_votes(players_count: int) -> None:
        """Sets the minimum number of votes required to pass a vote."""
        EndVote.min_votes = (players_count + 1) // 2

    @staticmethod
    def handle_vote(message: str, client_id: int) -> None:
        """handles if there is a endvote to start or vote for in the messages."""
        client = fetch_client(client_id)
        if message.lower() == "?end":
            if EndVote.is_started():
                client.send(
                    "End vote is already started, vote with `end` if you haven't already."
                )
                return
            if monotonic() < EndVote.relaxation:
                client.send("End vote cannot be started yet, try again in a bit.")
            from bascenev1 import get_game_roster, get_foreground_host_activity, timer

            EndVote.set_min_votes(len(get_game_roster()) - 1)
            EndVote.vote(client.account_id)
            with get_foreground_host_activity().context:
                timer(60, EndVote.end)
            utils.send(
                f"End vote started by {client.name}! Vote with `end` to end the game. votes remaining: {EndVote.min_votes - EndVote.votes}"
            )
        elif message.lower() == "end":
            if EndVote.is_started():
                if EndVote.vote(client.account_id):
                    if EndVote.votes >= EndVote.min_votes:
                        EndVote.end_game()
                        utils.send("End vote passed, ending the game!")
                        return
                    utils.send(
                        f"{client.name} voted for end, votes remaining: {EndVote.min_votes - EndVote.votes}"
                    )
