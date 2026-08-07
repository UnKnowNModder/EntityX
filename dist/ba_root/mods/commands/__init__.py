"""core command package."""
# ba_meta require api 9
# thanks to snoweee for enlightening me with decorators <3
from __future__ import annotations
from bacore import Authority, Players, Client, fetch_client, fetch_player
import importlib, babase, inspect
from pathlib import Path

_commands = {}


def on_command(
	name: str,
	aliases: list[str] = [],
	authority: Authority = Authority.USER,
	usage: str = "",
):
	"""decorator to register a command."""

	def decorator(function):
		cmd = {"call": function, "authority": authority, "usage": usage}
		_commands[name] = cmd
		if aliases:
			for aliase in aliases:
				_commands[aliase] = cmd
		return function

	return decorator


def command_line(msg: str, client: Client) -> str | None:
	"""processes a chat message as a command.
	command line as the name says."""
	if not msg.startswith("/"):
		return msg
	command = msg.split()[0].lower()
	args = msg.split()[1:]
	if command in _commands:
		cmd = _commands[command]
		if client.authority >= cmd["authority"]:
			function = cmd["call"]
			sign = inspect.signature(function)
			params = [param for param in sign.parameters]
			try:
				if "message" in params and "target" in params:
					message = " ".join(args[1:])
					target = fetch_client(args[0])
					function(client, target, message)
				elif "args" in params:
					function(client, args)
				elif "target" in params:
					target = fetch_client(args[0])
					function(client, target)
				elif "player" in params:
					player = fetch_player(args[0])
					function(client, player)
				elif "players" in params:
					players = Players()
					function(client, players)
				elif "account_id" in params:
					function(client, args[0])
				else:
					function(client)
			except Exception as err:
				print("err:", err)
				client.error(f"Usage: {cmd['usage']}")
			return
	# wasn't any known command.
	return msg

def control_message(msg: str, client_id: int) -> bool:
	""" controls the message for filters/commands. """
	client = Client(client_id) if client_id == -1 else fetch_client(client_id)
	if client and msg:
		if not client.authenticity:
			auth_code = client.get_auth_code()
			if not client.verify_auth_code(msg.split()[0]):
				client.error(f"Your auth code is: {auth_code}\nPlease enter in chat to verify.")
			return
		if client.is_mute:
			print(f"{client.name} (muted): {msg}")
			return
		return command_line(msg, client)
	return

def _load_commands():
    """automatically imports command files in the directory."""
    package_dir = Path(__file__).parent
    for file in package_dir.glob("*.py"):
        if file.stem == "__init__":
            continue
        module_name = f"{__package__}.{file.stem}"
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"⚠️ Failed to load command file {file.stem}")

# ba_meta export babase.Plugin
class Load(babase.Plugin):
	def __init__(self) -> None:
		_load_commands()
		print("✅ Loaded commands. ")
