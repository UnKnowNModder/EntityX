import bascenev1

from server.clients import Client, fetch_client

from . import patch_method


@patch_method(bascenev1._session.Session, "on_player_request", initial=True)
def on_player_request(self, player: bascenev1.SessionPlayer, og_result) -> bool:
    client = Client(player.inputdevice.client_id, player.get_account_id())
    if not client.authenticity:
        auth_code = client.get_auth_code()
        client.error(f"Your auth code is: {auth_code}\nPlease enter in chat to verify.")
        return False
    return og_result


@patch_method(bascenev1._hooks, "on_client_joined")
def on_client_joined(client_id: int) -> None:
    client = fetch_client(client_id)
    print(
        f"{client.name} Joined the server (Addr: {client.address}, uuid: {client.public_uuid})"
    )
