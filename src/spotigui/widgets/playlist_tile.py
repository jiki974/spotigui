"""Playlist tile widget for displaying playlists in grid."""

from typing import Optional, Callable
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
from kivy.properties import  ObjectProperty, DictProperty


class PlaylistTile(MDCard):
    """A tile widget representing a single Spotify playlist."""

    playlist_data = DictProperty({})
    on_playlist_select = ObjectProperty(None)

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
        self.orientation = "vertical"
        self.padding = "10dp"
        self.spacing = "10dp"
        self.size_hint = (1, 1)
        self.elevation = 2
        self.radius = "10dp"

        # Create layout for tile content
        content_layout = MDBoxLayout(orientation="vertical", spacing="5dp")

        # Add playlist cover image if available
        images = playlist_data.get("images", [])
        if images and len(images) > 0:
            image_url = images[0].get("url", "")
            if image_url:
                image = AsyncImage(
                    source=image_url,
                    size_hint=(1, None),
                    height="200dp",
                    width="200dp",
                )
                content_layout.add_widget(image)
            else:
                # Placeholder if no image URL
                placeholder = MDLabel(
                    text="♫",
                    size_hint=(1, None),
                    height="120dp",
                    halign="center",
                    valign="center",
                    font_size="48sp",
                )
                content_layout.add_widget(placeholder)
        else:
            # Placeholder if no images
            placeholder = MDLabel(
                text="♫",
                size_hint=(1, None),
                height="120dp",
                halign="center",
                valign="center",
                font_size="48sp",
            )
            content_layout.add_widget(placeholder)

        # Add playlist name
        playlist_name = playlist_data.get("name", "Unknown Playlist")
        name_label = MDLabel(
            text=playlist_name,
            size_hint_y=0.2,
            bold=True,
            halign="center",
        )
        content_layout.add_widget(name_label)

        # Add playlist description or track count if available
        track_count = playlist_data.get("tracks", {}).get("total", 0)
        if track_count:
            info_text = f"{track_count} tracks"
            info_label = MDLabel(
                text=info_text,
                size_hint_y=0.1,
                halign="center",
                font_size="10sp",
            )
            content_layout.add_widget(info_label)

        self.add_widget(content_layout)

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
