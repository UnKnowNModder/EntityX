""" config storage core. """
from __future__ import annotations
from pathlib import Path
from ._storage import Storage
from ._enums import Utility, Playlist

class Config(Storage):
	"""config storage class."""

	def __init__(self) -> None:
		super().__init__("config.json")
		self.toml = self.directory.parents[3] / "config.toml"
		self.bootstrap()

	def bootstrap(self) -> None:
		"""creates essential files."""
		if not self.path.exists():
			config = {}
			config["tournament"] = {"webhook_url": "YOUR RESULT ANNOUNCEMENT WEBHOOK URL HERE.", "include_score": True}
			config["stats"] = {"enable": False, "leaderboard": True}
			config["auth_verification"] = {"enable": False, "days": 7}
			config[Utility.WHITELIST] = False
			config[Utility.SPECTATOR] = True
			self.commit(config)

	def toggle(self, utility: Utility) -> bool:
		"""toggles the utility."""
		config = self.read()
		config[utility] = not config.get(utility, True)
		self.commit(config)
		return config[utility]

	def set_playlist(self, playlist: Playlist) -> None:
		"""changes the playlist code in .toml file."""
		code = playlist.value
		with self.toml.open("r") as f:
			lines = f.readlines()
		with self.toml.open("w") as f:
			for line in lines:
				if line.strip().startswith(f"playlist_code ="):
					f.write(f"playlist_code = {code}\n")
				else:
					f.write(line)

	@property
	def whitelist(self) -> bool:
		"""returns whether whitelist is enable or not."""
		config = self.read()
		return config[Utility.WHITELIST]

	@property
	def spectator(self) -> bool:
		"""returns whether spectator is enable or not."""
		config = self.read()
		return config[Utility.SPECTATOR]