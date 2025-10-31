"""
Main entry point for spotigui application.
Initializes the Kivy/KivyMD application with 720x720 window size.
"""

import threading
import time
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import Clock, mainthread
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from spotigui.config import WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME, DEFAULT_PLAYLISTS_COUNT
from spotigui.spotify_api import SpotifyAPI
from spotigui.screens.home_screen import HomeScreen
from spotigui.screens.now_playing_screen import NowPlayingScreen


# Configure window size before importing any other Kivy widgets
Window.size = (WINDOW_WIDTH, WINDOW_HEIGHT)


class SpotiGuiApp(MDApp):
    """Main application class for spotigui."""

    def __init__(self, **kwargs):
        """Initialize the application."""
        super().__init__(**kwargs)
        self.title = APP_NAME
        self.spotify_api = SpotifyAPI()
        self.home_screen = None
        self.now_playing_screen = None
        self.screen_manager = None
        self.playback_poll_thread = None
        self.stop_polling = False
        self.current_device_id = None
        self.is_muted = False
        self.mute_volume = 50

        # Create triggers for better performance
        self._load_playlists_trigger = Clock.create_trigger(self._load_playlists, 0)
        self._update_track_info_trigger = Clock.create_trigger(self._update_track_info, 0)

    def build(self):
        """Build the application UI."""
        # Set theme to light mode with white background
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # Create screen manager
        self.screen_manager = MDScreenManager()

        # Create and add home screen (playlists)
        self.home_screen = HomeScreen(
            on_playlist_select=self._on_playlist_select,
        )
        # self.screen_manager.add_widget(self.home_screen)

        # Create and add now playing screen
        self.now_playing_screen = NowPlayingScreen(
            on_play=self._on_play,
            on_pause=self._on_pause,
            on_next=self._on_next,
            on_previous=self._on_previous,
            on_volume_change=self._on_volume_change,
            on_mute_toggle=self._on_mute_toggle,
            on_device_select=self._on_device_select,
            on_device_refresh=self._on_device_refresh,
            on_back_to_playlists=self._on_back_to_playlists,
        )
        self.screen_manager.add_widget(self.now_playing_screen)

        return self.screen_manager

    def on_start(self):
        """Called when app is starting."""
        # Authenticate with Spotify in a background thread
        auth_thread = threading.Thread(target=self._authenticate_spotify, daemon=True)
        auth_thread.start()

    def _authenticate_spotify(self):
        """Authenticate with Spotify API."""
        if self.spotify_api.authenticate():
            # Fetch initial playlists (schedule on main thread)
            self._load_playlists_trigger()

            # Get available devices
            devices = self.spotify_api.get_available_devices()
            if devices:
                self.current_device_id = devices[0].get("id")

            # Start polling for playback state
            self.stop_polling = False
            self.playback_poll_thread = threading.Thread(
                target=self._poll_playback_state, daemon=True
            )
            self.playback_poll_thread.start()
        else:
            Logger.error("SpotiGUI", "Failed to authenticate with Spotify")

    def _load_playlists(self, dt=None):
        """Load user playlists and display them."""
        self.home_screen.show_loading()

        def load_playlists_thread():
            playlists = self.spotify_api.get_current_user_playlists(
                limit=DEFAULT_PLAYLISTS_COUNT
            )
            # Use mainthread decorator for thread-safe UI updates
            self._update_playlists_ui(playlists)

        thread = threading.Thread(target=load_playlists_thread, daemon=True)
        thread.start()

    @mainthread
    def _update_playlists_ui(self, playlists):
        """Update playlists in UI (runs on main thread)."""
        self.home_screen.add_playlists(playlists)

    def _poll_playback_state(self):
        """Poll Spotify API for current playback state."""
        while not self.stop_polling:
            try:
                playback = self.spotify_api.get_current_playback()
                if playback:
                    is_playing = playback.get("is_playing", False)
                    progress_ms = playback.get("progress_ms", 0)
                    item = playback.get("item", {})
                    duration_ms = item.get("duration_ms", 0)

                    # Update UI in main thread using mainthread decorator
                    self._update_playback_ui(is_playing, progress_ms, duration_ms, item)

                time.sleep(1)  # Poll every second
            except Exception as e:
                Logger.error("SpotiGUI", f"Playback polling error: {e}")
                time.sleep(2)

    @mainthread
    def _update_playback_ui(self, is_playing: bool, progress_ms: int, duration_ms: int, track_data: dict):
        """Update UI with current playback state (runs on main thread)."""
        # Update now playing screen if it's the current screen
        if self.screen_manager.current == "now_playing":
            self.now_playing_screen.set_playing_state(is_playing)
            self.now_playing_screen.update_progress(progress_ms, duration_ms)
            self.now_playing_screen.update_track_info(track_data)

    @mainthread
    def _update_track_info(self, dt=None):
        """Update track info on now playing screen (runs on main thread)."""
        playback = self.spotify_api.get_current_playback()
        if playback:
            item = playback.get("item", {})
            self.now_playing_screen.update_track_info(item)

    def _on_play(self):
        """Handle play action."""
        thread = threading.Thread(
            target=lambda: self.spotify_api.play(self.current_device_id), daemon=True
        )
        thread.start()

    def _on_pause(self):
        """Handle pause action."""
        thread = threading.Thread(
            target=lambda: self.spotify_api.pause(self.current_device_id), daemon=True
        )
        thread.start()

    def _on_next(self):
        """Handle next track action."""
        thread = threading.Thread(
            target=lambda: self.spotify_api.next_track(self.current_device_id), daemon=True
        )
        thread.start()

    def _on_previous(self):
        """Handle previous track action."""
        thread = threading.Thread(
            target=lambda: self.spotify_api.previous_track(self.current_device_id), daemon=True
        )
        thread.start()

    def _on_volume_change(self, volume: int):
        """Handle volume change."""
        self.mute_volume = volume
        self.is_muted = False
        thread = threading.Thread(
            target=lambda: self.spotify_api.set_volume(volume, self.current_device_id),
            daemon=True,
        )
        thread.start()

    def _on_mute_toggle(self, is_muted: bool):
        """Handle mute toggle."""
        self.is_muted = is_muted
        if is_muted:
            # Store current volume and set to 0
            thread = threading.Thread(
                target=lambda: self.spotify_api.set_volume(0, self.current_device_id),
                daemon=True,
            )
        else:
            # Restore previous volume
            thread = threading.Thread(
                target=lambda: self.spotify_api.set_volume(
                    self.mute_volume, self.current_device_id
                ),
                daemon=True,
            )
        thread.start()

    def _on_playlist_select(self, playlist_data: dict):
        """Handle playlist selection."""
        playlist_uri = playlist_data.get("uri")
        if playlist_uri:
            def play_playlist():
                self.spotify_api.play(self.current_device_id, context_uri=playlist_uri)
                # Update track info after starting playback
                time.sleep(0.5)  # Brief delay to let playback start
                self._update_track_info_trigger()

            thread = threading.Thread(target=play_playlist, daemon=True)
            thread.start()

            # Navigate to now playing screen
            self.screen_manager.current = "now_playing"

    def _on_back_to_playlists(self):
        """Handle navigation back to playlists screen."""
        self.screen_manager.current = "home"

    def _on_device_select(self, device_id: str):
        """Handle device selection."""
        Logger.info(f"SpotiGUI: Device selected: {device_id}")
        self.current_device_id = device_id
        # Transfer playback to the selected device
        thread = threading.Thread(
            target=lambda: self.spotify_api.transfer_playback(device_id, force_play=False),
            daemon=True
        )
        thread.start()

    def _on_device_refresh(self):
        """Handle device refresh request."""
        devices = self.spotify_api.get_available_devices()
        Logger.info(f"SpotiGUI: Found {len(devices)} devices")
        return devices

    def on_stop(self):
        """Called when app is stopping."""
        self.stop_polling = True
        if self.playback_poll_thread:
            self.playback_poll_thread.join(timeout=2)


def main():
    """Entry point for the application."""
    app = SpotiGuiApp()
    app.run()


if __name__ == "__main__":
    main()
