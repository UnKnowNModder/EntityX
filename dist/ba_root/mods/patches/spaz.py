from collections.abc import Sequence

import bascenev1
from bascenev1lib.actor import playerspaz

from server import config
from stats import attach_rank

from . import patch_method


@patch_method(playerspaz.PlayerSpaz, "__init__", initial=True)
def new_init(
    self,
    player: bascenev1.Player,
    *,
    color: Sequence[float] = (1.0, 1.0, 1.0),
    highlight: Sequence[float] = (0.5, 0.5, 0.5),
    character: str = "Spaz",
    powerups_expire: bool = True,
):
    """modified constructor of PlayerSpaz class."""
    if config.stats.enable:
        attach_rank(self, player)
