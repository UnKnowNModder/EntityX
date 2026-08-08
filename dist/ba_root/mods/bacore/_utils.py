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

def replace_method(module, func_name: str, initial: bool = False):
    """ Decorator to replace a function in a module/class by name."""
    if not hasattr(module, func_name):
        raise AttributeError(f"Module '{module.__name__}' has no attribute '{func_name}'")
    original_func = getattr(module, func_name)
    
    if not callable(original_func):
        raise TypeError(f"Attribute '{func_name}' in '{module.__name__}' is not callable")

    def decorator(new_func):
        sign = signature(new_func)
        has_og_result = "og_result" in sign.parameters

        @wraps(original_func)
        def wrapper(*args, **kwargs) -> Any:
            if initial:
                # if this is true, we'll call the original function initially.
                result = original_func(*args, **kwargs)
                if has_og_result:
                    return new_func(*args, **kwargs, og_result=result)
            return new_func(*args, **kwargs)

        # incase we need the original function
        wrapper._original = original_func

        # patch it into the module
        setattr(module, func_name, wrapper)

        return wrapper  # just to be safe.
    return decorator

