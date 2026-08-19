""" bot.py for discord bot functionality. """
import asyncio
import json
import socket
import logging
from discord import Intents, app_commands, Interaction, Activity, ActivityType
from discord.ext import commands
import discord
from server import config
from server.enums import Authority, Role, TournamentType, SeriesFormat
from roles import roles
from tournament import tournament
from tournament.schema import SeasonSchema


class GameClient:
    """ client for sending json payloads to our server's socket tunnel. """
    def __init__(self, host: str = "127.0.0.1"):
        self.host = host
        self.port = config.discord.port

    def send_action(self, action: str, response: bool = False, **kwags) -> dict | None:
        """ sends action to tunnel"""
        payload = json.dumps({"action": action, **kwags}).encode("utf-8")
        # run in background loop
        return asyncio.get_running_loop().run_in_executor(None, self.send, payload, response)


    def send(self, payload: bytes, response: bool) -> dict | None:
        """ sends payload"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.sendto(payload, (self.host, self.port))

                # check if we need response.
                if not response:
                    return

                sock.settimeout(2.0)
                data, _ = sock.recvfrom(4096)
                # return the dict.
                return json.loads(data.decode("utf-8"))

            except Exception as e:
                print(f"Error while sending payload to socket tunnel: {e}")
    


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix=[], intents=Intents.default(), owner_id=config.discord.owner_id)

    async def setup_hook(self) -> None:
        self.tree.on_error = self.on_app_cmd_error
        await self.add_cog(Commands(self))

    async def on_app_cmd_error(self, interaction: Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CheckFailure):
            return
        print(f"Discord: error: {error}")

    async def on_ready(self):
        """ the bot is ready"""
        print(f"Discord: logged in as {self.user}")

        # change presence and sync slash commands.
        await self.change_presence(activity=Activity(type=ActivityType.watching, name="Bombsquad"))
        for guild in self.guilds:
            self.tree.clear_commands(guild=guild)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

def require(authority: Authority):
    """ decorator for authority check"""

    async def examine(interaction: Interaction) -> bool:
        if interaction.user.id == interaction.client.owner_id:
            return True

        if roles.get_authority_level(interaction.user.id) >= authority:
            return True

        await interaction.response.send_message("You are not authorised", ephemeral=True)
        return False
    return app_commands.check(examine)
    

class Commands(commands.Cog):
    """ cog for slash commands"""
    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.client = GameClient()

    @app_commands.command(name="createseason")
    @app_commands.describe()
    @require(authority=Authority.LEADER)
    async def create_season(self, interaction: Interaction, title: str, type: TournamentType, series: SeriesFormat) -> None:
        """ creates a tournament season"""
        if tournament.read().active_season:
            await interaction.response.send_message("Cannot create! a season is going on.")
            return

        from datetime import datetime, timezone, timedelta
        ist = timezone(timedelta(hours=5, minutes=30))
        
        schema = SeasonSchema(title=title, series=series, type=type, created_at=datetime.now(ist))
        tournament.create_season(schema=schema)
        await interaction.response.send_message(f"The season: {title} has been created with {type} and {series}")

    @app_commands.command(name="say")
    @app_commands.describe(message = "The text to send")
    @require(Authority.ADMIN)
    async def say(self, interaction: Interaction, message: str) -> None:
        """ sends message in game chat"""
        self.client.send_action(action="message", text=message, sender=interaction.user.display_name)
        await interaction.response.send_message("Done!", ephemeral=True)

    @app_commands.command(name="cmd")
    @app_commands.describe(command = "The chat-command to execute")
    async def cmd(self, interaction: Interaction, command: str) -> None:
        """ executes a chat command in game."""
        self.client.send_action(action="command", command=command, account_id=interaction.user.id)
        await interaction.response.send_message("Done!", ephemeral=True)

    @app_commands.command(name="list")
    async def list(self, interaction: Interaction) -> None:
        """ lists all the players from game"""
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
        """ to add/remove a user to admins"""
        if roles.has_role(Role.ADMIN, user.id):
            roles.remove(Role.ADMIN, user.id)
            await interaction.response.send_message(f"{user.name} has been removed from admins", ephemeral=True)
        else:
            roles.add(Role.ADMIN, user.id)
            await interaction.response.send_message(f"{user.name} has been added to admins", ephemeral=True)

    @app_commands.command(name="owner")
    @app_commands.describe(user="the user to add/remove")
    @require(Authority.HOST)
    async def owner(self, interaction: Interaction, user: discord.Member) -> None:
        """ to add/remove a user to owners"""
        if roles.has_role(Role.LEADER, user.id):
            roles.remove(Role.LEADER, user.id)
            await interaction.response.send_message(f"{user.name} has been removed from owners", ephemeral=True)
        else:
            roles.add(Role.LEADER, user.id)
            await interaction.response.send_message(f"{user.name} has been added to owners", ephemeral=True)

    @app_commands.command(name="participate")
    @app_commands.describe(account_id = "The v2 account-id (looks like a-xxx....)")
    async def participate(self, interaction: Interaction, account_id: str) -> None:
        """ participate in tournament"""
        season_id = tournament.read().active_season
        if not season_id:
            await interaction.response.send_message("There is no tournament ongoing.", ephemeral=True)
            return

        # tournament role
        role_name = "Participant"
        guild = interaction.guild
        role = discord.utils.get(guild.roles, role_name)

        if not role:
            # create it
            guild.create_role(name=role_name, color=discord.Color.dark_teal)

        # pre-register in our database
        from tournament.storage import Registration
        registration = Registration(season_id=season_id)
        success = registration.pre_register(account_id=account_id, discord_user_id=str(interaction.user.id))
        if success is None:
            await interaction.response.send_message("Please ver  ify yourself in the game with /register with your asssigned account.", ephemeral=True)
            return
        elif not success:
            await interaction.response.send_message("You are already registered.", ephemeral=True)
            return

        # assign the role and respond.
        await interaction.user.add_roles(role)
        await interaction.response.send_message("You have been pre-registered, verify yourself in the game with /register with your assigned account.")


if __name__ == "__main__":
    bot = DiscordBot()
    bot.run(token=config.discord.token, log_level=logging.WARNING)