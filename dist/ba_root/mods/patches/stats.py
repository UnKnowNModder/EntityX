from bascenev1._activitytypes import ScoreScreenActivity

from server import config
from stats import update_stats
from stats import stats
from . import patch_method
import os


@patch_method(ScoreScreenActivity, "on_begin", initial=True)
def new_on_begin(self) -> None:
    """modified."""
    if os.getenv("BA_TOURNAMENT_MATCH") != "0":
        stats.tournament_path = stats.tournament_path / os.getenv("BA_TOURNAMENT_MATCH") / "stats.json"
        update_stats(self._stats, tournament=True)
        return
    if config.stats.enable:
        update_stats(self._stats)
