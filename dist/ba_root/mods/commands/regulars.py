""" regular commands. """
from __future__ import annotations
from . import on_command
from core import Client, all_clients
import bascenev1

@on_command(name="/list", aliases=["/ls"])
def list(client: Client):
	"""shows the client, a list of players."""
	heads = "{0:^16}{1:^15}{2:^15}\n"
	sep = "--------------------------------------------------------------\n"
	string = heads.format("Name", "Client ID", "Index ID") + sep
	if session := bascenev1.get_foreground_host_session():
		for index, player in enumerate(session.sessionplayers):
			string += heads.format(player.getname(True, True), player.inputdevice.client_id, index)
	for i in bascenev1.get_game_roster()[1:]:
		if str(i["client_id"]) not in string:
			string += heads.format(i["display_string"], i["client_id"], "<in lobby>")
	client.success(string)

@on_command(name="/stats")
def show_stats(client: Client) -> None:
	"""shows the client his stats."""
	from stats import stats
	if stats := stats.get(client.account_id):
		message = "{} | score: {} | kills: {} | deaths: {} | games: {}".format(stats["rank"], stats["score"], stats["kills"], stats["deaths"], stats["games"])
		client.send(message, sender = "rank")
		return
	client.error("Your stats will be available soon.")


@on_command(name="/pb", aliases=["/ac", "/id"])
def show_account_id(client: Client, target: Client):
	"""Shows the client's or target's account ID."""
	target = target or client
	client.send(target.account_id, sender=f"{target.name}'s ID")


@on_command(name="/pm", aliases=["/dm"], usage="/pm <client id> <message>")
def private_message(client: Client, target: Client, message: str):
	"""Sends a private message to target client."""
	name = f"{client.name} (pvt)"
	target.send(message, sender=name)
	client.send(message, sender=name)

@on_command(name="/ping", aliases=["/ms"])
def show_ping(client: Client):
	"""shows the client's ping"""
	message = "Your ping: {} ms".format(client.ping)
	client.send(message)

@on_command(name="/pingall", aliases=["/msall"])
def show_all_pings(client: Client):
	"""shows all the connected clients' ping"""
	text_format = "{}'s ping: {} ms"
	for _client in all_clients():
		client.send(text_format.format(_client.name, _client.ping))