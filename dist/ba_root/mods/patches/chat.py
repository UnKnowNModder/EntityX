import bascenev1

from commands import control_message
from utilities.endvote import EndVote
from . import patch_method


@patch_method(bascenev1._hooks, "filter_chat_message")
def filter_chat_message(msg: str, client_id: int) -> str | None:
    """custom patch for chat messages."""
    EndVote.handle_vote(msg, client_id)
    return control_message(msg, client_id)
