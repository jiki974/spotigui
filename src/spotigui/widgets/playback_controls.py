"""Playback controls widget for play, pause, next, previous, volume control."""

from typing import Optional, Callable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import BooleanProperty


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
        self.orientation = "vertical"
        self.spacing = "10dp"
        self.padding = "10dp"
        self.size_hint_y = None
        self.height = "100dp"

        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_next_callback = on_next
        self.on_previous_callback = on_previous
        self.on_volume_click_callback = on_volume_click

        # Main control buttons layout
        buttons_layout = MDBoxLayout(
            orientation = "horizontal",
            spacing="5dp",
            size_hint_y=1,
        )

        # Volume button container
        volume_container = AnchorLayout(
            anchor_x="center",
            anchor_y="center",
            size_hint_x=0.2
        )
        self.volume_btn = MDIconButton(
            icon="volume-high",
            font_size="32sp",
            size_hint=(None, None),
            size=("48dp", "48dp")
        )
        self.volume_btn.bind(on_press=self._on_volume_click)
        volume_container.add_widget(self.volume_btn)
        #buttons_layout.add_widget(volume_container)

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

    def _on_volume_click(self, _instance):
        """Handle volume button press."""
        if self.on_volume_click_callback:
            self.on_volume_click_callback()

    def set_playing_state(self, is_playing: bool):
        """Update the playing state UI."""
        self.is_playing = is_playing
        self.play_pause_btn.icon = "pause" if is_playing else "play"
