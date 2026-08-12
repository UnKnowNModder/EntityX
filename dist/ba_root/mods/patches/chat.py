import bascenev1
from . import patch_method
from commands import control_message

@patch_method(bascenev1._hooks, "filter_chat_message")
def filter_chat_message(msg: str, client_id: int) -> str | None:
    """ custom patch for chat messages. """
    return control_message(msg, client_id)