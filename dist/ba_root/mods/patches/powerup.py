import bascenev1
from typing import Sequence
from . import patch_method
import core

@patch_method(bascenev1, "get_default_powerup_distribution")
def powerup_distribution() -> Sequence[tuple[str, int]]:
	powerups = core.config.read()["powerups"]
	return (
		('triple_bombs', powerups.get('triple_bombs', 3)),
		('ice_bombs', powerups.get('ice_bombs', 3)),
		('punch', powerups.get('punch', 0)),
		('impact_bombs', powerups.get('impact_bombs', 3)),
		('land_mines', powerups.get('land_mines', 2)),
		('sticky_bombs', powerups.get('sticky_bombs', 3)),
		('shield', powerups.get('shield', 0)),
		('health', powerups.get('health', 0)),
		('curse', powerups.get('curse', 0)),
	)