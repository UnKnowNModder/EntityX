from bascenev1._activitytypes import ScoreScreenActivity

from server import config
from stats import update_stats

from . import patch_method


@patch_method(ScoreScreenActivity, "on_begin", initial=True)
def new_on_begin(self) -> None:
    """modified."""
    if config.stats.enable:
        update_stats(self._stats)
