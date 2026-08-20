"""tournament teams session"""

from typing import override

from bascenev1._dualteamsession import DualTeamSession


class TournamentSession(DualTeamSession):
    """dual team session configured for tournament"""

    def __init__(self):
        super().__init__()
        # TODO: everything.

    @override
    def on_player_request(self, player):
        return super().on_player_request(player)
