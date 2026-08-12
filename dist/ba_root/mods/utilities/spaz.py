""" modified spaz functionality. """
from __future__ import annotations
import bascenev1
import core

class Text:
	""" text which spawns on the node's head. """
	def __init__(self, node: bascenev1.Node, text: str) -> None:
		color = (1, 1, 1) # default
		self.node = node
		math = bascenev1.newnode(
			"math", 
			owner = self.node,
			attrs = {
				"input1": (0, 1.38, 0),
				"operation": "add"
			}
		)
		self.node.connectattr("torso_position", math, "input2")
		
		self.text = bascenev1.newnode(
			"text",
			owner = self.node,
			attrs = {
				"text": text,
				"in_world": True,
				"shadow": 1.1,
				"flatness": 1.0,
				"color": color,
				"scale": 0.01,
				"h_align": "center"
			}
		)
		math.connectattr("output", self.text, "position")
		# bascenev1.animate_array(self.text, "scale", {0: 0.0, 1: 0.01})
		
def attach_rank(self, player: bascenev1.Player) -> None:
	""" attaches the rank on player head. """
	if player and player.sessionplayer:
		account_id = player.sessionplayer.get_account_id()
		stats = core.stats.get(account_id)
		if stats:
			rank = f"#{stats['rank']}"
			Text(self.node, rank)
