import json
import os
import shutil
import socket
import subprocess
import threading
from pathlib import Path

import babase

from commands import command_line
from server import config
from server.clients import Client, all_clients
from server.utils import send


class SocketTunnel(threading.Thread):
    """a socket tunnel to communicate and receive commands from discord bot without interrupting the main game thread and process."""

    def __init__(self, port: int):
        super().__init__(daemon=True)
        self.port = port
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.port))

    def run(self) -> None:
        # this runs in a loop, but runs only when there socket receives bytes.
        while self.running:
            try:
                raw_bytes, addr = self.sock.recvfrom(4096)
                if not self.running:
                    break

                data = json.loads(raw_bytes.decode("utf-8"))
                # push safely into the game thread.
                babase.pushcall(
                    lambda: self._handle_data(data, self.sock, addr),
                    from_other_thread=True,
                )
            except OSError:
                break

    def _handle_data(self, data: dict, sock: socket.socket, addr: tuple) -> None:
        """handles and processes the received data."""
        action = data["action"]
        if action == "message":
            send(data["text"], sender=data["sender"])

        elif action == "command":
            account_id = data["account_id"]
            command = data["command"]
            client = Client(account_id=account_id)
            command_line(msg=command, client=client)

        elif action == "list":
            response = {"players": []}
            for client in all_clients():
                response["players"].append(
                    {
                        "name": client.display_string,
                        "client_id": client.client_id,
                    }
                )
            sock.sendto(json.dumps(response).encode("utf-8"), addr)

    def shutdown(self) -> None:
        """shuts down the thread gracefully."""
        if not self.running:
            return
        self.running = False
        # send a dummy byte to wake up our socket connection to bring it out of the while loop
        wake_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        wake_sock.sendto(b"{}", ("127.0.0.1", self.port))
        wake_sock.close()
        self.sock.close()

        if threading.current_thread() != self:
            # run and cleanly terminate.
            self.join(timeout=1.0)


async def shutdown(self) -> None:
    """shuts down the process and socket thread."""
    print("shutting down discord bot")
    # terminate the process
    if hasattr(self, "process") and self.process and self.process.poll() is None:
        try:
            self.process.terminate()
            self.process.wait(timeout=2.0)
        except:
            self.process.kill()
        self.process = None

    # shutdown the socket thread
    if self.socket:
        self.socket.shutdown()
        self.socket = None


def launch(self) -> None:
    """launches the bot."""
    # uv is a prerequisite.
    uv_path = shutil.which("uv")
    if not uv_path:
        # uv does not exist.. we need to install it.
        print("Error: uv is not installed\n Installing it now...")
        cmd = ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"]
        subprocess.run(cmd, check=True, capture_output=True)
        print("Success: downloaded uv successfullly")
        uv_path = shutil.which("uv")

    # run the bot script using uv
    script_path = str(Path(__file__).resolve().parent / "bot.py")
    cmd = [
        uv_path,
        "run",
        "--python",
        "python3.13",
        "--with",
        "discord.py",
        "-B",
        script_path,
    ]

    # we need to pass env for the file to be able to import from sister folders.
    MODS_DIR = str(Path(__file__).resolve().parent.parent)
    env = os.environ.copy()
    env["PYTHONPATH"] = MODS_DIR
    print("Starting discord bot.")
    self.process = subprocess.Popen(cmd, env=env)


def load(self) -> None:
    """sets up server socket and executes the bot."""
    # firstly, check for a valid discord bot token.
    if config.discord.token == "ENTER-YOUR-BOT-TOKEN-HERE":
        print("Error: Put a valid bot token.")
        return

    # execute the bot in a thread (incase uv is not installed.)
    threading.Thread(target=launch, args=(self,), daemon=True).start()

    # start the socket
    port = config.discord.port
    self.socket = SocketTunnel(port)
    self.socket.start()

    # add to shutdown task
    babase.app.add_shutdown_task(shutdown(self))
