"""utilities loader plugin."""

import importlib
from pathlib import Path


def load():
    """automatically imports utility files in the directory."""
    package_dir = Path(__file__).parent
    for file in package_dir.glob("*.py"):
        module_name = f"{__package__}.{file.stem}"
        try:
            importlib.import_module(module_name)
        except ImportError:
            print(f"⚠️ Failed to load utility file {file.stem}")
