"""Initialization screen with loading indicator."""

from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/screens/init_screen.kv")


class InitScreen(MDScreen):
    """Initial screen displayed while checking authentication status."""

    def __init__(self, **kwargs):
        """Initialize init screen."""
        super().__init__(**kwargs)
