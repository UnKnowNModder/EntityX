import core
from bascenev1._activitytypes import ScoreScreenActivity
from utilities.stats import update_stats
from . import patch_method

@patch_method(ScoreScreenActivity, "on_begin", initial = True)
def new_on_begin(self) -> None:
	""" modified. """
	config = core.config.read()
	if config["stats"]["enable"]:
		update_stats(self._stats)