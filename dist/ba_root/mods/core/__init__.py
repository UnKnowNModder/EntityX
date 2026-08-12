"""core package that initializes and binds storage methods."""

# ba_meta require api 9

import babase
from ._config import config
from ._roles import roles
from ._stats import stats
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
	send
)
from ._enums import (
	Authority,
	Role,
	Playlist,
	Utility
)

# ba_meta export babase.Plugin
class Initialize(babase.Plugin):
	"""initializes and bootstraps the storages."""

	def __init__(self) -> None:
		config.bootstrap()
		roles.bootstrap()
		stats.bootstrap()
		print("✅ Initiated storages. ")
