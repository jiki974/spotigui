"""Home screen showing playlists."""

from typing import Optional, Callable, List, Dict, Any
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.logger import Logger

from spotigui.widgets.playlist_tile import PlaylistTile

# Load the KV file
Builder.load_file("src/spotigui/screens/home_screen.kv")


class HomeScreen(MDScreen):
    """Home screen displaying user playlists."""

    def __init__(
        self,
        on_playlist_select: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize home screen.

        Args:
            on_playlist_select: Callback when playlist is selected
        """
        super().__init__(**kwargs)

        self.on_playlist_select_callback = on_playlist_select

    def add_playlists(self, playlists: List[Dict[str, Any]]):
        """
        Add playlists to the list.

        Args:
            playlists: List of playlist dictionaries from Spotify API
        """
        Logger.info(f"HomeScreen.add_playlists: Adding {len(playlists)} playlists")

        if 'playlists_list' not in self.ids:
            Logger.error("HomeScreen.add_playlists: playlists_list not found in ids!")
            return

        self.ids.playlists_list.clear_widgets()

        for playlist in playlists:
            Logger.info(f"HomeScreen.add_playlists: Creating tile for playlist '{playlist.get('name', 'NO NAME')}'")
            tile = PlaylistTile(
                playlist_data=playlist,
                on_select=self._on_playlist_select,
                size_hint_y=None,
                height="100dp"
            )
            self.ids.playlists_list.add_widget(tile)

    def show_loading(self):
        """Show loading indicator while fetching playlists."""
        self.ids.playlists_list.clear_widgets()
        loading_label = MDLabel(
            text="Loading playlists...",
            size_hint_y=None,
            height="50dp",
            halign="center",
        )
        self.ids.playlists_list.add_widget(loading_label)

    def _on_playlist_select(self, playlist_data: Dict[str, Any]):
        """Handle playlist selection."""
        if self.on_playlist_select_callback:
            self.on_playlist_select_callback(playlist_data)
