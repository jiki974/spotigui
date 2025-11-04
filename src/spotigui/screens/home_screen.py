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
        on_navigate_to_now_playing: Optional[Callable] = None,
        on_device_select: Optional[Callable] = None,
        on_device_refresh: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize home screen.

        Args:
            on_playlist_select: Callback when playlist is selected
            on_navigate_to_now_playing: Callback to navigate to now playing screen
            on_device_select: Callback when device is selected
            on_device_refresh: Callback to refresh device list
        """
        super().__init__(**kwargs)

        self.on_playlist_select_callback = on_playlist_select
        self.on_navigate_to_now_playing_callback = on_navigate_to_now_playing
        self.on_device_select_callback = on_device_select
        self.on_device_refresh_callback = on_device_refresh

    def on_kv_post(self, base_widget):
        """Called after the KV file has been applied."""
        super().on_kv_post(base_widget)

        # Set up top bar callbacks
        self.ids.top_bar.on_back_callback = self._on_navigate_to_now_playing
        self.ids.top_bar.on_device_select_callback = self._on_device_select
        self.ids.top_bar.on_device_refresh_callback = self._on_device_refresh

    def _on_navigate_to_now_playing(self):
        """Handle navigation to now playing screen."""
        if self.on_navigate_to_now_playing_callback:
            self.on_navigate_to_now_playing_callback()

    def _on_device_select(self, device_id: str):
        """Handle device selection."""
        if self.on_device_select_callback:
            self.on_device_select_callback(device_id)

    def _on_device_refresh(self):
        """Handle device refresh request."""
        if self.on_device_refresh_callback:
            return self.on_device_refresh_callback()
        return []

    def add_playlists(self, playlists: List[Dict[str, Any]]):
        """
        Add playlists to the list.

        Args:
            playlists: List of playlist dictionaries from Spotify API
        """

        if 'playlists_list' not in self.ids:
            Logger.error("HomeScreen.add_playlists: playlists_list not found in ids!")
            return

        self.ids.playlists_list.clear_widgets()

        for playlist in playlists:
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
