"""Playback controls bottom sheet widget."""

from typing import Optional, Callable
from kivymd.uix.bottomsheet import MDBottomSheet
from kivy.properties import BooleanProperty
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/widgets/playback_controls.kv")


class PlaybackControlsSheet(MDBottomSheet):
    """Bottom sheet containing playback controls."""

    is_playing = BooleanProperty(False)
    is_muted = BooleanProperty(False)

    def __init__(
        self,
        on_play: Optional[Callable] = None,
        on_pause: Optional[Callable] = None,
        on_next: Optional[Callable] = None,
        on_previous: Optional[Callable] = None,
        on_mute_toggle: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize playback controls sheet.

        Args:
            on_play: Callback when play is pressed
            on_pause: Callback when pause is pressed
            on_next: Callback when next is pressed
            on_previous: Callback when previous is pressed
            on_mute_toggle: Callback when mute is toggled
        """
        super().__init__(**kwargs)

        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_next_callback = on_next
        self.on_previous_callback = on_previous
        self.on_mute_toggle_callback = on_mute_toggle

    def set_playing_state(self, is_playing: bool):
        """
        Update playing state.

        Args:
            is_playing: True if track is playing, False otherwise
        """
        self.is_playing = is_playing

    def _on_play_pause(self, _instance):
        """Handle play/pause button press."""
        if self.is_playing:
            if self.on_pause_callback:
                self.on_pause_callback()
        else:
            if self.on_play_callback:
                self.on_play_callback()

    def _on_next(self, _instance=None):
        """Handle next track action."""
        if self.on_next_callback:
            self.on_next_callback()

    def _on_previous(self, _instance=None):
        """Handle previous track action."""
        if self.on_previous_callback:
            self.on_previous_callback()

    def _on_mute_toggle_click(self, _instance):
        """Handle mute/unmute button click."""
        # Toggle mute state
        new_mute_state = not self.is_muted
        self.is_muted = new_mute_state

        # Call the mute toggle callback
        if self.on_mute_toggle_callback:
            self.on_mute_toggle_callback(new_mute_state)

    def open_sheet(self):
        """Open the playback bottom sheet."""
        self.set_state("open")
