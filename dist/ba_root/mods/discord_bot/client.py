"""game client for talking to game tunnel"""

import asyncio
import json
import socket

from server import config


class GameClient:
    """client for sending json payloads to our server's socket tunnel."""

    def __init__(self, host: str = "127.0.0.1"):
        self.host = host
        self.port = config.discord.port

    def send_action(self, action: str, response: bool = False, **kwags) -> dict | None:
        """sends action to tunnel"""
        payload = json.dumps({"action": action, **kwags}).encode("utf-8")
        # run in background loop
        return asyncio.get_running_loop().run_in_executor(
            None, self.send, payload, response
        )

    def send(self, payload: bytes, response: bool) -> dict | None:
        """sends payload"""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.sendto(payload, (self.host, self.port))

                # check if we need response.
                if not response:
                    return

                sock.settimeout(2.0)
                data, _ = sock.recvfrom(4096)
                # return the dict.
                return json.loads(data.decode("utf-8"))

            except Exception as e:
                print(f"Error while sending payload to socket tunnel: {e}")
