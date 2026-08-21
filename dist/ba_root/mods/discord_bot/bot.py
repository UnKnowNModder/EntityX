"""bot.py for discord bot functionality."""

import logging

import discord
from discord import Activity, ActivityType, Intents, Interaction, app_commands
from discord.ext import commands

from discord_bot.client import GameClient
from discord_bot.ui import CaptainRegistrationModal, SoloRegistrationModal, TeamInvitationView
from roles import roles
from server import config
from server.enums import Authority, Role, SeriesType, TournamentType
from tournament import tournament
from tournament.schema import SeasonSchema


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = Intents.default()
        intents.members = True
        super().__init__(
            command_prefix=[],
            intents=intents,
            owner_id=config.discord.owner_id,
        )

    async def setup_hook(self) -> None:
        self.add_view(TeamInvitationView("9999"))
        self.tree.on_error = self.on_app_cmd_error
        await self.add_cog(Commands(self))

    async def on_app_cmd_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            return
        print(f"Discord: error: {error}")

    async def on_ready(self):
        """the bot is ready"""
        print(f"Discord: logged in as {self.user}")

        # change presence and sync slash commands.
        await self.change_presence(
            activity=Activity(type=ActivityType.watching, name="Bombsquad")
        )
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)


def require(authority: Authority):
    """decorator for authority check"""

    async def examine(interaction: Interaction) -> bool:
        if interaction.user.id == interaction.client.owner_id:
            return True

        if roles.get_authority_level(interaction.user.id) >= authority:
            return True

        await interaction.response.send_message(
            "You are not authorised", ephemeral=True
        )
        return False

    return app_commands.check(examine)


class Commands(commands.Cog):
    """cog for slash commands"""

    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.client = GameClient()

    @app_commands.command(name="createseason")
    @app_commands.describe(type="Tournament Type", series="Series Type")
    @require(authority=Authority.LEADER)
    async def create_season(
        self, interaction: Interaction, type: TournamentType, series: SeriesType
    ) -> None:
        """creates a tournament season"""
        if int(tournament.read().active_season):
            await interaction.response.send_message(
                "Cannot create! a season is going on."
            )
            return

        from datetime import datetime, timedelta, timezone

        ist = timezone(timedelta(hours=5, minutes=30))

        schema = SeasonSchema(
            series=series, type=type, created_at=str(datetime.now(ist))
        )
        tournament.create_season(schema=schema)
        await interaction.response.send_message(
            f"The season has been created with {type} and {series}"
        )

    @app_commands.command(name="participate")
    async def participate(self, interaction: Interaction) -> None:
        """participate in tournament"""
        db = tournament.read()
        season_id = db.active_season
        if not int(season_id):
            await interaction.response.send_message(
                "There is no tournament ongoing.", ephemeral=True
            )
            return

        season_data = tournament.get_season(season_id=season_id)
        size = season_data.type.count
        if size > 1:
            # for not-solo seasons
            await interaction.response.send_modal(CaptainRegistrationModal(season_id=season_id, size=size-1))
        else:
            # for solo seasons
            await interaction.response.send_modal(
                SoloRegistrationModal(season_id=season_id)
            )

    @app_commands.command(name="say")
    @app_commands.describe(message="The text to send")
    @require(Authority.ADMIN)
    async def say(self, interaction: Interaction, message: str) -> None:
        """sends message in game chat"""
        self.client.send_action(
            action="message", text=message, sender=interaction.user.display_name
        )
        await interaction.response.send_message("Done!", ephemeral=True)

    @app_commands.command(name="cmd")
    @app_commands.describe(command="The chat-command to execute")
    async def cmd(self, interaction: Interaction, command: str) -> None:
        """executes a chat command in game."""
        self.client.send_action(
            action="command", command=command, account_id=interaction.user.id
        )
        await interaction.response.send_message("Done!", ephemeral=True)

    @app_commands.command(name="list")
    async def list(self, interaction: Interaction) -> None:
        """lists all the players from game"""
        await interaction.response.defer(ephemeral=True)
        response = await self.client.send_action(action="list", response=True)

        if not response["players"]:
            await interaction.followup.send("There are no players in the server")
            return

        heads = "{0:^16}{1:^15}\n"
        result = ""
        for player in response["players"]:
            result += heads.format(player["name"], player["client_id"])

        await interaction.followup.send(result)

    @app_commands.command(name="admin")
    @app_commands.describe(user="the user to add/remove")
    @require(Authority.LEADER)
    async def admin(self, interaction: Interaction, user: discord.Member) -> None:
        """to add/remove a user to admins"""
        if roles.has_role(Role.ADMIN, user.id):
            roles.remove(Role.ADMIN, user.id)
            await interaction.response.send_message(
                f"{user.name} has been removed from admins", ephemeral=True
            )
        else:
            roles.add(Role.ADMIN, user.id)
            await interaction.response.send_message(
                f"{user.name} has been added to admins", ephemeral=True
            )

    @app_commands.command(name="owner")
    @app_commands.describe(user="the user to add/remove")
    @require(Authority.HOST)
    async def owner(self, interaction: Interaction, user: discord.Member) -> None:
        """to add/remove a user to owners"""
        if roles.has_role(Role.LEADER, user.id):
            roles.remove(Role.LEADER, user.id)
            await interaction.response.send_message(
                f"{user.name} has been removed from owners", ephemeral=True
            )
        else:
            roles.add(Role.LEADER, user.id)
            await interaction.response.send_message(
                f"{user.name} has been added to owners", ephemeral=True
            )


if __name__ == "__main__":
    bot = DiscordBot()
    bot.run(token=config.discord.token, log_level=logging.WARNING)
