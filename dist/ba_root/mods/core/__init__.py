"""core package that initializes and binds storage methods."""

from ._config import config
from ._roles import roles
from ._clients import (
	Client,
	Player,
	Players,
	all_clients,
	fetch_client,
	fetch_player
)
from ._utils import (
	success,
	error,
	send,
    Text
)
from ._enums import (
	Authority,
	Role,
	Playlist,
	Utility
)

__all__ = [
    "config",
    "roles",
    "Client",
    "Player",
    "Players",
    "all_clients",
    "fetch_client",
    "fetch_player",
    "success",
    "error",
    "send",
    "Text",
    "Authority",
    "Role",
    "Playlist",
    "Utility",
]