"""Playlist tile widget for displaying playlists in grid."""

from typing import Optional, Callable
from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty, DictProperty, StringProperty
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/widgets/playlist_tile.kv")


class PlaylistTile(MDCard):
    """A tile widget representing a single Spotify playlist."""

    playlist_data = DictProperty({})
    on_playlist_select = ObjectProperty(None)

    # Properties for KV bindings
    image_url = StringProperty("")
    playlist_name = StringProperty("Unknown Playlist")
    track_count_text = StringProperty("")

    def __init__(self, playlist_data: dict, on_select: Optional[Callable] = None, **kwargs):
        """
        Initialize playlist tile.

        Args:
            playlist_data: Dictionary containing playlist information (name, images, etc.)
            on_select: Callback function when tile is tapped
        """
        super().__init__(**kwargs)
        self.playlist_data = playlist_data
        self.on_playlist_select = on_select
        self._update_properties()

    def _update_properties(self):
        """Update properties from playlist data for KV bindings."""
        # Extract image URL
        images = self.playlist_data.get("images", [])
        if images and len(images) > 0:
            # Try to get the URL, handling both dict and direct URL cases
            self.image_url = images[0] if isinstance(images[0], str) else images[0].get("url", "")
        else:
            self.image_url = ""

        # Extract playlist name
        self.playlist_name = self.playlist_data.get("name", "Unknown Playlist")

        # Extract track count
        track_count = self.playlist_data.get("tracks", {}).get("total", 0)
        self.track_count_text = f"{track_count} tracks" if track_count else ""

    def on_press(self, press):
        return super(PlaylistTile, self).on_press(press)

    def on_touch_down(self, touch):
        """Handle touch down event with proper collision detection."""
        if self.collide_point(*touch.pos):
            # Grab the touch for this widget
            touch.grab(self)
            return True
        return super(PlaylistTile, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        """Handle touch up event to trigger playlist selection."""
        # Check if this touch was grabbed by this widget
        if touch.grab_current is self:
            # Release the touch
            touch.ungrab(self)
            # Trigger the selection callback
            if self.on_playlist_select:
                self.on_playlist_select(self.playlist_data)
            return True
        return super(PlaylistTile, self).on_touch_up(touch)
