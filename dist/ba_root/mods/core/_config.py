""" config storage core. """
from __future__ import annotations
from pathlib import Path
import re
from ._storage import Storage
from ._enums import Utility, Playlist

class Config(Storage):
	"""config storage class."""

	def __init__(self) -> None:
		super().__init__("config.json")
		self.toml = self.directory.parents[2] / "config.toml"

	def bootstrap(self) -> None:
		"""creates essential files."""
		if not self.path.exists():
			config = {}
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
		content = self.toml.read_text(encoding="utf-8")
		# match with regex.
		pattern = r"^(playlist_code\s*=\s*)[^\r\n#]+"
		new_content = re.sub(pattern, fr"\g<1>{code}", content, flags=re.MULTILINE)
		# store to temp file first.
		temp_file = self.toml.with_suffix(".toml.tmp")
		temp_file.write_text(new_content, encoding="utf-8")
		# replace with oriignal safely.
		temp_file.replace(self.toml)

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

config = Config()