"""
spotigui - A multiplatform Spotify client to control any Spotify devices
"""

import sys
from pathlib import Path

__version__ = "0.1.0"
__author__ = "Jacky Hoareau"


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    In development, KV files are at src/spotigui/...
    In PyInstaller bundle, KV files are in the temporary extraction folder.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        # Remove 'src/spotigui/' prefix if present since files are at root in bundle
        if relative_path.startswith('src/spotigui/'):
            relative_path = relative_path.replace('src/spotigui/', '')
    except AttributeError:
        # Running in normal Python environment
        base_path = Path(__file__).parent.parent.parent

    return str(Path(base_path) / relative_path)
