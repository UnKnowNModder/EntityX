""" regular commands. """
from __future__ import annotations
from . import on_command
from bacore import Client, all_clients
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