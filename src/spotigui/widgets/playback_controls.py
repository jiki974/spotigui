"""Playback controls widget for play, pause, next, previous, volume control."""

from typing import Optional, Callable
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import BooleanProperty
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/widgets/playback_controls.kv")


class PlaybackControlsWidget(MDBoxLayout):
    """Widget containing playback controls."""

    is_playing = BooleanProperty(False)

    def __init__(
        self,
        on_play: Optional[Callable] = None,
        on_pause: Optional[Callable] = None,
        on_next: Optional[Callable] = None,
        on_previous: Optional[Callable] = None,
        on_volume_click: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize playback controls.

        Args:
            on_play: Callback when play is pressed
            on_pause: Callback when pause is pressed
            on_next: Callback when next is pressed
            on_previous: Callback when previous is pressed
            on_volume_click: Callback when volume button is pressed
        """
        super().__init__(**kwargs)

        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_next_callback = on_next
        self.on_previous_callback = on_previous
        self.on_volume_click_callback = on_volume_click

    def _on_play_pause(self, _instance):
        """Handle play/pause button press."""
        if self.is_playing:
            if self.on_pause_callback:
                self.on_pause_callback()
            self.is_playing = False
        else:
            if self.on_play_callback:
                self.on_play_callback()
            self.is_playing = True

    def _on_next(self, _instance):
        """Handle next button press."""
        if self.on_next_callback:
            self.on_next_callback()

    def _on_previous(self, _instance):
        """Handle previous button press."""
        if self.on_previous_callback:
            self.on_previous_callback()

    def _on_volume_click(self, _instance):
        """Handle volume button press."""
        if self.on_volume_click_callback:
            self.on_volume_click_callback()

    def set_playing_state(self, is_playing: bool):
        """Update the playing state UI."""
        self.is_playing = is_playing
