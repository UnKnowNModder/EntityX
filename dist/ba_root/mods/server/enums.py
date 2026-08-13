"""types file for storage."""

from enum import IntEnum, StrEnum


class Authority(IntEnum):
    """enum class for authority levels."""

    USER = 0
    WHITELIST = 1
    ADMIN = 2
    LEADER = 3
    HOST = 10  # for server.


class Role(StrEnum):
    """enum class for roles."""

    LEADER = "leaders"
    ADMIN = "admins"
    WHITELIST = "whitelist"
    BANLIST = "banlist"


class Utility(StrEnum):
    """enum class for utilities."""

    WHITELIST = "whitelist"
    SPECTATOR = "spectator"
    POWERUPS = "powerups"


class Playlist(IntEnum):
    """enum class for playlists."""

    TEAMS = 617192
    FFA = 617193
