"""defines base storage class."""

from __future__ import annotations
from pathlib import Path
from typing import Optional
import json

MODS_DIR: Path = Path(__file__).resolve().parent.parent


class Storage:
    """storage class."""

    def __init__(self, filename: str, subfolder: str | Path | None = None) -> None:
        self._cache = {}
        if subfolder:
            self.directory = MODS_DIR / subfolder
        else:
            self.directory = MODS_DIR
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / filename

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
