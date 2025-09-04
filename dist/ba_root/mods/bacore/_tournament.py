""" tournament storage core. """
from __future__ import annotations
import os, secrets, string
import babase, bascenev1
from ._storage import Storage
from ._clients import Client
from ._enums import Match, Team
from ._utils import success

class Tournament(Storage):
	"""tournament storage class."""

	def __init__(self) -> None:
		super().__init__("tournament", is_dir = True)
		self.path = self.directory / "matches.json"
		self.results = self.directory / "results.json"
		self.registration = self.directory / "registrations.json"
		self.match: Match = {}
		self.bootstrap()

	def bootstrap(self) -> None:
		"""creates tournament file."""
		from . import config
		self.config = config.read()
		if not self.path.exists():
			self.commit([])
		if not self.results.exists():
			self.commit([], self.results)
		if not self.registration.exists():
			self.commit({}, self.registration)

	def insert(self, match: Match) -> None:
		"""inserts the match to the database."""
		tournament = self.read()
		match["id"] = len(tournament) + 1
		match["confirmed"] = []
		tournament.append(match)
		self.commit(tournament)

	def discard(self, id: int, survive: bool = False) -> None:
		"""discards a match."""
		tournament = self.read()
		match = [m for m in tournament if m["id"] == id][0]
		if survive:
			for team in match["teams"]:
				self.register(team["name"], team["participants"])
		tournament.remove(match)
		self.commit(tournament)
	
	def register(self, name: str, account_ids: list[str]) -> bool:
		""" registers a team/player in teams/solo tournament. """
		registration = self.read(self.registration)
		if name in registration:
			return False
		registration[name] = account_ids
		self.commit(registration, self.registration)
		return True

	def pair_match(self, series: int, first_team: str, second_team: str) -> None:
		""" pairs a match between two given teams/players. """
		registration = self.read(self.registration)
		assert first_team in registration
		assert second_team in registration
		match: Match = {
			"series": series,
			"teams": [
				{"name": first_team, "participants": registration[first_team]},
				{"name": second_team, "participants": registration[second_team]}
			]
		}
		self.insert(match)
		del registration[first_team]
		del registration[second_team]
		self.commit(registration, self.registration)


	def get_player_team(self, player: bascenev1.SessionPlayer) -> dict:
		""" returns the tournament team this player is associated with. """
		account_id = player.get_v1_account_id()
		for team in self.match["teams"]:
			if account_id in team["participants"]:
				return team
		return {}

	def list_teams(self) -> list[str]:
		""" returns registered team's names."""
		registration = self.read(self.registration)
		return [team for team in registration]

	def list_match(self) -> list[str]:
		""" idk. """
		matches = []
		tournament = self.read()
		for match in tournament:
			series = match["series"]
			team1 = match["teams"][0]["name"]
			team2 = match["teams"][1]["name"]
			form = f"{series} -> {team1} vs {team2}"
			matches.append(form)
		return matches

	def confirm(self, client: Client) -> bool | None:
		"""confirms the client if they are in a match."""
		# check: if any match is ongoing
		if self.match:
			client.error("A match is in progress — confirmation unavailable.")
			return False
		account_id = client.account_id
		tournament = self.read()
		for match in tournament:
			all_members = match["teams"][0]["participants"] + match["teams"][1]["participants"]

			if account_id in all_members:
				if account_id in match["confirmed"]:
					# ah, double confirm, pretty smart huh?
					client.error("You have already confirmed.")
					return False
				match["confirmed"].append(account_id)
				if len(match["confirmed"]) == len(all_members):
					# all clients have been registered, assign the self.match it's value.
					self.match = match
					# load and start the tournament session.
					with babase.ContextRef.empty():
						success("Your match is about to begin.")
						babase.apptimer(2.0, self.begin)
					# clean up.
					# tournament.remove(match)
				self.commit(tournament)
				client.success("You have been successfully confirmed.")
				return True
		client.error("You are not part of any match.")

	def declare(self, winner: bascenev1.SessionTeam, message: str) -> None:
		"""declares a match winner and saves it."""
		from bacommon.servermanager import ShutdownReason
		success(message + "\nThe match result has been announced to discord.")
		# clean up
		self.discard(self.match["id"])
		result = {}
		for team in self.match["teams"]:
			if team["name"] == winner.name:
				result["winner"] = team["name"]
				result["members"] = team["participants"]
				continue
			result["loser"] = team["name"]
		# also register the winner team for next rounds.
		self.register(winner.name, result["members"])
		results = self.read(self.results)
		results.append(result)
		self.match.clear()
		# announce in the server aswell..
		self.announce_winner(result)
		self.commit(results, self.results)
		# it does not hurt to clean-up the server entirely.
		with babase.ContextRef.empty():
			babase.apptimer(10, babase.app.classic.server._execute_shutdown)
		# babase.app.classic.server.shutdown(ShutdownReason.RESTARTING, False)
		

	def announce_winner(self, result: dict) -> None:
		import requests, datetime
		""" pushes announcement to webhooks. """
		WEBHOOK_URL = self.config["tournament"]["webhook_url"]
		now = (datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)).strftime("%d %b %Y · %I:%M %p")
		data = {
			"embeds": [
				{
					"title": "<:winner:1411402836582858752> Match Result",
					"description": f"{result['winner']} has won the match against {result['loser']}",
					"color": 0x00ff00,
					"footer": {
						"text": f'{now}'
					}
				}
			]
		}
		requests.post(WEBHOOK_URL, json=data)

	def begin(self) -> None:
		"""begins the tournament session."""
		# start the match.
		from utilities import TournamentTransitionActivity
		session = bascenev1.get_foreground_host_session()
		with session.context:
			session.setactivity(bascenev1.newactivity(TournamentTransitionActivity))
		
		