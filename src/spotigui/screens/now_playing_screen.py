"""Now Playing screen showing current track and playback controls."""

from typing import Optional, Callable, Dict, Any
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.properties import BooleanProperty

from spotigui.widgets.volume_sheet import VolumeControlWidget

# Load the KV file
Builder.load_file("src/spotigui/screens/now_playing_screen.kv")


class NowPlayingScreen(MDScreen):
    """Now Playing screen displaying current track and playback controls."""

    is_playing = BooleanProperty(False)

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

        self.on_play_callback = on_play
        self.on_pause_callback = on_pause
        self.on_next_callback = on_next
        self.on_previous_callback = on_previous
        self.on_volume_change_callback = on_volume_change
        self.on_mute_toggle_callback = on_mute_toggle
        self.on_device_select_callback = on_device_select
        self.on_device_refresh_callback = on_device_refresh
        self.on_back_to_playlists_callback = on_back_to_playlists

        # Store swipe and tap tracking
        self.touch_start_pos = {}
        self.touch_start_time = {}
        self.min_swipe_distance = 50
        self.max_tap_duration = 0.3  # Max duration for tap (in seconds)
        self.max_tap_distance = 10  # Max distance for tap (in pixels)

        # Volume widget will be created fresh each time it's shown

    def on_kv_post(self, base_widget):
        """Called after the KV file has been applied."""
        super().on_kv_post(base_widget)

        # Set up top bar callbacks after widgets are created
        self.ids.top_bar.on_back_callback = self._on_back
        self.ids.top_bar.on_device_select_callback = self._on_device_select
        self.ids.top_bar.on_device_refresh_callback = self._on_device_refresh

        # Bind to album art loading events
        self.ids.album_art.bind(on_load=self._on_image_load)


    def _on_image_load(self, _instance):
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
            self.ids.top_bar.ids.track_name_label.text = "No track playing"
            self.ids.album_art.source = ""
            return

        # Update artist names
        artists = track_data.get("artists", [])
        artist_names = ", ".join([artist.get("name", "") for artist in artists])

        # Update track name
        track_name = track_data.get("name", "Unknown Track")
        self.ids.top_bar.ids.track_name_label.text = " - ".join([track_name, artist_names])

        # Update album info
        album = track_data.get("album", {})

        # Update album art - prefer medium size image (index 1) for better quality
        images = album.get("images", [])
        if images:
            self.ids.album_art.source = images[0]["url"]
        else:
            self.ids.album_art.source = ""

    def update_progress(self, current_pos_ms: int, duration_ms: int):
        """
        Update track progress display.

        Args:
            current_pos_ms: Current position in milliseconds
            duration_ms: Total duration in milliseconds
        """
        current_sec = current_pos_ms // 1000
        duration_sec = duration_ms // 1000

        # Update current position
        self.ids.current_time_label.text = self._format_time(current_sec)

        # Update progress bar
        if duration_sec > 0:
            progress_percent = (current_sec / duration_sec) * 100
            self.ids.progress_bar.value = progress_percent

            # Calculate and update time remaining
            remaining_sec = duration_sec - current_sec
            self.ids.time_remaining_label.text = self._format_time(remaining_sec)
        else:
            self.ids.progress_bar.value = 0
            self.ids.time_remaining_label.text = "00:00"

    @staticmethod
    def _format_time(seconds: int) -> str:
        """
        Format seconds to MM:SS format.

        Args:
            seconds: Number of seconds

        Returns:
            Formatted time string (MM:SS)
        """
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def set_playing_state(self, is_playing: bool):
        """
        Update playing state.

        Args:
            is_playing: True if track is playing, False otherwise
        """
        self.is_playing = is_playing

    def on_touch_down(self, touch):
        """Handle touch down for swipe and tap detection."""
        if super(NowPlayingScreen, self).on_touch_down(touch):
            return True

        if self.collide_point(*touch.pos):
            self.touch_start_pos[touch.uid] = (touch.x, touch.y)
            self.touch_start_time[touch.uid] = touch.time_start
            touch.grab(self)
            return True
        return False

    def on_touch_up(self, touch):
        """Handle touch up to detect swipe gestures and taps."""
        if touch.grab_current is self:
            start_pos = self.touch_start_pos.get(touch.uid)
            start_time = self.touch_start_time.get(touch.uid)

            if start_pos and start_time:
                dx = touch.x - start_pos[0]
                dy = touch.y - start_pos[1]
                distance = (dx ** 2 + dy ** 2) ** 0.5
                duration = touch.time_end - start_time

                # Detect horizontal swipe
                if abs(dx) > self.min_swipe_distance and abs(dy) < abs(dx) / 2:
                    if dx > 0:
                        # Swipe right - next track
                        self._on_next(None)
                    elif dx < 0:
                        # Swipe left - previous track
                        self._on_previous(None)
                # Detect single tap (short duration, minimal movement)
                elif distance < self.max_tap_distance and duration < self.max_tap_duration:
                    # Single tap - open bottom sheet
                    self.open_playback_sheet()

                del self.touch_start_pos[touch.uid]
                del self.touch_start_time[touch.uid]

            touch.ungrab(self)
            return True

        return super(NowPlayingScreen, self).on_touch_up(touch)

    def _on_play_pause(self, _instance):
        """Handle play/pause button press."""
        if self.is_playing:
            if self.on_pause_callback:
                self.on_pause_callback()
        else:
            if self.on_play_callback:
                self.on_play_callback()

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

    def _on_volume_click(self, _instance):
        """Handle volume button click."""
        self._show_volume_sheet()

    def _show_volume_sheet(self):
        """Show the volume control bottom sheet."""
        from kivymd.uix.bottomsheet import MDBottomSheet

        # Create fresh volume widget each time (prevents parent conflict)
        volume_widget = VolumeControlWidget(
            on_volume_change=self._on_volume_change,
            on_mute_toggle=self._on_mute_toggle,
        )

        # Create bottom sheet each time (KivyMD best practice)
        bottom_sheet = MDBottomSheet()
        bottom_sheet.add_widget(volume_widget)
        bottom_sheet.set_state("open")

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

    def open_playback_sheet(self):
        """Open the playback bottom sheet."""
        self.ids.playback_bottom_sheet.set_state("open")

    def close_playback_sheet(self):
        """Close the playback bottom sheet."""
        self.ids.playback_bottom_sheet.set_state("close")
