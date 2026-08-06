""" modified spaz functionality. """
from __future__ import annotations
from typing import Sequence
import bascenev1 as bs
import bacore
from .utils import replace_method
from bascenev1lib.actor import playerspaz

class Text:
	""" text which spawns on the node's head. """
	def __init__(self, node: bs.Node, text: str) -> None:
		color = (1, 1, 1) # default
		self.node = node
		math = bs.newnode(
			"math", 
			owner = self.node,
			attrs = {
				"input1": (0, 1.38, 0),
				"operation": "add"
			}
		)
		self.node.connectattr("torso_position", math, "input2")
		
		self.text = bs.newnode(
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
		# bs.animate_array(self.text, "scale", {0: 0.0, 1: 0.01})
		
def attach_rank(self, player: bs.Player) -> None:
	""" attaches the rank on player head. """
	if player and player.sessionplayer:
		account_id = player.sessionplayer.get_account_id()
		stats = bacore.stats.get(account_id)
		if stats:
			rank = f"#{stats['rank']}"
			Text(self.node, rank)


@replace_method(playerspaz.PlayerSpaz, "__init__", initial = True)
def new_init(self,player: bs.Player,*,color: Sequence[float] = (1.0, 1.0, 1.0),highlight: Sequence[float] = (0.5, 0.5, 0.5),character: str = "Spaz",powerups_expire: bool = True):
	""" modified constructor of PlayerSpaz class. """
	config = bacore.config.read()
	if config["stats"]["enable"]:
		attach_rank(self, player)
