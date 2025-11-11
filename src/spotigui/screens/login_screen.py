"""Login screen with QR code for Spotify OAuth authentication."""

import io
import threading

import qrcode
from kivy.app import App
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.properties import StringProperty, ObjectProperty
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from spotigui import resource_path

# Load the KV file
Builder.load_file(resource_path("src/spotigui/screens/login_screen.kv"))


class LoginScreen(MDScreen):
    """Screen that displays a QR code for Spotify OAuth authentication.

    Instead of opening a browser window, this screen generates a QR code
    from the Spotify OAuth URL. Users can scan it with their phone to
    authenticate.
    """

    # Properties
    auth_url = StringProperty("")
    qr_image = ObjectProperty(None)
    status_text = StringProperty("Scan the QR code to authenticate with Spotify")

    def __init__(self, spotify_api=None, **kwargs):
        super().__init__(**kwargs)
        self._auth_check_event = None
        self._spotify_api = spotify_api

    def on_kv_post(self, base_widget):
        """Called after the KV file has been applied."""
        super().on_kv_post(base_widget)
        # Start the spinner initially since QR code will be loaded
        if 'qr_spinner' in self.ids:
            self.ids.qr_spinner.start()
        # Bind to qr_image property changes
        self.bind(qr_image=self._on_qr_image_change)

    def _on_qr_image_change(self, instance, value):
        """Handle QR image property changes."""
        if value and hasattr(self, 'ids') and 'qr_spinner' in self.ids:
            self.ids.qr_spinner.stop()
        elif not value and hasattr(self, 'ids') and 'qr_spinner' in self.ids:
            self.ids.qr_spinner.start()

    def set_auth_url(self, url: str):
        """Set the OAuth URL and generate QR code.

        Args:
            url: The Spotify OAuth authorization URL
        """
        self.auth_url = url
        # Generate QR code in background thread
        threading.Thread(
            target=self._generate_qr_code,
            args=(url,),
            daemon=True
        ).start()

    def _generate_qr_code(self, url: str):
        """Generate QR code image from URL in background thread.

        Args:
            url: The URL to encode in the QR code
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)

            # Create PIL image
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert PIL image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Schedule UI update on main thread
            Clock.schedule_once(
                lambda dt: self._update_qr_image(img_bytes.getvalue()),
                0
            )

        except Exception as e:
            Logger.error(f"LoginScreen: Failed to generate QR code: {e}")
            Clock.schedule_once(
                lambda dt: self._update_status("Failed to generate QR code"),
                0
            )

    def _update_qr_image(self, img_data: bytes):
        """Update the QR code image widget on main thread.

        Args:
            img_data: PNG image data as bytes
        """
        try:
            # Create CoreImage from bytes
            data = io.BytesIO(img_data)
            core_image = CoreImage(data, ext='png')

            # Set the property - the KV binding will update the widget automatically
            self.qr_image = core_image.texture

        except Exception as e:
            Logger.error(f"LoginScreen: Failed to update QR image: {e}")
            import traceback
            Logger.error(f"LoginScreen: Traceback: {traceback.format_exc()}")
            self.status_text = "Failed to display QR code"

    def _update_status(self, text: str):
        """Update the status text on main thread.

        Args:
            text: Status message to display
        """
        self.status_text = text

    def start_auth_check(self, check_callback):
        """Start periodic checking for authentication completion.

        Args:
            check_callback: Function to call that returns True if auth is complete
        """
        self._check_callback = check_callback
        self._auth_check_event = Clock.schedule_interval(
            self._check_auth_status,
            2.0  # Check every 2 seconds
        )
        self.status_text = "Scan the QR code with your phone to authenticate"

    def _check_auth_status(self, dt):
        """Check if authentication has completed."""
        if hasattr(self, '_check_callback') and self._check_callback():
            # Authentication successful
            self.status_text = "Authentication successful! Loading playlists..."

            # Stop checking
            if self._auth_check_event:
                self._auth_check_event.cancel()
                self._auth_check_event = None

            # Get the running app and trigger authentication completion
            app = App.get_running_app()
            if app and hasattr(app, 'on_auth_complete'):
                app.on_auth_complete()
            else:
                Logger.error("LoginScreen: Cannot navigate - app not available or missing on_auth_complete method")

    def stop_auth_check(self):
        """Stop checking for authentication completion."""
        if self._auth_check_event:
            self._auth_check_event.cancel()
            self._auth_check_event = None

    def on_leave(self):
        """Clean up when leaving the screen."""
        self.stop_auth_check()
