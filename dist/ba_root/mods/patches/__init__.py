""" patches loader plugin"""
import importlib
from pathlib import Path
from functools import wraps
from inspect import signature
from typing import Any

def patch_method(module, func_name: str, initial: bool = False):
    """ Decorator to patch a function in a module/class by name."""
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

def load():
    """automatically imports patch files in the directory."""
    package_dir = Path(__file__).parent
    for file in package_dir.glob("*.py"):
        module_name = f"{__package__}.{file.stem}"
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"⚠️ Failed to load patch file {file.stem}")


