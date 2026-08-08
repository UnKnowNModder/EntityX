"""defines base storage class."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import json, babase

class Storage:
	"""storage class."""

	def __init__(self, filename: str, is_dir: bool = False) -> None:
		self.directory = Path(babase.env()["python_directory_user"]) / "storage"
		self._cache = {}
		if is_dir:
			self.directory = self.directory / filename
		else:
			self.path = self.directory / filename
		self.directory.mkdir(parents=True, exist_ok=True)

	def read(self, external_path: Optional[Path] = None) -> dict:
		"""reads the data from the file."""
		target_path = external_path or self.path
		if target_path not in self._cache:
			try:
				with target_path.open("r") as f:
					self._cache[target_path] = json.load(f)
			except (FileNotFoundError, json.JSONDecodeError):
				return {}
		return self._cache[target_path]

	def commit(self, data: dict | list, external_path: Optional[Path] = None) -> None:
		"""commits the data to the file."""
		target_path = external_path or self.path
		with target_path.open("w") as f:
			self._cache[target_path] = data
			json.dump(data, f, indent=4)

