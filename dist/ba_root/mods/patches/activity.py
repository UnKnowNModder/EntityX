from . import patch_method
from bascenev1._activity import Activity
from utilities.endvote import EndVote
from time import monotonic


@patch_method(Activity, "end", initial=True)
def end(*args, **kwargs):
    # if there is an end vote ongoing, just close it.
    EndVote.end()


@patch_method(Activity, "on_begin", initial=True)
def on_begin(*args, **kwargs):
    # don't allow player's to start endvote if the game just started, for that. log the time.
    EndVote.relaxation = monotonic() + 60  # don't allow for initial 60 seconds
