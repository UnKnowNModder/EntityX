"""the mods loader."""

# ba_meta require api 9
from traceback import format_exc

import babase
import bascenev1

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


# ba_meta export babase.Plugin
class Load(babase.Plugin):
    def __init__(self) -> None:
        try:
            self._load()
            print(f"{GREEN}Success: All the mods have been loaded.{RESET}")
        except:
            print(
                f"{RED}Error: The mods could not be loaded, contact the mod author.{RESET}"
            )
            print(f"The error is as following:\n {format_exc()}")

    def _load(self) -> None:
        # necessary imports
        import commands
        import patches
        import roles
        import server
        import stats
        import tournament
        import utilities

        # boot storages.
        server.config.bootstrap()
        roles.roles.bootstrap()
        roles.auth.bootstrap()
        stats.stats.bootstrap()
        tournament.tournament.bootstrap()

        # load patches.
        patches.load()

        # load commands.
        commands.load()

        # load utilities.
        utilities.load()

        # discord bot
        if server.config.discord.enable:
            import discord_bot

            discord_bot.load(self)

        # reload hooks.
        bascenev1.reload_hooks()
