""" bot.py for discord bot functionality. """

import json
import socket
import logging
from discord import Intents, app_commands, Interaction, Activity, ActivityType
from discord.ext import commands
from server import config
from server.enums import Authority
from roles import roles


class GameClient:
    """ client for sending json payloads to our server's socket tunnel. """
    def __init__(self, host: str = "127.0.0.1"):
        self.host = host
        self.port = config.discord.port

    def send(self, payload: dict) -> None:
        """ sends payload dict"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.sendto(json.dumps(payload).encode("utf-8"), (self.host, self.port))
            except Exception as e:
                print(f"Error while sending payload to socket tunnel: {e}")
    
    def say(self, text: str, sender: str | None = None):
        """ sends chat message to the game chat"""
        payload = {
            "command": "message",
            "text": text,
            "sender": sender
        }
        self.send(payload)

    def kick(self, client_id: int):
        """ kicks the player"""
        self.say(f"/kick {client_id}")

    def quit(self):
        """ quits"""
        self.say("/quit")

    def limit(self, count: int):
        """ server players count limit"""
        self.say(f"/limit {count}")

    def teams(self):
        """ playlist to teams"""
        self.say("/teams")

    def ffa(self):
        """ playlist to ffa"""
        self.say("/ffa")


class DiscordBot(commands.Bot):
    def __int__(self) -> None:
        super().__init__(command_prefix=[], intents=Intents.default(), owner_id=config.discord.owner_id)

    async def setup_hook(self) -> None:
        self.tree.on_error = self.on_app_cmd_error
        await self.add_cog(Commands)

    async def on_app_cmd_error(self, interaction: Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CheckFailure):
            return
        print(f"discord bot: error: {error}")

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

    @app_commands.command(name="say")
    @app_commands.describe(message = "The text to send")
    @require(Authority.ADMIN)
    async def say(self, interaction: Interaction, message: str) -> None:
        """ sends message in game chat"""
        self.client.say(message, interaction.user.display_name)

    @app_commands.command(name="kick")
    @app_commands.describe(client_id = "Player's client-id to kick")
    @require(Authority.ADMIN)
    async def kick(self, interaction: Interaction, client_id: int) -> None:
        """ kicks a player"""
        self.client.kick(client_id)

    @app_commands.command(name="limit")
    @app_commands.describe(count = "players count")
    @require(Authority.ADMIN)
    async def limit(self, interaction: Interaction, count: int) -> None:
        """ limit players count"""
        self.client.limit(count)

    @app_commands.command(name="quit")
    @require(Authority.ADMIN)
    async def quit(self, interaction: Interaction) -> None:
        """ quit the game server"""
        self.client.quit()

    @app_commands.command(name="teams")
    @require(Authority.ADMIN)
    async def teams(self, interaction: Interaction) -> None:
        """ playlist to teams"""
        self.client.teams()

    @app_commands.command(name="ffa")
    @require(Authority.ADMIN)
    async def ffa(self, interaction: Interaction) -> None:
        """ playlist to ffa"""
        self.client.ffa()


if __name__ == "__main__":
    bot = DiscordBot()
    bot.run(token=config.discord.token, log_level=logging.WARNING)