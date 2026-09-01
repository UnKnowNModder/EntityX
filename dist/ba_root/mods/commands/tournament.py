"""tournament-related commands."""

from server.clients import Client
from tournament import tournament
from tournament.manager import manager
from tournament.registration import Registration

from . import on_command


@on_command(name="/ready")
def ready(client: Client):
    """marks the player as ready and starts the match if everyone is ready."""
    season_id = tournament.active_season
    if not int(season_id):
        client.error("There is no tournament ongoing.")
        return
    response = manager.handle_player_ready(account_id=client.account_id)
    if response["status"] == "success":
        client.success(response["message"])
        if response.get("start", False):
            from server.utils import success

            success(
                message=f"Tournament match between {manager.active_match['team_names'][0]} and {manager.active_match['team_names'][1]} is starting in 2 seconds."
            )
        return
    if response["status"] == "error":
        client.error(response["message"])


@on_command(name="/verify", usage="/verify <code>")
def verify(client: Client, args: list[str]):
    """verifies the player in their team."""
    season_id = tournament.active_season
    if not int(season_id):
        client.error("There is no tournament ongoing.")
        return
    registration = Registration(season_id=season_id)
    if registration.is_registered(client.account_id):
        client.error("You are already registered.")
        return

    code = args[0]
    status = registration.verify(
        code, client.account_id, device_uuid=client.public_uuid
    )
    if status:
        client.success("You have been successfully verified.")
        return
    if status is None:
        client.error("The code is invalid.")
        return
    client.error("You have not registered from discord server yet.")
