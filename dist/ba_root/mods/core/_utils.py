"""basic helper utility."""

from __future__ import annotations
from functools import wraps
from inspect import signature
from typing import Any
import bascenev1

def error(message: str, clients: list[int] | None = None) -> None:
	"""shows an error screenmessage."""
	bascenev1.broadcastmessage(message, color=(1, 0, 0), transient=True, clients=clients)


def success(message: str, clients: list[int] | None = None) -> None:
	"""shows a success screenmessage."""
	bascenev1.broadcastmessage(message, color=(0, 0.5, 1), transient=True, clients=clients)


def send(
	message: str, clients: list[int] | None = None, sender: str | None = None
) -> None:
	"""sends a chatmessage."""
	if message.startswith("/"):
		# cover up for server authority exploitation.
		return
	bascenev1.chatmessage(message, clients=clients, sender_override=sender)
