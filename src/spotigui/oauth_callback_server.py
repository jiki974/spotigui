# -*- coding: utf-8 -*-
"""
OAuth callback server for handling Spotify OAuth redirects.
Runs a simple HTTP server to receive the authorization code.
"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from kivy.logger import Logger


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callbacks."""

    callback_code = None
    callback_received = threading.Event()

    def do_GET(self):
        """Handle GET request from OAuth redirect."""
        try:
            # Parse the URL to extract the authorization code
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            if 'code' in query_params:
                # Store the authorization code
                OAuthCallbackHandler.callback_code = query_params['code'][0]
                OAuthCallbackHandler.callback_received.set()

                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                success_html = """
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Authentication Successful</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #1DB954;">
                    <h1 style="color: white; font-size: 48px;">✓</h1>
                    <h2 style="color: white;">Authentication Successful!</h2>
                    <p style="color: white;">You can close this window and return to the app.</p>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode('utf-8'))
                Logger.info("OAuthServer: Authorization code received, authentication will complete shortly")
            elif 'error' in query_params:
                # Handle OAuth error
                error = query_params['error'][0]
                Logger.error(f"OAuthServer: OAuth error: {error}")

                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                error_html = f"""
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Authentication Failed</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #e22134;">
                    <h1 style="color: white; font-size: 48px;">✗</h1>
                    <h2 style="color: white;">Authentication Failed</h2>
                    <p style="color: white;">Error: {error}</p>
                    <p style="color: white;">Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode('utf-8'))
            else:
                # Unknown request - missing code parameter
                Logger.warning("OAuthServer: Received callback without 'code' parameter")
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                invalid_html = """
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Invalid Request</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #ffa500;">
                    <h1 style="color: white; font-size: 48px;">⚠</h1>
                    <h2 style="color: white;">Invalid OAuth Callback</h2>
                    <p style="color: white;">The authorization code was not found.</p>
                    <p style="color: white;">Please try scanning the QR code again.</p>
                </body>
                </html>
                """
                self.wfile.write(invalid_html.encode('utf-8'))

        except Exception as e:
            Logger.error(f"OAuthServer: Error handling request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_page = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <title>Server Error</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>Server Error</h1>
                <p>An error occurred while processing your request.</p>
            </body>
            </html>
            """
            self.wfile.write(error_page.encode('utf-8'))

    def log_message(self, format, *args):
        """Override to use Kivy logger instead of stderr."""
        Logger.debug(f"OAuthServer: {format % args}")


class OAuthCallbackServer:
    """OAuth callback server manager."""

    def __init__(self, port=8888):
        """
        Initialize OAuth callback server.

        Args:
            port: Port to listen on (default 8888 to match redirect URI)
        """
        self.port = port
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the callback server in a background thread."""
        if self.server_thread and self.server_thread.is_alive():
            Logger.warning("OAuthServer: Server already running")
            return

        # Reset the callback state
        OAuthCallbackHandler.callback_code = None
        OAuthCallbackHandler.callback_received.clear()

        try:
            self.server = HTTPServer(('', self.port), OAuthCallbackHandler)
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            Logger.info(f"OAuthServer: Started on port {self.port}")
        except Exception as e:
            Logger.error(f"OAuthServer: Failed to start server: {e}")
            raise

    def _run_server(self):
        """Run the server (called in background thread)."""
        try:
            self.server.serve_forever()
        except Exception as e:
            Logger.error(f"OAuthServer: Server error: {e}")

    def wait_for_callback(self, timeout=300):
        """
        Wait for OAuth callback to be received.

        Args:
            timeout: Maximum time to wait in seconds (default 300 = 5 minutes)

        Returns:
            Authorization code if received, None if timeout
        """
        if OAuthCallbackHandler.callback_received.wait(timeout):
            return OAuthCallbackHandler.callback_code
        return None

    def stop(self):
        """Stop the callback server."""
        if self.server:
            Logger.info("OAuthServer: Stopping server")
            self.server.shutdown()
            self.server = None
        if self.server_thread:
            self.server_thread.join(timeout=2)
            self.server_thread = None
