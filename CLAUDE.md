# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**spotigui** is a multiplatform Spotify client designed to control any Spotify devices. This is a Python-based project that will provide a graphical user interface for cross-platform use (Windows, macOS, Linux).

### Current Status

This repository is in its **very initial stage** with only basic boilerplate files:
- `README.md` - Project description
- `LICENSE` - MIT License
- `.gitignore` - Python-focused ignore patterns

No source code, configuration, or build files have been created yet.

## Technology Stack

- **Language**: Python 3.x
- **GUI Framework**: Kivy (cross-platform, supports Windows, macOS, Linux, iOS, Android)
- **Target**: Cross-platform desktop application with GUI
- **Default Window Size**: 720x720 pixels
- **Authentication**: OAuth (via spotipy's SpotifyOAuth)
- **Build Tool**: PyInstaller (for creating executables, based on .gitignore patterns)
- **Testing Framework**: pytest (configured in .gitignore)

## Project Setup (To Be Implemented)

When setting up this project, the following will need to be created:

### Configuration Files
- `pyproject.toml` or `setup.py` - Python package metadata and dependencies
- `requirements.txt` - Pinned dependency versions
- Build configuration for PyInstaller

### Project Structure (Expected)
- `src/spotigui/` - Main package directory
- `tests/` - Test files
- Build output directories (handled by PyInstaller)

### Key Dependencies
- **Kivy** - Cross-platform GUI framework
- **KivyMD** - Material Design implementation for Kivy (for polished, modern UI components)
- **spotipy** - Official Spotify Web API Python client library for simplified API integration
- Possibly async libraries (`aiohttp`, `asyncio`) for handling API calls without blocking the UI

## Architecture Overview

The application has the following architectural layers and features:

### Core Layers

1. **Spotify API Layer** - Communication with Spotify Web API, authentication/OAuth via spotipy
2. **Device Management** - List and control available Spotify devices
3. **Playback Control** - Manage playback state (play, pause, resume, next, previous)
4. **GUI/UI Layer** - Cross-platform user interface with Material Design
5. **Configuration** - Manage settings and credentials

### Core Features

**Playback Controls**
- Play/Pause/Resume functionality
- Next track button / Swipe right gesture
- Previous track button / Swipe left gesture
- Volume control (increase/decrease)
- Mute/Unmute toggle
- These controls should be easily accessible and prominently displayed in the UI
- Swipe gestures provide alternative navigation method for intuitive touch-based control

**Track Progress Display**
- Status bar showing current playback position and track duration
- Display time remaining (minutes and seconds) before track ends
- Update in real-time as track plays
- Should be prominently visible during playback

**Home Screen**
- Default view displays user's Spotify playlists
- Playlists displayed as tiles in a grid layout
- Display 6 playlists by default (scrollable for additional playlists)
- Each tile should display relevant metadata (name, description, cover art if available)
- Tiles should be responsive, clickable, and support touch interactions (swipe, tap)

## Common Commands (To Be Established)

Once the project is set up with dependencies and structure:

- `python -m pytest` - Run tests
- `python -m pytest tests/test_specific.py` - Run specific test file
- `python -m pytest -v` - Run tests with verbose output
- `python -m ruff check .` - Lint code (if ruff is configured)
- `python -m mypy src/` - Type check (if mypy is configured)
- `pyinstaller src/spotigui/main.spec` - Build executable (once .spec file is created)

## Development Notes

### Kivy-Specific Guidelines

- **Window Size**: Configure the default window to 720x720 pixels (set in `main.py` before importing any Kivy widgets)
- **Touch Capabilities**: The application leverages all Kivy touch capabilities
  - Implement touch event handlers (`on_touch_down`, `on_touch_move`, `on_touch_up`) for custom interactions
  - Support multi-touch gestures for intuitive device control
  - **Swipe Gestures for Playback Control**:
    - Swipe right to move to next track
    - Swipe left to move to previous track
  - Implement long press, swipe, drag, and pinch gestures using Kivy's gesture system or custom touch logic
  - Use `GestureBox` or custom gesture detection for advanced touch interactions
  - Design UI with touch-friendly target sizes and spacing (minimum 48x48 dp for touch targets)
- **Material Design**: Use KivyMD for a modern, polished Material Design UI
  - Install and configure KivyMD library for Material Design components
  - Use `MDApp` instead of standard Kivy `App` class
  - Leverage Material Design widgets (buttons, cards, dialogs, navigation bars, etc.)
  - Use `MDGridLayout` or `RecycleGridLayout` for playlist tile grid display
  - Use `MDCard` for individual playlist tiles with images and metadata
  - Follow Material Design guidelines for spacing, typography, color, and elevation
  - Use `MDTheme` for consistent theming across the application
- **KV Language**: Use `.kv` files for UI layout and design (separate from Python logic)
- **Threading**: Use `threading` or `asyncio` for spotipy API calls to prevent blocking the Kivy event loop
- **Dependencies**: Install from wheel files for cross-platform compatibility (especially for PyInstaller builds)
- **Screen Management**: Use `ScreenManager` for handling multiple screens/views in the app

### Spotify Integration (spotipy)

- **Authentication**: Use spotipy's `SpotifyOAuth` for OAuth flow (not `SpotifyClientCredentials`)
  - Configure required OAuth scopes: `user-read-private`, `user-read-playback-state`, `user-modify-playback-state`, `playlist-read-private`
  - Handle the OAuth redirect callback (typically `http://localhost:8888/callback`)
- **Playback Controls**: Use spotipy's playback control methods:
  - `start_playback()` / `pause_playback()` for play/pause
  - `next_track()` for next song
  - `previous_track()` for previous song
  - `volume()` for volume control
- **Playback State**: Regularly poll `current_playback()` to get:
  - Current track progress (in milliseconds) and duration
  - Calculate time remaining (duration - progress) and convert to minutes:seconds format
  - Display in status bar that updates in real-time
  - Use threading to poll playback state without blocking UI
- **Volume Management**:
  - Use `volume()` to adjust playback volume
  - Implement mute by storing current volume and setting to 0
  - Implement unmute by restoring stored volume value
- **Playlist Retrieval**: Use spotipy's `current_user_playlists()` to fetch user's playlists for home screen display
  - Paginate results and load 6 playlists by default
  - Support scrolling/pagination for additional playlists
- **Async Calls**: Wrap all spotipy calls in threads to prevent blocking the Kivy UI during API requests
- **Credential Storage**: Securely store refresh tokens and API credentials (use `spotipy.CacheHandler` or custom secure storage)
- **Device Control**: Use spotipy's device listing and playback control methods to manage Spotify devices

### General Development

- The `.gitignore` includes patterns for Python virtual environments (`venv/`, `.venv/`), `pytest`, and PyInstaller
- Use a virtual environment for all development work
- The project targets multiple platforms - test on Windows, macOS, and Linux
- Spotify API requires OAuth authentication - plan credential handling carefully
- PyInstaller will be used to package the application for distribution
- Build and test on each target platform before release (Kivy apps can have platform-specific quirks)
