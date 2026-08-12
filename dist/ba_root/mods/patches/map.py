import core
from bascenev1._map import Map
from . import patch_method

@patch_method(Map, "__init__", initial = True)
def new_map_init(self, *args, **kwargs):
	config = core.config.read()
	if config["stats"]["enable"] and config["stats"]["leaderboard"]:
		core.stats.leaderboard(self.node)