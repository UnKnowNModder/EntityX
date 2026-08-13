import bascenev1
from typing import Sequence
from . import patch_method
from server import config


@patch_method(bascenev1, "get_default_powerup_distribution")
def powerup_distribution() -> Sequence[tuple[str, int]]:
    powerups = config.powerups
    return (
        ("triple_bombs", powerups.triple_bombs),
        ("ice_bombs", powerups.ice_bombs),
        ("punch", powerups.punch),
        ("impact_bombs", powerups.impact_bombs),
        ("land_mines", powerups.land_mines),
        ("sticky_bombs", powerups.sticky_bombs),
        ("shield", powerups.shield),
        ("health", powerups.health),
        ("curse", powerups.curse),
    )
