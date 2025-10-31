"""Playback controls widget for play, pause, next, previous, volume control."""

from typing import Optional, Callable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.slider import MDSlider
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import BooleanProperty, NumericProperty


class PlaybackControlsWidget(MDBoxLayout):
    """Widget containing playback controls and volume slider."""

    is_playing = BooleanProperty(False)
    volume_level = NumericProperty(50)
    is_muted = BooleanProperty(False)

    def __init__(
        self,
        on_play: Optional[Callable] = None,
        on_pause: Optional[Callable] = None,
        on_next: Optional[Callable] = None,
        on_previous: Optional[Callable] = None,
        on_volume_change: Optional[Callable] = None,
        on_mute_toggle: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize playback controls.

        Args:
            on_play: Callback when play is pressed
            on_pause: Callback when pause is pressed
            on_next: Callback when next is pressed
            on_previous: Callback when previous is pressed
            on_volume_change: Callback when volume changes
            on_mute_toggle: Callback when mute is toggled
        """
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "10dp"
        self.padding = "10dp"
        self.size_hint_y = None
        self.height = "64dp"

        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_next_callback = on_next
        self.on_previous_callback = on_previous
        self.on_volume_change_callback = on_volume_change
        self.on_mute_toggle_callback = on_mute_toggle

        # Main control buttons layout
        buttons_layout = MDBoxLayout(
            orientation = "horizontal",
            spacing="5dp",
            size_hint_y=0.3,
        )

        # Previous button container
        prev_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_x=0.2
        )
        self.prev_btn = MDIconButton(
            icon="skip-previous",
            font_size="48sp",
            size_hint=(None, None),
            size=("48dp", "48dp")
        )
        self.prev_btn.bind(on_press=self._on_previous)
        prev_container.add_widget(self.prev_btn)
        buttons_layout.add_widget(prev_container)

        # Play/Pause button container
        play_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_x=0.6
        )
        self.play_pause_btn = MDIconButton(
            icon="play",
            font_size="64sp",
            size_hint=(None, None),
            size=("64dp", "64dp")
        )
        self.play_pause_btn.bind(on_press=self._on_play_pause)
        play_container.add_widget(self.play_pause_btn)
        buttons_layout.add_widget(play_container)

        # Next button container
        next_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_x=0.2
        )
        self.next_btn = MDIconButton(
            icon="skip-next",
            font_size="48sp",
            size_hint=(None, None),
            size=("48dp", "48dp")
        )
        self.next_btn.bind(on_press=self._on_next)
        next_container.add_widget(self.next_btn)
        buttons_layout.add_widget(next_container)

        self.add_widget(buttons_layout)

        # Volume control layout
        volume_layout = MDBoxLayout(size_hint_y=0.15)

        # Mute button container
        mute_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_x=0.15
        )
        self.mute_btn = MDIconButton(
            icon="volume-high",
            font_size="24sp",
            size_hint=(None, None),
            size=("48dp", "48dp")
        )
        self.mute_btn.bind(on_press=self._on_mute_toggle)
        mute_container.add_widget(self.mute_btn)
        volume_layout.add_widget(mute_container)

        # Volume slider
        self.volume_slider = MDSlider(
            min=0,
            max=100,
            value=self.volume_level,
        )
        self.volume_slider.bind(value=self._on_volume_change)
        volume_layout.add_widget(self.volume_slider)

        #self.add_widget(volume_layout)

    def _on_play_pause(self, _instance):
        """Handle play/pause button press."""
        if self.is_playing:
            if self.on_pause_callback:
                self.on_pause_callback()
            self.is_playing = False
            self.play_pause_btn.icon = "play"
        else:
            if self.on_play_callback:
                self.on_play_callback()
            self.is_playing = True
            self.play_pause_btn.icon = "pause"

    def _on_next(self, _instance):
        """Handle next button press."""
        if self.on_next_callback:
            self.on_next_callback()

    def _on_previous(self, _instance):
        """Handle previous button press."""
        if self.on_previous_callback:
            self.on_previous_callback()

    def _on_volume_change(self, _slider, value):
        """Handle volume slider change."""
        self.volume_level = int(value)
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

    def set_playing_state(self, is_playing: bool):
        """Update the playing state UI."""
        self.is_playing = is_playing
        self.play_pause_btn.icon = "pause" if is_playing else "play"
