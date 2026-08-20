"""defines base storage class."""

from __future__ import annotations

import json
from pathlib import Path

MODS_DIR: Path = Path(__file__).resolve().parent.parent


class Storage:
    """storage class."""

    def __init__(self, filename: str, subfolder: str | Path | None = None) -> None:
        self._cache = {}
        self._mtime = {}
        if subfolder:
            self.directory = MODS_DIR / subfolder
        else:
            self.directory = MODS_DIR
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / filename

    def read(self, external_path: Path | None = None) -> dict:
        """reads the data from the file."""
        target_path = external_path or self.path
        try:
            current_mtime = target_path.stat().st_mtime
            if (
                target_path in self._cache
                and self._mtime.get(target_path) == current_mtime
            ):
                # return from cache
                return self._cache[target_path]
            with target_path.open("r") as f:
                data = json.load(f)
                self._cache[target_path] = data
                self._mtime[target_path] = current_mtime
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def commit(self, data: dict | list, external_path: Path | None = None) -> None:
        """commits the data to the file."""
        target_path = external_path or self.path
        with target_path.open("w") as f:
            json.dump(data, f, indent=4)

        # update
        self._cache[target_path] = data
        self._mtime[target_path] = target_path.stat().st_mtime
