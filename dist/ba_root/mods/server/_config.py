"""config storage core."""

from __future__ import annotations
import re, babase
from .storage import Storage
from .enums import Utility, Playlist


class ConfigDict(dict):
    """for dot notation (ah i love easy things..)"""

    def __getitem__(self, key: str):
        item = super().__getitem__(key)
        if isinstance(item, dict) and not isinstance(item, ConfigDict):
            return ConfigDict(item)
        return item

    def __getattr__(self, setting: str):
        try:
            return self[setting]
        except KeyError:
            raise AttributeError(f"Config has no setting: {setting}")


class Config(Storage):
    """config storage class."""

    def __init__(self) -> None:
        super().__init__("config.json")
        self.toml = self.directory.parents[2] / "config.toml"
        self.template_file = (
            self.directory.parents[1]
            / babase.env()["python_directory_app"]
            / "config_template.json"
        )

    def bootstrap(self) -> None:
        """creates essential files."""
        if not self.path.exists():
            # mhm.. we take it from template file.
            config = self.read(self.template_file)
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
        new_content = re.sub(pattern, rf"\g<1>{code}", content, flags=re.MULTILINE)
        # store to temp file first.
        temp_file = self.toml.with_suffix(".toml.tmp")
        temp_file.write_text(new_content, encoding="utf-8")
        # replace with oriignal safely.
        temp_file.replace(self.toml)

    def __getattr__(self, key: str):
        data = ConfigDict(self.read())
        if key in data:
            return data[key]
        raise AttributeError(f"Config has no setting: {key}")


config = Config()
