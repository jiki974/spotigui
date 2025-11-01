"""Playlist tile widget for displaying playlists in grid."""

from typing import Optional, Callable
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.image import AsyncImage
from kivy.properties import ObjectProperty, DictProperty
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.clock import Clock

# Load the KV file
Builder.load_file("src/spotigui/widgets/playlist_tile.kv")


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
        Logger.info(f"PlaylistTile.__init__: Received playlist data: {playlist_data.get('name', 'NO NAME')}")
        # Build content after the widget is fully initialized
        Clock.schedule_once(lambda dt: self._build_content(), 0)

    def _build_content(self):
        """Build the tile content with playlist data."""
        if not hasattr(self, 'ids') or 'content_layout' not in self.ids:
            # IDs not ready yet, try again
            Clock.schedule_once(lambda dt: self._build_content(), 0.1)
            return

        Logger.info(f"PlaylistTile._build_content: Building content for playlist: {self.playlist_data}")

        # Add playlist cover image if available
        images = self.playlist_data.get("images", [])
        Logger.info(f"PlaylistTile._build_content: Playlist '{self.playlist_data.get('name', 'Unknown')}' has {len(images)} images")

        if images and len(images) > 0:
            # Try to get the URL, handling both dict and direct URL cases
            image_url = images[0] if isinstance(images[0], str) else images[0].get("url", "")
            Logger.info(f"PlaylistTile: Image URL: {image_url[:50] if image_url else 'None'}...")

            if image_url:
                # Create a container for the image with rounded corners effect
                image_container = MDBoxLayout(
                    size_hint=(None, None),
                    size=("70dp", "70dp")
                )
                image = AsyncImage(
                    source=image_url,
                    size_hint=(None, None),
                    size=("70dp", "70dp"),
                    allow_stretch=True,
                    keep_ratio=True,
                    mipmap=True,
                    nocache=False
                )
                image_container.add_widget(image)
                self.ids.content_layout.add_widget(image_container)
            else:
                Logger.warning("PlaylistTile: No valid image URL found")
                # Placeholder if no image URL with background
                placeholder_container = MDBoxLayout(
                    size_hint=(None, None),
                    size=("70dp", "70dp"),
                    md_bg_color=(0.95, 0.95, 0.95, 1)
                )
                placeholder = MDLabel(
                    text="♫",
                    halign="center",
                    valign="center",
                    font_size="36sp",
                )
                placeholder_container.add_widget(placeholder)
                self.ids.content_layout.add_widget(placeholder_container)
        else:
            Logger.info("PlaylistTile: No images array found")
            # Placeholder if no images with background
            placeholder_container = MDBoxLayout(
                size_hint=(None, None),
                size=("70dp", "70dp"),
                md_bg_color=(0.95, 0.95, 0.95, 1)
            )
            placeholder = MDLabel(
                text="♫",
                halign="center",
                valign="center",
                font_size="36sp",
            )
            placeholder_container.add_widget(placeholder)
            self.ids.content_layout.add_widget(placeholder_container)

        # Add playlist info (name and optional track count)
        info_layout = MDBoxLayout(
            orientation="vertical",
            spacing="5dp"
        )

        playlist_name = self.playlist_data.get("name", "Unknown Playlist")
        name_label = MDLabel(
            text=playlist_name,
            size_hint_y=None,
            height="30dp",
            bold=True,
            halign="left",
            valign="center",
            font_size="16sp",
        )
        info_layout.add_widget(name_label)

        # Add track count as subtitle
        track_count = self.playlist_data.get("tracks", {}).get("total", 0)
        if track_count:
            subtitle = MDLabel(
                text=f"{track_count} tracks",
                size_hint_y=None,
                height="20dp",
                halign="left",
                valign="center",
                font_size="12sp",
                theme_text_color="Secondary"
            )
            info_layout.add_widget(subtitle)

        self.ids.content_layout.add_widget(info_layout)

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
