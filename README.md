# spotigui
A multiplatform spotify client to control any spotify devices

## OAuth Authentication with Cloudflare Tunnel

For touchscreen devices without keyboard, the app uses QR code authentication with Cloudflare Tunnel to receive OAuth callbacks.

### Setup

1. **Install Cloudflare Tunnel (cloudflared)**
   ```bash
   # macOS
   brew install cloudflare/cloudflare/cloudflared

   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Start the tunnel** (forwards external traffic to local port 8888)
   ```bash
   cloudflared tunnel --url http://localhost:8888
   ```

   This will output a public URL like: `https://random-name.trycloudflare.com`

3. **Update Spotify App Settings**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click on your app
   - Click "Edit Settings"
   - Under "Redirect URIs", add: `https://your-tunnel-url.trycloudflare.com/callback`
   - **IMPORTANT**: Click "Add" and then "Save" at the bottom
   - Verify the URI appears in the list

4. **Update Environment Variable**
   Create/update `.env` file with the **EXACT SAME URL**:
   ```bash
   SPOTIFY_REDIRECT_URI=https://your-tunnel-url.trycloudflare.com/callback
   ```

   **⚠️ Critical:** The redirect URI in `.env` must EXACTLY match the one in Spotify Dashboard (including https/http, trailing slashes, etc.)

5. **Run the app**
   ```bash
   python -m spotigui.main
   ```

   Scan the QR code on your phone, authorize the app, and authentication will complete automatically!
