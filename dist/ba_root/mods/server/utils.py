"""basic helper utility."""

from __future__ import annotations
from functools import wraps
from inspect import signature
from typing import Any
import bascenev1


def error(message: str, clients: list[int] | None = None) -> None:
    """shows an error screenmessage."""
    bascenev1.broadcastmessage(
        message, color=(1, 0, 0), transient=True, clients=clients
    )


def success(message: str, clients: list[int] | None = None) -> None:
    """shows a success screenmessage."""
    bascenev1.broadcastmessage(
        message, color=(0, 0.5, 1), transient=True, clients=clients
    )


def send(
    message: str, clients: list[int] | None = None, sender: str | None = None
) -> None:
    """sends a chatmessage."""
    if message.startswith("/"):
        # cover up for server authority exploitation.
        return
    bascenev1.chatmessage(message, clients=clients, sender_override=sender)


class Text:
    """text which spawns on the node's head."""

    def __init__(self, node: bascenev1.Node, text: str) -> None:
        color = (1, 1, 1)  # default
        self.node = node
        math = bascenev1.newnode(
            "math", owner=self.node, attrs={"input1": (0, 1.38, 0), "operation": "add"}
        )
        self.node.connectattr("torso_position", math, "input2")

        self.text = bascenev1.newnode(
            "text",
            owner=self.node,
            attrs={
                "text": text,
                "in_world": True,
                "shadow": 1.1,
                "flatness": 1.0,
                "color": color,
                "scale": 0.01,
                "h_align": "center",
            },
        )
        math.connectattr("output", self.text, "position")
        # bascenev1.animate_array(self.text, "scale", {0: 0.0, 1: 0.01})
