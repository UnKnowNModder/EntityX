"""tournament-related commands."""

from server.clients import Client
from tournament import tournament
from tournament.storage import Registration

from . import on_command


@on_command(name="/verify")
def verify(client: Client):
    """verifies the player in their team."""
    season_id = tournament.read().active_season
    if not int(season_id):
        client.error("There is no tournament ongoing.")
        return
    registration = Registration(season_id=season_id)
    status = registration.verify(client.account_id, device_uuid=client.public_uuid)
    if status:
        client.success("You have been successfully verified.")
        return
    client.error("You have not registered from discord server yet.")
