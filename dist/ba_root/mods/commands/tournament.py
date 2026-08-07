""" cheat commands. """
from __future__ import annotations
from . import on_command
from bacore import Authority, Client, tournament

@on_command(name="/confirm")
def confirm(client: Client) -> None:
	"""confirms the client to the tournament match."""
	tournament.confirm(client)

@on_command(
	name="/listmatch", aliases=["/lm", "/matches"], authority=Authority.LEADER
)
def list_matches(client: Client):
	""" lists all the tournament matches. """
	for match in tournament.read():
		message = f"{match['teams'][0]['name']} vs {match['teams'][1]['name']} [series: {match['series']}]"
		client.send(message, sender=f"{match['id']}")