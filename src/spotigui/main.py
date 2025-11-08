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

from spotigui.config import WINDOW_WIDTH, WINDOW_HEIGHT, APP_NAME, DEFAULT_PLAYLISTS_COUNT, DEFAULT_DEVICE_NAME
from spotigui.spotify_api import SpotifyAPI
from spotigui.screens.login_screen import LoginScreen
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
        self.login_screen = None
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
        
        self.icon = 'icon.png'

        # Set theme to light mode with white background
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Lightpink"

        # Create screen manager
        self.screen_manager = MDScreenManager()

        # Create and add login screen
        self.login_screen = LoginScreen(spotify_api=self.spotify_api)
        self.screen_manager.add_widget(self.login_screen)

        # Create and add home screen (playlists)
        self.home_screen = HomeScreen(
            on_playlist_select=self._on_playlist_select,
            on_navigate_to_now_playing=self._on_navigate_to_now_playing,
            on_device_select=self._on_device_select,
            on_device_refresh=self._on_device_refresh,
        )
        self.screen_manager.add_widget(self.home_screen)

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

        # Don't set initial screen yet - will be determined by auth check in on_start
        # Login screen is added first, so it will be the default current screen


        return self.screen_manager


    def on_start(self):
        """Called when app is starting."""
        # Check authentication in background thread
        auth_thread = threading.Thread(target=self._check_and_setup_auth, daemon=True)
        auth_thread.start()

    def _check_and_setup_auth(self):
        """Check if already authenticated, or show login screen."""
        # Initialize OAuth manager (without opening browser)
        self.spotify_api.init_oauth_manager(open_browser=False)

        # Check if already authenticated (from cache)
        if self.spotify_api.check_auth_complete():
            Logger.info("SpotiGUI: Already authenticated from cache")
            # Already authenticated, proceed to home screen
            Clock.schedule_once(lambda dt: self._on_auth_complete(), 0)
        else:
            Logger.info("SpotiGUI: Not authenticated, showing login screen")
            # Not authenticated, show login screen with QR code
            auth_url = self.spotify_api.get_auth_url()
            if auth_url:
                Clock.schedule_once(
                    lambda dt: self._show_login_screen(auth_url), 0
                )
            else:
                Logger.error("SpotiGUI: Failed to generate auth URL")

    @mainthread
    def _show_login_screen(self, auth_url: str):
        """Display login screen with QR code."""
        # Switch to login screen first so widget tree is built
        self.screen_manager.current = "login"

        # Set auth URL after screen is displayed (small delay to ensure widgets are ready)
        Clock.schedule_once(lambda dt: self._setup_login_screen(auth_url), 0.1)

    def _setup_login_screen(self, auth_url: str):
        """Set up login screen with QR code after widgets are ready."""
        self.login_screen.set_auth_url(auth_url)
        self.login_screen.start_auth_check(self.spotify_api.check_auth_complete)

    def on_auth_complete(self):
        """Called when authentication is complete."""
        self._on_auth_complete()

    def _on_auth_complete(self):
        """Handle successful authentication."""
        Logger.info("SpotiGUI: Authentication complete, initializing app")

        # Stop login screen polling
        if self.login_screen:
            self.login_screen.stop_auth_check()

        # Fetch initial playlists (schedule on main thread)
        Logger.info("SpotiGUI: Loading playlists...")
        self._load_playlists_trigger()

        # Get available devices and select the default one
        Logger.info("SpotiGUI: Getting available devices...")
        devices = self.spotify_api.get_available_devices()
        if devices:
            self.current_device_id = self._select_default_device(devices)
        else:
            Logger.warning("SpotiGUI: No Spotify devices found")

        # Start polling for playback state
        Logger.info("SpotiGUI: Starting playback polling...")
        self.stop_polling = False
        self.playback_poll_thread = threading.Thread(
            target=self._poll_playback_state, daemon=True
        )
        self.playback_poll_thread.start()

        # Navigate to home screen
        Logger.info("SpotiGUI: Scheduling navigation to home screen in 0.5s")
        Clock.schedule_once(lambda dt: self._navigate_to_home(), 0.5)

    @mainthread
    def _navigate_to_home(self):
        """Navigate to home screen."""
        Logger.info(f"SpotiGUI: Navigating to home screen (current: {self.screen_manager.current})")
        self.screen_manager.current = "home"
        Logger.info(f"SpotiGUI: Navigation complete (current: {self.screen_manager.current})")

    def _select_default_device(self, devices):
        """
        Select the default device based on configuration.

        Args:
            devices: List of available Spotify devices

        Returns:
            Device ID of the selected device
        """
        if not devices:
            Logger.warning("SpotiGUI: No devices available")
            return None

        # If default device name is configured, try to find it
        if DEFAULT_DEVICE_NAME:
            for device in devices:
                device_name = device.get("name", "")
                if device_name.lower() == DEFAULT_DEVICE_NAME.lower():
                    device_id = device.get("id")
                    Logger.info(f"SpotiGUI: Selected default device: {device_name} (ID: {device_id})")
                    return device_id

            Logger.warning(f"SpotiGUI: Default device '{DEFAULT_DEVICE_NAME}' not found. Using first available device.")

        # Fallback to first available device
        first_device = devices[0]
        device_name = first_device.get("name", "Unknown")
        device_id = first_device.get("id")
        Logger.info(f"SpotiGUI: Using first available device: {device_name} (ID: {device_id})")
        return device_id

    def _load_playlists(self, _dt=None):
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
                Logger.error(f"SpotiGUI: Playback polling error: {e}")
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
    def _update_track_info(self, _dt=None):
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

    def _on_navigate_to_now_playing(self):
        """Handle navigation to now playing screen from home."""
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
