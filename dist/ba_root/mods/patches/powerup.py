import bascenev1
from typing import Sequence
from . import patch_method


@patch_method(bascenev1, "get_default_powerup_distribution")
def powerup_distribution() -> Sequence[tuple[str, int]]:
	return (
		('triple_bombs', 3),
		('ice_bombs', 3),
		('punch', 0),
		('impact_bombs', 3),
		('land_mines', 2),
		('sticky_bombs', 3),
		('shield', 0),
		('health', 0),
		('curse', 0),
	)