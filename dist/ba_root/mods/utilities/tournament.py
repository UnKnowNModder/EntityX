# Released under the MIT License. See LICENSE for details.
#
"""Functionality related to tournament sessions."""
from __future__ import annotations

from typing import TYPE_CHECKING, override

import babase, bacore
import _bascenev1, bascenev1
from bacore import Client
from bascenev1._dualteamsession import DualTeamSession
from bascenev1._activitytypes import TransitionActivity

if TYPE_CHECKING:
	from typing import Any


class TournamentSession(DualTeamSession):
	"""special session type for tournament. """

	def __init__(self) -> None:
		super().__init__()
		self._series: int = 0
		self._requested_teams = {}
		self._disqualify_time: int = 15 # minutes
		self._disqualify_timers: dict = {}

	@override
	def on_player_request(self, player: bascenev1.SessionPlayer) -> bool:
		identifier = player.get_account_id()
		client = Client(player.inputdevice.client_id, identifier)
		if bacore.tournament.match and not client.is_participant:
			client.error("A match is in progress — joining is not allowed.")
			return False
		
		if identifier in self._disqualify_timers:
			del self._disqualify_timers[identifier]
		return super().on_player_request(player)

	@override
	def on_player_leave(self, sessionplayer: bascenev1.SessionPlayer) -> None:
		super().on_player_leave(sessionplayer)
		
		message = "Join within {} minutes to avoid disqualification.".format(self._disqualify_time)
		try: Client(sessionplayer.inputdevice.client_id).error(message)
		except: pass
		
		identifier = self._player_requested_identifiers.get(sessionplayer.id)
		sessionteam = self._requested_teams[identifier]
		
		with self.context:
			self._disqualify_timers[identifier] = bascenev1.Timer(self._disqualify_time*60, bascenev1.WeakCallStrict(self.disqualify_team, sessionteam, identifier))

	def disqualify_team(self, team: bascenev1.SessionTeam, identifier: str) -> None:
		""" disqualifies a team from the tournament. """
		# clean up
		del self._disqualify_timers[identifier]
		del self._requested_teams[identifier]
		teams = self.sessionteams
		winner_team = teams[team.id ^ 1]
		disqualify_message = "Team {} has been disqualified due to a player leaving — Team {} wins by default".format(team.name, winner_team.name)
		bacore.tournament.declare(winner_team, disqualify_message)

	@override
	def on_team_join(self, team: bascenev1.SessionTeam) -> None:
		super().on_team_join(team)
		# swap team name with tournament team name.
		team.name = bacore.tournament.match["teams"][team.id]["name"]
	
	@override
	def handlemessage(self, msg: Any) -> Any:
		from bascenev1._lobby import PlayerReadyMessage
		if isinstance(msg, PlayerReadyMessage):
			player = msg.chooser.getplayer()
			player_team_name = bacore.tournament.get_player_team(player)["name"]
			if not msg.chooser.sessionteam.name == player_team_name:
				Client(player.inputdevice.client_id).error("Incorrect team — please verify and join your assigned team.")
				return None
			# keep track of chooser's team incase we might need to disqualify them.
			self._requested_teams[player.get_account_id()] = msg.chooser.sessionteam
			self._on_player_ready(msg.chooser)
		
		else:
			return super().handlemessage(msg)

	@override
	def _switch_to_score_screen(self, results: bascenev1.GameResults) -> None:
		# pylint: disable=cyclic-import
		from bascenev1lib.activity.multiteamvictory import (
			TeamSeriesVictoryScoreScreenActivity,
		)
		from bascenev1lib.activity.dualteamscore import (
			TeamVictoryScoreScreenActivity,
		)
		from bascenev1lib.activity.drawscore import DrawScoreScreenActivity

		winnergroups = results.winnergroups

		# If everyone has the same score, call it a draw.
		if len(winnergroups) < 2:
			self.setactivity(_bascenev1.newactivity(DrawScoreScreenActivity))
		else:
			winner = winnergroups[0].teams[0]
			winner.customdata['score'] += 1

			# If a team has won, show final victory screen.
			if winner.customdata['score'] >= (self._series_length - 1) / 2 + 1:
				self._series += 1
				self.setactivity(
					_bascenev1.newactivity(
						TeamSeriesVictoryScoreScreenActivity,
						{'winner': winner},
					)
				)
				if self._series >= bacore.tournament.match["series"]:
					win_message = "Match concluded — winner: {}.".format(winner.name)
					bacore.tournament.declare(winner, win_message)
			else:
				self.setactivity(
					_bascenev1.newactivity(
						TeamVictoryScoreScreenActivity, {'winner': winner}
					)
				)
				
class TournamentTransitionActivity(TransitionActivity):
	"""A simple transition activity to switch from any session to tournament session. """
	
	@override
	def end(self, results: Any = None, delay: float = 0.0, force: bool = False) -> None:
		call = babase.CallStrict(_bascenev1.new_host_session, TournamentSession)
		babase.pushcall(call)
		