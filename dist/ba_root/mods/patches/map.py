from server import config
from bascenev1._map import Map
from stats import stats
from . import patch_method


@patch_method(Map, "__init__", initial=True)
def new_map_init(self, *args, **kwargs):
    if config.stats.enable and config.stats.leaderboard:
        stats.leaderboard(self.node)
