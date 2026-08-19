""" tournament-related commands. """

from . import on_command
from tournament import tournament
from tournament.storage import Registration
from server.clients import Client

@on_command(name="/register")
def register(client: Client):
    """ verifies and registers into the tournament."""
    season_id = tournament.read().active_season
    if not int(season_id):
        client.error("There is no tournament ongoing.")
        return
    registration = Registration(season_id=season_id)
    status = registration.verify(client.account_id, device_uuid=client.public_uuid)
    if status:
        client.success("You have been successfully verified and registered.")
