# Building spotigui Executable

This guide explains how to package spotigui into a standalone executable with all dependencies included.

## Prerequisites

- Python 3.13
- Virtual environment with all dependencies installed
- PyInstaller (installed automatically by build script)

## Build Instructions

### macOS

1. Make sure you're in the project root directory:
   ```bash
   cd /Users/jackyhoareau/Documents/hypermuse/spotigui
   ```

2. Run the build script:
   ```bash
   ./build.sh
   ```

3. The executable will be created in the `dist` directory:
   - **App Bundle**: `dist/spotigui.app` (recommended for macOS)
   - **Executable**: `dist/spotigui` (if app bundle creation fails)

4. Run the application:
   ```bash
   open dist/spotigui.app
   ```
   Or:
   ```bash
   ./dist/spotigui
   ```

### Manual Build (if build.sh fails)

1. Activate virtual environment:
   ```bash
   source myenv/bin/activate
   ```

2. Install PyInstaller if not already installed:
   ```bash
   pip install pyinstaller
   ```

3. Clean previous builds:
   ```bash
   rm -rf build dist
   ```

4. Run PyInstaller with the spec file:
   ```bash
   pyinstaller spotigui.spec
   ```

## What Gets Packaged

The build includes:
- All Python code from `src/spotigui/`
- All `.kv` files (UI layouts)
- The application icon (`icon.png`)
- All required dependencies:
  - Kivy and KivyMD
  - Spotipy (Spotify API client)
  - QRCode generator
  - PIL/Pillow
  - Other Python dependencies

## Configuration

### Environment Variables

The packaged app still requires a `.env` file with your Spotify API credentials. You have two options:

1. **Place .env next to the executable:**
   ```
   dist/
     spotigui.app/
     .env
   ```

2. **Place .env in user's home directory:**
   ```
   ~/.spotigui/.env
   ```

The `.env` file should contain:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

## Troubleshooting

### Build Fails with Missing Module

If PyInstaller can't find a module, add it to the `hiddenimports` list in `spotigui.spec`:

```python
hiddenimports=[
    'your.missing.module',
    # ... other imports
],
```

### KV Files Not Found

The application uses a `resource_path()` function to correctly locate KV files in both development and packaged environments. The spec file automatically collects all `.kv` files. If you add new KV files:

1. They will be included automatically in the next build
2. Make sure to use `resource_path()` when loading them with `Builder.load_file()`:

```python
from spotigui import resource_path
Builder.load_file(resource_path("src/spotigui/your_file.kv"))
```

### App Won't Start

1. Try running from terminal to see error messages:
   ```bash
   dist/spotigui.app/Contents/MacOS/spotigui
   ```

2. Check that your `.env` file is in the correct location

3. Verify Spotify API credentials are correct

### Large File Size

The packaged app includes the entire Python runtime and all dependencies. Typical size is 100-200MB. This is normal for Python GUI applications.

To reduce size:
- Remove unused dependencies from your virtual environment before building
- Use `upx=True` in the spec file (already enabled)

## Distribution

### macOS App Bundle

The `spotigui.app` bundle can be:
1. Copied to `/Applications/`
2. Distributed as a `.dmg` file (requires additional tools like `create-dmg`)
3. Zipped and shared directly

**Note**: macOS will show a security warning for unsigned apps. Users need to:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the security dialog

### Code Signing (Optional)

For distribution, you should code sign the app with an Apple Developer certificate:

```bash
codesign --deep --force --sign "Developer ID Application: Your Name" dist/spotigui.app
```

## Windows Build (Cross-platform)

To build for Windows, you need to run PyInstaller on a Windows machine:

1. Install Python 3.13 on Windows
2. Create virtual environment: `python -m venv myenv`
3. Activate: `myenv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install PyInstaller: `pip install pyinstaller`
6. Build: `pyinstaller spotigui.spec`

The Windows build will create `dist/spotigui.exe`.

## Linux Build

Similar to Windows, run on a Linux machine:

1. Install Python 3.13
2. Create virtual environment
3. Install dependencies including system packages for Kivy
4. Run PyInstaller

Linux builds create a single executable in `dist/spotigui`.
