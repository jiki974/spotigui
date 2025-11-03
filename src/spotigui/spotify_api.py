"""
Spotify API wrapper using spotipy library.
Handles authentication, playback control, device management, and playlist retrieval.
"""

from typing import Optional, Dict, List, Any
import logging
import threading
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from kivy.logger import Logger
from spotigui.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPES, CACHE_DIR
from spotigui.oauth_callback_server import OAuthCallbackServer

# Suppress verbose spotipy logging
logging.getLogger('spotipy').setLevel(logging.WARNING)

class SpotifyAPI:
    """Wrapper around spotipy Spotify Web API client."""

    def __init__(self):
        """Initialize the Spotify API client."""
        self.sp: Optional[spotipy.Spotify] = None
        self.oauth_manager: Optional[SpotifyOAuth] = None
        self.callback_server: Optional[OAuthCallbackServer] = None
        self.callback_thread: Optional[threading.Thread] = None

    def init_oauth_manager(self, open_browser: bool = False):
        """
        Initialize OAuth manager without authenticating.

        Args:
            open_browser: Whether to open browser for OAuth (default False for QR code flow)
        """
        if not self.oauth_manager:
            self.oauth_manager = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SPOTIFY_SCOPES,
                cache_path=str(CACHE_DIR / ".spotify_cache"),
                open_browser=open_browser,
            )

    def start_callback_server(self):
        """Start the OAuth callback server to receive redirects."""
        if not self.callback_server:
            try:
                self.callback_server = OAuthCallbackServer(port=8888)
                self.callback_server.start()
                Logger.info("SpotifyAPI: OAuth callback server started")
            except Exception as e:
                Logger.error(f"SpotifyAPI: Failed to start callback server: {e}")
                raise

    def stop_callback_server(self):
        """Stop the OAuth callback server."""
        if self.callback_server:
            self.callback_server.stop()
            self.callback_server = None
            Logger.info("SpotifyAPI: OAuth callback server stopped")

    def get_auth_url(self) -> Optional[str]:
        """
        Get the OAuth authorization URL for QR code display.
        Also starts the callback server to receive the redirect.

        Returns:
            str: Authorization URL or None if OAuth manager not initialized
        """
        if not self.oauth_manager:
            self.init_oauth_manager(open_browser=False)

        try:
            # Start callback server to receive the OAuth redirect
            self.start_callback_server()

            auth_url = self.oauth_manager.get_authorize_url()
            Logger.info("SpotifyAPI: Generated OAuth authorization URL")
            return auth_url
        except Exception as e:
            Logger.error(f"SpotifyAPI: Failed to generate auth URL: {e}")
            return None

    def process_callback_url(self, callback_url: str) -> bool:
        """
        Process the OAuth callback URL to complete authentication.

        Args:
            callback_url: The full callback URL with authorization code

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.oauth_manager:
            Logger.error("SpotifyAPI: OAuth manager not initialized")
            return False

        try:
            # Extract the authorization code from the callback URL
            code = self.oauth_manager.parse_response_code(callback_url)
            if not code:
                Logger.error("SpotifyAPI: No authorization code found in callback URL")
                return False

            Logger.info("SpotifyAPI: Authorization code extracted, exchanging for token...")

            # Exchange the code for an access token
            token_info = self.oauth_manager.get_access_token(code, as_dict=True, check_cache=False)

            if token_info:
                # Initialize Spotify client
                self.sp = spotipy.Spotify(auth_manager=self.oauth_manager)
                # Verify it works
                self.sp.current_user()
                Logger.info("SpotifyAPI: Successfully authenticated via callback URL")
                return True

        except Exception as e:
            Logger.error(f"SpotifyAPI: Failed to process callback URL: {e}")

        return False

    def check_auth_complete(self) -> bool:
        """
        Check if user has completed OAuth authentication.

        Checks both cached tokens and the callback server (non-blocking).

        Returns:
            bool: True if authentication is complete, False otherwise
        """
        if not self.oauth_manager:
            return False

        try:
            # Try to get cached token first (fast path)
            token_info = self.oauth_manager.get_cached_token()

            if token_info and not self.oauth_manager.is_token_expired(token_info):
                # Token exists and is valid, initialize Spotify client
                if not self.sp:
                    self.sp = spotipy.Spotify(auth_manager=self.oauth_manager)
                    # Verify it works
                    self.sp.current_user()
                    Logger.info("SpotifyAPI: Successfully authenticated with cached token")
                    # Stop callback server if running
                    self.stop_callback_server()
                return True

            # Check if callback server received authorization code
            if self.callback_server and self.callback_server.wait_for_callback(timeout=0):
                code = self.callback_server.wait_for_callback(timeout=0)
                if code:
                    Logger.info("SpotifyAPI: Authorization code received from callback server")
                    # Exchange code for token
                    token_info = self.oauth_manager.get_access_token(code, as_dict=True, check_cache=False)
                    if token_info:
                        self.sp = spotipy.Spotify(auth_manager=self.oauth_manager)
                        self.sp.current_user()
                        Logger.info("SpotifyAPI: Successfully authenticated via callback server")
                        self.stop_callback_server()
                        return True

        except SpotifyException as e:
            Logger.debug(f"SpotifyAPI: Auth check - not yet complete: {e}")
        except Exception as e:
            Logger.debug(f"SpotifyAPI: Auth check error: {e}")

        return False

    def authenticate(self, open_browser: bool = False) -> bool:
        """
        Authenticate with Spotify using OAuth flow.

        Args:
            open_browser: Whether to open browser (False for QR code flow)

        Returns:
            bool: True if authentication successful, False otherwise.
        """
        try:
            self.init_oauth_manager(open_browser=open_browser)
            self.sp = spotipy.Spotify(auth_manager=self.oauth_manager)
            # Test the connection by getting current user info
            self.sp.current_user()
            Logger.info("SpotifyAPI: Successfully authenticated with Spotify")
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify authentication failed: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Authentication failed: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self.sp is not None

    def get_current_user_playlists(self, limit: int = 6, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get current user's playlists.

        Args:
            limit: Number of playlists to return (default 6)
            offset: Index offset for pagination (default 0)

        Returns:
            List of playlist dictionaries with name, description, and images.
        """
        if not self.is_authenticated():
            return []

        try:
            results = self.sp.current_user_playlists(limit=limit, offset=offset)
            return results.get("items", [])
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error fetching playlists: {e}")
            return []
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error fetching playlists: {e}")
            return []

    def get_current_playback(self) -> Optional[Dict[str, Any]]:
        """
        Get current playback state information.

        Returns:
            Dictionary with playback state or None if error.
        """
        if not self.is_authenticated():
            return None

        try:
            return self.sp.current_playback()
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error fetching playback state: {e}")
            return None
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error fetching playback state: {e}")
            return None

    def play(self, device_id: Optional[str] = None, context_uri: Optional[str] = None) -> bool:
        """
        Start playback.

        Args:
            device_id: Device ID to play on (if None, uses active device)
            context_uri: Spotify URI of playlist/album to play (optional)

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.start_playback(device_id=device_id, context_uri=context_uri)
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error starting playback: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error starting playback: {e}")
            return False

    def pause(self, device_id: Optional[str] = None) -> bool:
        """
        Pause playback.

        Args:
            device_id: Device ID to pause on (if None, uses active device)

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.pause_playback(device_id=device_id)
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error pausing playback: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error pausing playback: {e}")
            return False

    def next_track(self, device_id: Optional[str] = None) -> bool:
        """
        Skip to next track.

        Args:
            device_id: Device ID to skip on (if None, uses active device)

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.next_track(device_id=device_id)
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error skipping to next track: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error skipping to next track: {e}")
            return False

    def previous_track(self, device_id: Optional[str] = None) -> bool:
        """
        Skip to previous track.

        Args:
            device_id: Device ID to go back on (if None, uses active device)

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.previous_track(device_id=device_id)
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error skipping to previous track: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error skipping to previous track: {e}")
            return False

    def set_volume(self, volume_percent: int, device_id: Optional[str] = None) -> bool:
        """
        Set playback volume.

        Args:
            volume_percent: Volume level (0-100)
            device_id: Device ID to set volume on (if None, uses active device)

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.volume(volume_percent, device_id=device_id)
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error setting volume: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error setting volume: {e}")
            return False

    def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available Spotify devices.

        Returns:
            List of device dictionaries with id, name, type, and is_active.
        """
        if not self.is_authenticated():
            return []

        try:
            devices = self.sp.devices()
            return devices.get("devices", [])
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error fetching devices: {e}")
            return []
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error fetching devices: {e}")
            return []

    def transfer_playback(self, device_id: str, force_play: bool = False) -> bool:
        """
        Transfer playback to a specific device.

        Args:
            device_id: Device ID to transfer playback to
            force_play: Whether to start playback immediately after transfer

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.transfer_playback(device_id=device_id, force_play=force_play)
            Logger.info(f"SpotifyAPI: Transferred playback to device {device_id}")
            return True
        except SpotifyException as e:
            Logger.error(f"SpotifyAPI: Spotify error transferring playback: {e}")
            return False
        except Exception as e:
            Logger.error(f"SpotifyAPI: Error transferring playback: {e}")
            return False
