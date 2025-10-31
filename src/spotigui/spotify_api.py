"""
Spotify API wrapper using spotipy library.
Handles authentication, playback control, device management, and playlist retrieval.
"""

from typing import Optional, Dict, List, Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotigui.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SPOTIFY_SCOPES, CACHE_DIR


class SpotifyAPI:
    """Wrapper around spotipy Spotify Web API client."""

    def __init__(self):
        """Initialize the Spotify API client."""
        self.sp: Optional[spotipy.Spotify] = None
        self.oauth_manager: Optional[SpotifyOAuth] = None

    def authenticate(self) -> bool:
        """
        Authenticate with Spotify using OAuth flow.

        Returns:
            bool: True if authentication successful, False otherwise.
        """
        try:
            self.oauth_manager = SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SPOTIFY_SCOPES,
                cache_path=str(CACHE_DIR / ".spotify_cache"),
            )
            self.sp = spotipy.Spotify(auth_manager=self.oauth_manager)
            # Test the connection by getting current user info
            self.sp.current_user()
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
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
        except Exception as e:
            print(f"Error fetching playlists: {e}")
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
        except Exception as e:
            print(f"Error fetching playback state: {e}")
            return None

    def play(self, device_id: Optional[str] = None) -> bool:
        """
        Start playback.

        Args:
            device_id: Device ID to play on (if None, uses active device)

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_authenticated():
            return False

        try:
            self.sp.start_playback(device_id=device_id)
            return True
        except Exception as e:
            print(f"Error starting playback: {e}")
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
        except Exception as e:
            print(f"Error pausing playback: {e}")
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
        except Exception as e:
            print(f"Error skipping to next track: {e}")
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
        except Exception as e:
            print(f"Error skipping to previous track: {e}")
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
        except Exception as e:
            print(f"Error setting volume: {e}")
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
        except Exception as e:
            print(f"Error fetching devices: {e}")
            return []
