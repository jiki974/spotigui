"""Now Playing screen showing current track and playback controls."""

from typing import Optional, Callable, Dict, Any
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import AsyncImage

from spotigui.widgets.playback_controls import PlaybackControlsWidget
from spotigui.widgets.progress_bar import ProgressBarWidget
from spotigui.widgets.topbar import TopBarWidget


class NowPlayingScreen(MDScreen):
    """Now Playing screen displaying current track and playback controls."""

    def __init__(
        self,
        on_play: Optional[Callable] = None,
        on_pause: Optional[Callable] = None,
        on_next: Optional[Callable] = None,
        on_previous: Optional[Callable] = None,
        on_volume_change: Optional[Callable] = None,
        on_mute_toggle: Optional[Callable] = None,
        on_device_select: Optional[Callable] = None,
        on_device_refresh: Optional[Callable] = None,
        on_back_to_playlists: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize now playing screen.

        Args:
            on_play: Callback when play is pressed
            on_pause: Callback when pause is pressed
            on_next: Callback when next is pressed
            on_previous: Callback when previous is pressed
            on_volume_change: Callback when volume changes
            on_mute_toggle: Callback when mute is toggled
            on_device_select: Callback when device is selected
            on_device_refresh: Callback to refresh device list
            on_back_to_playlists: Callback to navigate back to playlists
        """
        super().__init__(**kwargs)
        self.name = "now_playing"
        self.md_bg_color = (1, 1, 1, 1)  # White background

        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_next_callback = on_next
        self.on_previous_callback = on_previous
        self.on_volume_change_callback = on_volume_change
        self.on_mute_toggle_callback = on_mute_toggle
        self.on_device_select_callback = on_device_select
        self.on_device_refresh_callback = on_device_refresh
        self.on_back_to_playlists_callback = on_back_to_playlists

        # Store swipe tracking
        self.touch_start_pos = {}
        self.min_swipe_distance = 50

        # Create main layout
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing="5dp",
            padding="5dp",
            md_bg_color=(1, 1, 1, 1)
        )

        # Top bar with back button and device selector
        self.top_bar = TopBarWidget(
            show_back_button=True,
            show_device_button=True,
            on_back=self._on_back,
            on_device_select=self._on_device_select,
            on_device_refresh=self._on_device_refresh,
        )
        main_layout.add_widget(self.top_bar)

        # Album art section
        album_art_container = MDBoxLayout(
            height = "480dp",
        )

        self.album_art = AsyncImage(
            source="",
            size_hint=(1, 1),
            fit_mode="contain",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            allow_stretch=True,
            nocache=False,
            mipmap=True
        )
        # Bind to loading events to hide the default loading icon
        self.album_art.bind(on_load=self._on_image_load)
        album_art_container.add_widget(self.album_art)
        main_layout.add_widget(album_art_container)

        # Playback controls section
        self.playback_controls = PlaybackControlsWidget(
            on_play=self._on_play,
            on_pause=self._on_pause,
            on_next=self._on_next,
            on_previous=self._on_previous,
            on_volume_change=self._on_volume_change,
            on_mute_toggle=self._on_mute_toggle,
        )
        main_layout.add_widget(self.playback_controls)

                # Progress bar section
        self.progress_bar = ProgressBarWidget()

        main_layout.add_widget(self.progress_bar)

        self.add_widget(main_layout)

    def _on_image_load(self, instance):
        """Handle image load event."""
        # This can be used for custom loading handling if needed
        pass

    def update_track_info(self, track_data: Dict[str, Any]):
        """
        Update the displayed track information.

        Args:
            track_data: Dictionary with track info (name, artists, album, images)
        """
        if not track_data:
            self.top_bar.track_name_label.text = "No track playing"
            self.album_art.source = ""
            return

        # Update artist names
        artists = track_data.get("artists", [])
        artist_names = ", ".join([artist.get("name", "") for artist in artists])

        # Update track name
        track_name = track_data.get("name", "Unknown Track")
        self.top_bar.track_name_label.text = " - ".join([track_name, artist_names])

        # Update album info
        album = track_data.get("album", {})

        # Update album art - prefer medium size image (index 1) for better quality
        images = album.get("images", [])
        if images:
            self.album_art.source = images[0]["url"]
        else:
            self.album_art.source = ""

    def update_progress(self, current_pos_ms: int, duration_ms: int):
        """
        Update track progress display.

        Args:
            current_pos_ms: Current position in milliseconds
            duration_ms: Total duration in milliseconds
        """
        self.progress_bar.update_progress(current_pos_ms, duration_ms)

    def set_playing_state(self, is_playing: bool):
        """
        Update playing state.

        Args:
            is_playing: True if track is playing, False otherwise
        """
        self.playback_controls.set_playing_state(is_playing)

    def on_touch_down(self, touch):
        """Handle touch down for swipe detection."""
        if super(NowPlayingScreen, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos):
            self.touch_start_pos[touch.uid] = (touch.x, touch.y)
            touch.grab(self)
            return True
        return False

    def on_touch_up(self, touch):
        """Handle touch up to detect swipe gestures."""
        if touch.grab_current is self:
            start_pos = self.touch_start_pos.get(touch.uid)
            if start_pos:
                dx = touch.x - start_pos[0]
                dy = touch.y - start_pos[1]

                # Detect horizontal swipe
                if abs(dx) > self.min_swipe_distance and abs(dy) < abs(dx) / 2:
                    if dx > 0:
                        # Swipe right - next track
                        self._on_next(None)
                    elif dx < 0:
                        # Swipe left - previous track
                        self._on_previous(None)

                del self.touch_start_pos[touch.uid]

            touch.ungrab(self)
            return True

        return super(NowPlayingScreen, self).on_touch_up(touch)

    def _on_play(self, _instance=None):
        """Handle play action."""
        if self.on_play_callback:
            self.on_play_callback()

    def _on_pause(self, _instance=None):
        """Handle pause action."""
        if self.on_pause_callback:
            self.on_pause_callback()

    def _on_next(self, _instance=None):
        """Handle next track action."""
        if self.on_next_callback:
            self.on_next_callback()

    def _on_previous(self, _instance=None):
        """Handle previous track action."""
        if self.on_previous_callback:
            self.on_previous_callback()

    def _on_volume_change(self, volume: int):
        """Handle volume change."""
        if self.on_volume_change_callback:
            self.on_volume_change_callback(volume)

    def _on_mute_toggle(self, is_muted: bool):
        """Handle mute toggle."""
        if self.on_mute_toggle_callback:
            self.on_mute_toggle_callback(is_muted)

    def _on_device_select(self, device_id: str):
        """Handle device selection."""
        if self.on_device_select_callback:
            self.on_device_select_callback(device_id)

    def _on_device_refresh(self):
        """Handle device refresh request."""
        if self.on_device_refresh_callback:
            return self.on_device_refresh_callback()
        return []

    def _on_back(self):
        """Handle back button press."""
        if self.on_back_to_playlists_callback:
            self.on_back_to_playlists_callback()
