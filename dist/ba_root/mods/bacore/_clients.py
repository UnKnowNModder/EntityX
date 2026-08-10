"""client-related utility"""

from __future__ import annotations
import bascenev1, secrets
from . import _utils as utils
from ._enums import Authority


class Client:
	"""Client object."""

	__mute_clients = set()  # class level var
	__authenticated = set()
	__auth_codes = {}

	def __init__(
		self,
		client_id: int = 0,
		account_id: str = "",
		name: str = "",
		in_lobby: bool = True,
	) -> None:
		self.client_id = client_id
		self.account_id = account_id
		self.name = name
		self.in_lobby = in_lobby

	@property
	def authority(self) -> Authority:
		"""this client's authority level."""
		from . import roles
		if self.client_id == -1:
			# special access to server.
			return Authority.HOST
		return roles.get_authority_level(self.account_id)
	
	@property
	def authenticity(self) -> bool:
		"""this client's authenticity."""
		from . import config
		if not config.read()['auth_verification']["enable"]:
			return True
		if self.client_id == -1:
			# host is always authentic
			return True
		from . import roles
		if self.account_id in Client.__authenticated:
			# we don't wanna fetch it from database everytime.
			return True
		response = roles.is_authentic(self.account_id)
		if response:
			Client.__authenticated.add(self.account_id)
		return response

	def authenticate(self) -> bool:
		""" authenticate this client. """
		from . import roles
		response = roles.authenticate(self.account_id)
		if response:
			self.success("You have been verified successfully.")
		return response

	def get_auth_code(self) -> None:
		""" generates an auth code for this client if doesn't exists. """
		if self.account_id not in Client.__auth_codes:
			Client.__auth_codes[self.account_id] = f'{secrets.randbelow(1_000_000):06d}'
		return Client.__auth_codes[self.account_id]
	
	def verify_auth_code(self, code: str) -> bool:
		""" verifies the entered code to auth code. """
		if Client.__auth_codes[self.account_id] == code:
			return self.authenticate()

	@property
	def is_participant(self) -> bool:
		""" whether the account is any participant of the current match. """
		from . import tournament
		if tournament.match:
			return self.account_id in tournament.match["confirmed"]
		return False

	@property
	def ping(self) -> int:
		""" returns the client's ping """
		return int(bascenev1.get_client_ping(self.client_id))

	@property
	def is_mute(self) -> bool:
		"""returns whether the client is mute or not."""
		return self.account_id in Client.__mute_clients

	def mute(self) -> None:
		"""mute this client."""
		if self.account_id not in Client.__mute_clients:
			Client.__mute_clients.add(self.account_id)
			return True
		# already mute.

	def unmute(self) -> None:
		"""unmute this client."""
		if self.account_id in Client.__mute_clients:
			Client.__mute_clients.discard(self.account_id)
			return True
		# not mute.

	def kick(self, time: int = 300) -> None:
		"""kick this client."""
		bascenev1.disconnect_client(self.client_id, ban_time=time)

	def success(self, message: str) -> None:
		"""show this client a success message."""
		utils.success(message, clients=[self.client_id])

	def error(self, message: str) -> None:
		"""show this client an error message."""
		utils.error(message, clients=[self.client_id])

	def send(self, message: str, sender: str | None = None) -> None:
		"""show this client a chat message."""
		utils.send(message, clients=[self.client_id], sender=sender)


class Player:
	"""Player object."""

	def __init__(self, player: bascenev1.SessionPlayer) -> None:
		self._player = player

	@property
	def name(self) -> str:
		"""name of the player."""
		if self.exists():
			return self._player.getname(True, True)
		return ""

	def handle(self, message) -> None:
		"""handles message for the player."""
		if self.is_alive():
			player = self._player.activityplayer
			player.actor.node.handlemessage(message)

	def exists(self) -> bool:
		"""returns whether the bascenev1.SessionPlayer exists."""
		return self._player.exists()

	def is_alive(self) -> bool:
		"""returns whether the bascenev1.Player is alive"""
		return self.exists() and self._player.activityplayer.is_alive()

	def remove(self) -> None:
		"""removes the player from game."""
		if self.exists():
			self._player.remove_from_game()

	def profiles(self) -> list[str]:
		"""returns the profiles of the session player.."""
		if self.exists():
			return self._player.inputdevice.get_player_profiles()
		return []

	def kill(self) -> None:
		"""kill this player."""
		self.handle(bascenev1.DieMessage())

	def freeze(self) -> None:
		""" freeze this player."""
		self.handle(bascenev1.FreezeMessage())

	def thaw(self) -> None:
		""" thaw this player."""
		self.handle(bascenev1.ThawMessage())
		
class Players:
	""" handles every player in session. """
	def handle(self, message) -> None:
		""" handles message for the all the players."""
		activity = bascenev1.get_foreground_host_activity()
		for player in activity.players:
			with activity.context:
				if player.is_alive():
					player.actor.node.handlemessage(message)
	
	def kill(self) -> None:
		""" kill all the players. """
		self.handle(bascenev1.DieMessage())

	def freeze(self) -> None:
		""" freeze all the players. """
		self.handle(bascenev1.FreezeMessage())

	def thaw(self) -> None:
		""" thaw all the players. """
		self.handle(bascenev1.ThawMessage())


def all_clients() -> list[Client]:
	"""returns a list of Client object."""
	clients = []
	for client in bascenev1.get_game_roster()[1:]:
		client_id = client["client_id"]
		account_id = client["account_id"]
		in_lobby = not client["players"]
		if not in_lobby:
			name = client["players"][0]["name"]
		else:
			name = client["display_string"]
		clients.append(Client(client_id, account_id, name, in_lobby))
	return clients


def fetch_client(client_id: int | str) -> Client | None:
	"""fetches and tries to returns a valid client."""
	# manual converting to avoid str cases.
	client_id = int(client_id)
	for client in all_clients():
		if client.client_id == client_id:
			return client
	return


def fetch_player(player_index: int | str) -> Player | None:
	"""fetches and tries to returns a valid player."""
	# manual converting to avoid str cases.
	player_index = int(player_index)
	if session := bascenev1.get_foreground_host_session():
		sessionplayer = session.sessionplayers[player_index]
		return Player(sessionplayer)
