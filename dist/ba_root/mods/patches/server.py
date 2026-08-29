import os

from baclassic._servermode import ServerController

from . import patch_method


@patch_method(ServerController, "handle_transition")
def handle_transition(self) -> bool:
    """patched method to stop the server from restarting in between a match."""
    if os.getenv("BA_SERVER_RESTART") == "0":
        return False
    return handle_transition.original(self)
