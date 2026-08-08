""" stats storage core. """
from __future__ import annotations
from ._storage import Storage
import bascenev1

class Stats(Storage):
	"""stats storage class."""

	def __init__(self) -> None:
		super().__init__("stats.json")
		self.top = []

	def bootstrap(self) -> None:
		"""creates essential files."""
		if not self.path.exists():
			self.commit({})
	
	def get(self, account_id: str) -> dict[str, int] | None:
		""" returns the stats of the account. """
		stats = self.read()
		if account_id in stats:
			return stats[account_id]
	
	def sort(self) -> dict[str, dict]:
		""" sorts the stats in descending order. """
		stats = self.read()
		sorted_raw = sorted(
			stats.items(),
			key=lambda item: (item[1]["score"], item[1]["kills"], -item[1]["deaths"], item[1]["games"]),
			reverse = True
		)
		sorted_stats = {}
		self.top.clear()
		for rank, (account_id, data) in enumerate(sorted_raw, start=1):
			if rank <= 3:
				self.top.append(data["name"])
			data = dict(data) # copying to avoid mutating og ref.
			data["rank"] = rank
			sorted_stats[account_id] = data
		self.commit(sorted_stats)
	
	def leaderboard(self, owner: bascenev1.Node | None) -> None:
		""" leaderboard for top rankers. """
		y_pos = -80
		for rank, name in enumerate(self.top, start = 1):
			# image node
			self.image = bascenev1.newnode(
				"image",
				owner = owner,
				attrs = {
					"scale": (300, 30),
					"texture": bascenev1.gettexture("uiAtlas2"),
					"position": (0, y_pos),
					"attach": "topRight",
					"opacity": 0.5,
					"color": (0.7, 0.3, 0)
				}
			)
			
			# text node
			self.text = bascenev1.newnode(
				"text",
				owner = owner,
				attrs = {
					"text": f"#{rank} " + name[:10] + "..",
					'flatness': 1.0,
					'h_align': 'left',
					'h_attach': 'right',
					'v_attach': 'top',
					'v_align': 'center',
					'position': (-140, y_pos),
					'scale': 0.7,
					'color': (0.7, 0.4, 0.3)
				}
			)
			y_pos -= 35


stats = Stats()