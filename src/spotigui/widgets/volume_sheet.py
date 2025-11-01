"""Volume control widget for bottom sheet."""

from typing import Optional, Callable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.label import MDLabel
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import BooleanProperty, NumericProperty


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
        self.orientation = "vertical"
        self.spacing = "20dp"
        self.padding = "20dp"
        self.size_hint_y = None
        self.height = "200dp"

        self.on_volume_change_callback = on_volume_change
        self.on_mute_toggle_callback = on_mute_toggle

        # Title
        title = MDLabel(
            text="Volume",
            size_hint_y=None,
            height="40dp",
            halign="center",
            font_size="20sp",
            bold=True
        )
        self.add_widget(title)

        # Volume controls container
        volume_controls = MDBoxLayout(
            orientation="horizontal",
            spacing="15dp",
            size_hint_y=None,
            height="60dp"
        )

        # Mute button container
        mute_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_x=None,
            width="60dp"
        )
        self.mute_btn = MDIconButton(
            icon="volume-high",
            font_size="32sp",
            size_hint=(None, None),
            size=("48dp", "48dp")
        )
        self.mute_btn.bind(on_press=self._on_mute_toggle)
        mute_container.add_widget(self.mute_btn)
        volume_controls.add_widget(mute_container)

        # Volume slider
        self.volume_slider = MDSlider(
            min=0,
            max=100,
            value=self.volume_level,
            size_hint_x=1
        )
        self.volume_slider.bind(value=self._on_volume_change)
        volume_controls.add_widget(self.volume_slider)

        # Volume percentage label
        self.volume_label = MDLabel(
            text=f"{int(self.volume_level)}%",
            size_hint_x=None,
            width="50dp",
            halign="center",
            font_size="16sp"
        )
        volume_controls.add_widget(self.volume_label)

        self.add_widget(volume_controls)

    def _on_volume_change(self, _slider, value):
        """Handle volume slider change."""
        self.volume_level = int(value)
        self.volume_label.text = f"{int(value)}%"
        self.is_muted = False
        self.mute_btn.icon = "volume-high"
        if self.on_volume_change_callback:
            self.on_volume_change_callback(int(value))

    def _on_mute_toggle(self, _instance):
        """Handle mute button press."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_btn.icon = "volume-mute"
            if self.on_mute_toggle_callback:
                self.on_mute_toggle_callback(True)
        else:
            self.mute_btn.icon = "volume-high"
            if self.on_mute_toggle_callback:
                self.on_mute_toggle_callback(False)

    def set_volume(self, volume: int):
        """Update the volume level."""
        self.volume_level = volume
        self.volume_slider.value = volume
        self.volume_label.text = f"{volume}%"

    def set_muted(self, is_muted: bool):
        """Update the muted state."""
        self.is_muted = is_muted
        self.mute_btn.icon = "volume-mute" if is_muted else "volume-high"
