"""Now Playing screen showing current track and playback controls."""

from typing import Optional, Callable, Dict, Any
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

from spotigui.widgets.volume_sheet import VolumeControlWidget

# Load the KV file
Builder.load_file("src/spotigui/screens/now_playing_screen.kv")


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

        # Store volume widget reference (will be shown as modal)
        self.volume_widget = VolumeControlWidget(
            on_volume_change=self._on_volume_change,
            on_mute_toggle=self._on_mute_toggle,
        )

    def on_kv_post(self, base_widget):
        """Called after the KV file has been applied."""
        super().on_kv_post(base_widget)

        # Set up top bar callbacks after widgets are created
        self.ids.top_bar.on_back_callback = self._on_back
        self.ids.top_bar.on_device_select_callback = self._on_device_select
        self.ids.top_bar.on_device_refresh_callback = self._on_device_refresh

        # Set up playback controls callbacks
        self.ids.playback_controls.on_play_callback = self._on_play
        self.ids.playback_controls.on_pause_callback = self._on_pause
        self.ids.playback_controls.on_next_callback = self._on_next
        self.ids.playback_controls.on_previous_callback = self._on_previous
        self.ids.playback_controls.on_volume_click_callback = self._show_volume_sheet

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
        self.ids.progress_bar.update_progress(current_pos_ms, duration_ms)

    def set_playing_state(self, is_playing: bool):
        """
        Update playing state.

        Args:
            is_playing: True if track is playing, False otherwise
        """
        self.ids.playback_controls.set_playing_state(is_playing)

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

    def _show_volume_sheet(self):
        """Show the volume control bottom sheet."""
        from kivymd.uix.bottomsheet import MDBottomSheet

        # Create bottom sheet each time (KivyMD best practice)
        bottom_sheet = MDBottomSheet()
        bottom_sheet.add_widget(self.volume_widget)
        bottom_sheet.status="opened"

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
