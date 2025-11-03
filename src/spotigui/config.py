"""
Configuration management for spotigui application.
Handles Spotify API credentials and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings
APP_NAME = "spotigui"
APP_VERSION = "0.1.0"

# Window settings
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 720

# Spotify API settings
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
# Redirect URI - use http://localhost:8888/callback for local development
# For production with Cloudflare Tunnel, set this to your tunnel URL, e.g.:
# SPOTIFY_REDIRECT_URI=https://your-tunnel.trycloudflare.com/callback
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# OAuth scopes required for the application
SPOTIFY_SCOPES = [
    "user-read-private",
    "user-read-playback-state",
    "user-modify-playback-state",
    "playlist-read-private",
]

# Cache directory for Spotify credentials
CACHE_DIR = Path.home() / ".spotigui"
CACHE_DIR.mkdir(exist_ok=True)

# Default number of playlists to display on home screen
DEFAULT_PLAYLISTS_COUNT = 10

# Default device to control (device name to match)
# Set this to the name of your preferred Spotify device
# If empty or None, will use the first available device
DEFAULT_DEVICE_NAME = os.getenv("DEFAULT_DEVICE_NAME", "")
