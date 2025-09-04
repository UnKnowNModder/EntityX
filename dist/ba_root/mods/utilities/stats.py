""" rank utility.
thanks to smoothy and ankit for their honourable work."""
from __future__ import annotations
from bascenev1._activitytypes import ScoreScreenActivity
from .utils import replace_method
from bascenev1._map import Map
from commands import on_command
import bacore, bascenev1, threading, requests

def update_stats(stats: bascenev1.Stats) -> None:
	""" does what the name says, duh. """
	rec_scores = {}
	rec_kills = {}
	rec_deaths = {}
	for record in stats.get_records().values():
		player = record.player
		if not player: continue
		account_id = player.get_v1_account_id()
		if account_id:
			rec_scores.setdefault(account_id, 0)
			rec_scores[account_id] += record.accumscore
			rec_kills.setdefault(account_id, 0)
			rec_kills[account_id] += record.accum_kill_count
			rec_deaths.setdefault(account_id, 0)
			rec_deaths[account_id] += record.accum_killed_count
	if rec_scores:
		RefreshStats(rec_scores, rec_kills, rec_deaths).start() # to decrease load, we run a thread to be safe.

@replace_method(ScoreScreenActivity, "on_begin", initial = True)
def new_on_begin(self) -> None:
	""" modified. """
	config = bacore.config.read()
	if config["stats"]["enable"]:
		update_stats(self._stats)

@replace_method(Map, "__init__", initial = True)
def new_map_init(*args, **kwargs):
	config = bacore.config.read()
	if config["stats"]["enable"] and config["stats"]["leaderboard"]:
		bacore.stats.leaderboard()

class RefreshStats(threading.Thread):
	""" refreshes and sorts the stats for rank. """
	def __init__(self, scores, kills, deaths) -> None:
		super().__init__()
		self.scores = scores
		self.kills = kills
		self.deaths = deaths
	
	def run(self) -> None:
		stats = bacore.stats.read()
		for account_id, score in self.scores.items():
			if account_id not in stats:
				# this user is new, we need to register him.
				stats[account_id] = {
					"name": self.get_account_name(account_id),
					"score": 0,
					"kills": 0,
					"deaths": 0,
					"games": 0
				}
			stats[account_id]["score"] += score
			stats[account_id]["kills"] += self.kills[account_id]
			stats[account_id]["deaths"] += self.deaths[account_id]
			stats[account_id]["games"] += 1
		bacore.stats.commit(stats)
		# sort the stats
		bacore.stats.sort()
	
	def get_account_name(self, account_id: str) -> None:
		try:
			url = f"http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID={account_id}"
			response = requests.get(url).json()
			return response["profileDisplayString"]
		except:
			return "??"
	
@on_command(name="/stats")
def show_stats(client: Client) -> None:
	"""shows the client his stats."""
	if stats := bacore.stats.get(client.account_id):
		message = "{} | score: {} | kills: {} | deaths: {} | games: {}".format(stats["rank"], stats["score"], stats["kills"], stats["deaths"], stats["games"])
		client.send(message, sender = "rank")
		return
	client.error("Your stats will be available soon.")

