import logging

import bascenev1

from server.clients import Client, fetch_client
from server.storage import MODS_DIR
from tournament import tournament

from . import patch_method

logging.basicConfig(
    filename=MODS_DIR / "server.log",
    filemode="a",
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


@patch_method(bascenev1._session.Session, "on_player_request", initial=True)
def on_player_request(self, player: bascenev1.SessionPlayer, og_result) -> bool:
    client = Client(player.inputdevice.client_id, player.get_account_id())
    if not client.authenticity:
        auth_code = client.get_auth_code()
        client.error(f"Your auth code is: {auth_code}\nPlease enter in chat to verify.")
        return False
    return og_result


@patch_method(bascenev1.DualTeamSession, "on_player_leave", initial=True)
def on_player_leave(self, player: bascenev1.SessionPlayer) -> None:
    identifier = self._player_requested_identifiers.get(player.id)
    if identifier and int(tournament.active_season):
        from tournament.manager import manager

        manager.handle_player_leave(identifier)


@patch_method(bascenev1._hooks, "on_client_joined")
def on_client_joined(client_id: int) -> None:
    client = fetch_client(client_id)
    message = f"{client.name} Joined the server (Addr: {client.address}, uuid: {client.public_uuid})"
    logging.info(message)
