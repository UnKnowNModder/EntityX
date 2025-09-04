# ba_meta require api 9
from discord.ext import commands
from discord import app_commands
import discord, time, threading, asyncio
from discord.ui import Select, Button, View
import bacore, bascenev1, babase

class MatchSelect(Select):
	def __init__(self, view):
		self.parent_view = view
		options = [
			discord.SelectOption(
				label=f"{m['teams'][0]['name']} vs {m['teams'][1]['name']}",
				value=m["id"]
			)
			for m in bacore.tournament.read()
		]
		super().__init__(placeholder="Select a match to delete...", min_values=1, max_values=1, options=options)

	async def callback(self, interaction):
		self.parent_view.selected_match_id = int(self.values[0])
		await interaction.response.defer()

class DeleteMatchView(View):
	def __init__(self, survive: bool):
		super().__init__(timeout=None)
		self.survive = survive
		self.selected_match_id: int | None = None
		self.add_item(MatchSelect(self))
		self.add_item(Button(label="Delete", style=discord.ButtonStyle.danger, custom_id="delete"))

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		if interaction.data.get("custom_id") == "delete":
			if not self.selected_match_id:
				await interaction.response.send_message("Please select a match first.", ephemeral=True)
			else:
				bacore.tournament.discard(self.selected_match_id, self.survive)
				await interaction.response.edit_message(
					content=f"<:Delete:1411282698647113779> Match with ID `{self.selected_match_id}` has been deleted.",
					view=None
				)
			return False
		return True

class TeamSelect(Select):
	def __init__(self, placeholder, view, index):
		self.index = index
		self.parent_view = view
		options = [discord.SelectOption(label=team) for team in bacore.tournament.list_teams()]
		super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options)

	async def callback(self, interaction):
		self.parent_view.selections[self.index] = self.values[0]
		await interaction.response.defer()

class MakeMatchView(View):
	def __init__(self, series: int):
		super().__init__(timeout=None)
		self.series = series
		self.selections = [None, None]

		self.add_item(TeamSelect("Choose Team 1", self, 0))
		self.add_item(TeamSelect("Choose Team 2", self, 1))
		self.add_item(Button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm"))

	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		if interaction.data.get("custom_id") == "confirm":
			team1, team2 = self.selections
			if not team1 or not team2:
				await interaction.response.send_message("Please select both teams before confirming.", ephemeral=True)
			elif team1 == team2:
				await interaction.response.send_message("Teams must be different. Pick again.", ephemeral=True)
			else:
				bacore.tournament.pair_match(self.series, team1, team2)
				embed = discord.Embed(title="<:Battle:1411282502248697967> Match Settled ",description=f"**{team1}** will face off against **{team2}**!",color=0xff0000)
				embed.set_footer(text="May the best team win!")
				await interaction.response.edit_message(content=None, embed=embed, view=None)
			return False
		return True

class Zielc(commands.Bot):
	def __init__(self):
		config = bacore.config.read()
		super().__init__(command_prefix="!", intents=discord.Intents.all(), owner_id=config["bot"]["owner_id"])

	async def on_ready(self):
		print(f"Logged in as {self.user.name}")
		# self.tree.clear_commands(guild=None)
		# await self.tree.sync()
		await self.change_presence(status=discord.Status.dnd,
                               activity=discord.Activity(
                                 type=discord.ActivityType.watching,
                                 name="You!!."))
		for guild in self.guilds:
			self.tree.clear_commands(guild=guild)
			self.tree.copy_global_to(guild=guild)
			synced = await self.tree.sync(guild=guild)
			print("synced", len(synced), "commands to", guild.name)

class Commands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	async def interaction_check(self, interaction: discord.Interaction) -> bool:
		if interaction.command.name == "register":
			return True
		if (interaction.user.id != self.bot.owner_id) and (not bacore.roles.has_role(bacore.Role.LEADER, interaction.user.id)):
			await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
			return False
		return True
	
	@commands.command(name='owner')
	@commands.is_owner()
	async def owner(self, ctx, user: discord.Member):
		if bacore.roles.has_role(bacore.Role.LEADER, user.id):
			bacore.roles.remove(bacore.Role.LEADER, user.id)
			await ctx.send(f"{user.name}[`{user.id}`] has been removed as owner.")
		else:
			bacore.roles.add(bacore.Role.LEADER, user.id)
			await ctx.send(f"{user.name}[`{user.id}`] has been added as owner.")
	
	@app_commands.command(name="send")
	async def send(self, interaction, message: str):
		bascenev1.pushcall(bascenev1.Call(bascenev1.chatmessage, f"{message}", sender_override=str(interaction.user.display_name)), from_other_thread=True)
		await interaction.response.send_message(f"({message}) has been sent.", ephemeral=True)
	
	@app_commands.command(name="restart")
	async def restart(self, interaction):
		await interaction.response.send_message(f"Restarted the server.")
		babase.quit()
		
	@app_commands.command(name="register")
	@app_commands.describe(name="Your name", account_id="Your pb-id")
	async def register(self, interaction, name: str, account_id: str):
		guild = interaction.guild
		member = interaction.user
		role_name = "Tourny Participant"

		role = discord.utils.get(guild.roles, name=role_name)
		if not role:
			role = await guild.create_role(name=role_name, color=0xff0000)

		if role in member.roles:
			await interaction.response.send_message(f"{member.mention}, you are already registered!", ephemeral=True)
			return

		if bacore.tournament.register(name, [account_id]):
			await member.add_roles(role)
			await interaction.response.send_message(f"{member.mention}, you have been registered!")
		else:
			await interaction.response.send_message(f"{member.mention}, {name} already exists.", ephemeral=True)
	
	match = app_commands.Group(name="match", description="Match related commands")

	@match.command(name="make")
	async def make(self, interaction, series: int = 1):
		if not bacore.tournament.list_teams():
			await interaction.response.send_message("Teams unavailable.")
			return
		view = MakeMatchView(series)
		await interaction.response.send_message("Pick two teams to match:", view=view)

	@match.command(name="delete")
	@app_commands.describe(survive="Keep some data?")
	async def delete(self, interaction, survive: bool = False):
		if not bacore.tournament.read():
			await interaction.response.send_message("Matches unavailable.")
			return
		view = DeleteMatchView(survive)
		await interaction.response.send_message(view=view)

	@match.command(name="list")
	async def list(self, interaction):
		matches = bacore.tournament.list_match()
		embed = discord.Embed(
			title="<:list:1411281734863159336> Current Matches",
			description="\n".join(matches) or "No matches available.",
			color=0xff0000
		)
		embed.set_footer(text=f"Total Matches: {len(matches)}")
		await interaction.response.send_message(embed=embed)
	
	@match.command(name="rglist")
	async def rglist(self, interaction):
		teams = bacore.tournament.list_teams()
		embed = discord.Embed(
			title="<:list:1411281734863159336> Registered Teams",
			description="\n".join([f"**{i+1}** -> {team}" for i, team in enumerate(teams)]) or "No teams available.",
			color=0xff0000
		)
		embed.set_footer(text=f"Total Teams: {len(teams)}")
		await interaction.response.send_message(embed=embed)

# Global variables for bot management
bot_thread = None
bot_loop = None
bot_instance = None


async def start_bot():
    global bot_instance
    config = bacore.config.read()
    bot_instance = Zielc()
    await bot_instance.add_cog(Commands(bot_instance))
    try:
        await bot_instance.start(config["bot"]["token"])
    except asyncio.CancelledError:
        print("Bot task was cancelled")
    except Exception as e:
        print(f"Bot encountered an error: {e}")
    finally:
        print("Bot has been shut down")


def run_thread(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        # Cancel all tasks
        for task in asyncio.all_tasks(loop):
            task.cancel()
        # Run once more to process cancellations
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def run():
    global bot_thread, bot_loop
    if bot_thread is not None or bot_loop is not None: return
    
    bot_loop = asyncio.new_event_loop()
    bot_thread = threading.Thread(target=run_thread, args=(bot_loop,), daemon=True)
    bot_thread.start()
    
    # Start the bot in the background thread
    asyncio.run_coroutine_threadsafe(start_bot(), bot_loop)
    print("✅ Loaded discord bot.")


def shutdown():
    """Properly shutdown the bot and its thread"""
    global bot_thread, bot_loop, bot_instance
    
    if bot_loop is not None and bot_loop.is_running():
        # Close the bot connection
        if bot_instance:
            asyncio.run_coroutine_threadsafe(bot_instance.close(), bot_loop)
            time.sleep(0.5)
        
        # Stop the event loop
        bot_loop.call_soon_threadsafe(bot_loop.stop)
        
        # Wait for thread to finish with timeout
        if bot_thread and bot_thread.is_alive():
            bot_thread.join(timeout=5.0)
            if bot_thread.is_alive():
                print("Warning: Bot thread did not terminate gracefully")
        
        bot_loop = None
        bot_thread = None
        bot_instance = None

# ba_meta export babase.Plugin
class Start(babase.Plugin):
	def __init__(self):
		config = bacore.config.read()
		self.has_run = False
		if config["bot"]["enable"]:
			run()
			self.has_run = True
	
	def on_app_shutdown(self):
		if self.has_run:
			shutdown()
