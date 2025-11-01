"""Home screen showing playlists."""

from typing import Optional, Callable, List, Dict, Any
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel

from spotigui.widgets.playlist_tile import PlaylistTile


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
        self.name = "home"
   
        self.on_playlist_select_callback = on_playlist_select

        # Create main layout with white background
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding="10dp",
            md_bg_color=(1, 1, 1, 1)
        )

        # Title section
        title_label = MDLabel(
             text="Your Playlists",
             size_hint_y=None,
             height="60dp",
             halign="left"
         )
        main_layout.add_widget(title_label)

        # Playlists section (scrollable list with card spacing)
        scroll_view = MDScrollView(size_hint=(1, 1))
        self.playlists_list = MDBoxLayout(
            orientation="vertical",
            spacing="15dp",
            size_hint_y=None,
            padding="10dp",
        )
        self.playlists_list.bind(minimum_height=self.playlists_list.setter("height"))

        scroll_view.add_widget(self.playlists_list)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def add_playlists(self, playlists: List[Dict[str, Any]]):
        """
        Add playlists to the list.

        Args:
            playlists: List of playlist dictionaries from Spotify API
        """
        self.playlists_list.clear_widgets()

        for playlist in playlists:
            tile = PlaylistTile(
                playlist_data=playlist,
                on_select=self._on_playlist_select,
                size_hint_y=None,
                height="100dp"
            )
            self.playlists_list.add_widget(tile)

    def show_loading(self):
        """Show loading indicator while fetching playlists."""
        self.playlists_list.clear_widgets()
        loading_label = MDLabel(
            text="Loading playlists...",
            size_hint_y=None,
            height="50dp",
            halign="center",
        )
        self.playlists_list.add_widget(loading_label)

    def _on_playlist_select(self, playlist_data: Dict[str, Any]):
        """Handle playlist selection."""
        if self.on_playlist_select_callback:
            self.on_playlist_select_callback(playlist_data)
