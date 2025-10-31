"""Home screen showing playlists."""

from typing import Optional, Callable, List, Dict, Any
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
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
             halign="left",
            padding=("10dp", "10dp")
         )
        main_layout.add_widget(title_label)

        # Playlists section (scrollable grid)
        scroll_view = MDScrollView(size_hint=(1, 1))
        self.playlists_grid = MDGridLayout(
            cols=2,
            spacing="100dp",
            size_hint_y=None,
            padding="5dp",
        )
        self.playlists_grid.bind(minimum_height=self.playlists_grid.setter("height"))

        scroll_view.add_widget(self.playlists_grid)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def add_playlists(self, playlists: List[Dict[str, Any]]):
        """
        Add playlists to the grid.

        Args:
            playlists: List of playlist dictionaries from Spotify API
        """
        self.playlists_grid.clear_widgets()

        for playlist in playlists:
            tile = PlaylistTile(
                playlist_data=playlist,
                on_select=self._on_playlist_select,
                size_hint_y=None,
                height="180dp",
            )
            self.playlists_grid.add_widget(tile)

    def show_loading(self):
        """Show loading indicator while fetching playlists."""
        self.playlists_grid.clear_widgets()
        loading_layout = MDBoxLayout(orientation="vertical", padding="20dp", spacing="10dp")
        loading_label = MDLabel(
            text="Loading playlists...",
            size_hint_y=None,
            height="50dp",
            halign="center",
        )
        loading_layout.add_widget(loading_label)
        self.playlists_grid.add_widget(loading_layout)

    def _on_playlist_select(self, playlist_data: Dict[str, Any]):
        """Handle playlist selection."""
        if self.on_playlist_select_callback:
            self.on_playlist_select_callback(playlist_data)
