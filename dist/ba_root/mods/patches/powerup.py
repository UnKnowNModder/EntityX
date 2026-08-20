from collections.abc import Sequence

import bascenev1
from bascenev1lib.actor.powerupbox import PowerupBox

from server import config

from . import patch_method


@patch_method(bascenev1, "get_default_powerup_distribution")
def powerup_distribution() -> Sequence[tuple[str, int]]:
    powerups = config.powerups
    return tuple(powerups.distribution.items())


@patch_method(PowerupBox, "__init__")
def powerupbox_init(self, *args, **kwargs):
    if not config.powerups.enable:
        super(PowerupBox, self).__init__()
        return
    return powerupbox_init.original(self, *args, **kwargs)
