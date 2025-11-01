"""Volume control widget for bottom sheet."""

from typing import Optional, Callable
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import BooleanProperty, NumericProperty
from kivy.lang import Builder

# Load the KV file
Builder.load_file("src/spotigui/widgets/volume_sheet.kv")


class VolumeControlWidget(MDBoxLayout):
    """Volume control widget content."""

    volume_level = NumericProperty(50)
    is_muted = BooleanProperty(False)

    def __init__(
        self,
        on_volume_change: Optional[Callable] = None,
        on_mute_toggle: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize volume control widget.

        Args:
            on_volume_change: Callback when volume changes
            on_mute_toggle: Callback when mute is toggled
        """
        super().__init__(**kwargs)

        self.on_volume_change_callback = on_volume_change
        self.on_mute_toggle_callback = on_mute_toggle

    def _on_volume_change(self, _slider, value):
        """Handle volume slider change."""
        self.volume_level = int(value)
        self.is_muted = False
        if self.on_volume_change_callback:
            self.on_volume_change_callback(int(value))

    def _on_mute_toggle(self, _instance):
        """Handle mute button press."""
        self.is_muted = not self.is_muted
        if self.on_mute_toggle_callback:
            self.on_mute_toggle_callback(self.is_muted)

    def set_volume(self, volume: int):
        """Update the volume level."""
        self.volume_level = volume

    def set_muted(self, is_muted: bool):
        """Update the muted state."""
        self.is_muted = is_muted
