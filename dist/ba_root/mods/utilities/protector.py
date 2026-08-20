"""Protects the server from unwanted players..
though I'm not unwanted :D (hope so)
"""

from __future__ import annotations

import babase
import bascenev1

from roles import roles
from server import config
from server.clients import Client, all_clients
from server.enums import Role


class Protector:
    """somewhat fishy name.."""

    def __init__(self):
        self.afk_time = 20  # seconds, + 10 will be added in code.
        self.lobby = {}
        # delay to get a valid session..
        self.runner_loop_timer = bascenev1.AppTimer(3, self.check_context)

    def check_context(self):
        session = bascenev1.get_foreground_host_session()
        if session:
            with session.context:
                self.runner_loop_timer = bascenev1.timer(
                    1, babase.CallStrict(self.runner_loop), repeat=True
                )

    def runner_loop(self):
        """this is the runner loop that protects everything.."""
        clients = all_clients()
        for client in clients:
            if client.authority:
                # no checks against authority.
                continue

            # blacklist
            if roles.has_role(Role.BANLIST, client.account_id):
                # direct kick em, no message.
                client.kick()
                continue
            # whitelist
            if config.whitelist:
                client.error(f"{client.name}, you are not in whitelist..")
                client.kick()
        if not config.spectator:
            self.handle_lobby_afk(clients)

    def handle_lobby_afk(self, clients: list[Client]):
        """handles afk lobby players.."""
        for client in clients:
            # lobby afk
            client_id = client.client_id
            if client.in_lobby and client_id not in self.lobby:
                self.lobby[client_id] = 10 + self.afk_time
            elif not client.in_lobby and client_id in self.lobby:
                del self.lobby[client_id]
        for client in self.lobby.copy():
            self.lobby[client] -= 1
            if self.lobby[client] == 0:
                # kick the client..
                bascenev1.broadcastmessage(
                    "Kicking you for being idle in lobby for too long",
                    color=(1, 0, 0),
                    transient=True,
                    clients=[client],
                )
                bascenev1.disconnect_client(client)
                print(f"Kicked {client} for being afk in lobby")
                del self.lobby[client]
            elif self.lobby[client] <= self.afk_time:
                # start warnings..
                bascenev1.broadcastmessage(
                    f"You have {self.lobby[client]}s left, hurry up and join the game.",
                    color=(1, 0, 0),
                    transient=True,
                    clients=[client],
                )


# call on import.
Protector()
