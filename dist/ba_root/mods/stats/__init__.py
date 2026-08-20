"""rank system.
thanks to smoothy and ankit for their honourable work."""

import threading

import bascenev1

from server.utils import Text

from ._stats import stats


def update_stats(stats: bascenev1.Stats) -> None:
    """does what the name says, duh."""
    rec_scores = {}
    rec_kills = {}
    rec_deaths = {}
    rec_names = {}
    for record in stats.get_records().values():
        player = record.player
        if not player:
            continue
        account_id = player.get_account_id()
        if account_id:
            rec_scores.setdefault(account_id, 0)
            rec_scores[account_id] += record.accumscore
            rec_kills.setdefault(account_id, 0)
            rec_kills[account_id] += record.accum_kill_count
            rec_deaths.setdefault(account_id, 0)
            rec_deaths[account_id] += record.accum_killed_count
            rec_names.setdefault(account_id, player.getname(True, True))
    if rec_scores:
        RefreshStats(
            rec_scores, rec_kills, rec_deaths, rec_names
        ).start()  # to decrease load, we run a thread to be safe.


class RefreshStats(threading.Thread):
    """refreshes and sorts the stats for rank."""

    def __init__(self, scores, kills, deaths, names) -> None:
        super().__init__()
        self.scores = scores
        self.kills = kills
        self.deaths = deaths
        self.names = names

    def run(self) -> None:
        data = stats.read()
        for account_id, score in self.scores.items():
            if account_id not in stats:
                # this user is new, we need to register him.
                data[account_id] = {
                    "name": self.names.get(account_id, "??"),
                    "score": 0,
                    "kills": 0,
                    "deaths": 0,
                    "games": 0,
                }
            data[account_id]["score"] += score
            data[account_id]["kills"] += self.kills[account_id]
            data[account_id]["deaths"] += self.deaths[account_id]
            data[account_id]["games"] += 1
        stats.commit(data)
        # sort the stats
        stats.sort()


def attach_rank(self, player: bascenev1.Player) -> None:
    """attaches the rank on player head."""
    if player and player.sessionplayer:
        account_id = player.sessionplayer.get_account_id()
        user_stats = stats.get(account_id)
        if user_stats:
            rank = f"#{user_stats['rank']}"
            Text(self.node, rank)


__all__ = ["attach_rank", "stats"]
