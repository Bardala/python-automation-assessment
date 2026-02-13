"""Fingerprint Recorder — Captures your REAL browser's fingerprint for replay.

Run this script, it will serve a local HTML page. Open it in your REAL Chrome
browser (not automated), and your fingerprint will be captured and saved.
"""

import json
import os
import http.server
import threading

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

RECORDER_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Fingerprint Recorder</title>
    <style>
        body { font-family: monospace; padding: 20px; background: #1a1a2e; color: #e0e0e0; }
        h1 { color: #0f3460; }
        pre { background: #16213e; padding: 15px; border-radius: 8px; overflow: auto; max-height: 500px; }
        .status { font-size: 1.4em; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .recording { background: #e94560; color: white; }
        .done { background: #0f3460; color: white; }
    </style>
</head>
<body>
    <h1>🔍 Browser Fingerprint Recorder</h1>
    <div id="status" class="status recording">⏳ Recording fingerprint...</div>
    <pre id="output"></pre>

    <script>
    async function collectFingerprint() {
        const fp = {};

        // Navigator properties
        fp.userAgent = navigator.userAgent;
        fp.platform = navigator.platform;
        fp.language = navigator.language;
        fp.languages = Array.from(navigator.languages);
        fp.hardwareConcurrency = navigator.hardwareConcurrency;
        fp.maxTouchPoints = navigator.maxTouchPoints;
        fp.vendor = navigator.vendor;
        fp.appVersion = navigator.appVersion;
        fp.doNotTrack = navigator.doNotTrack;
        fp.cookieEnabled = navigator.cookieEnabled;
        fp.deviceMemory = navigator.deviceMemory || null;
        fp.pdfViewerEnabled = navigator.pdfViewerEnabled;

        // Screen properties
        fp.screen = {
            width: screen.width,
            height: screen.height,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            colorDepth: screen.colorDepth,
            pixelDepth: screen.pixelDepth
        };
        fp.devicePixelRatio = window.devicePixelRatio;

        // Timezone
        fp.timezoneOffset = new Date().getTimezoneOffset();
        fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // WebGL
        try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                fp.webgl = {
                    vendor: gl.getParameter(debugInfo ? debugInfo.UNMASKED_VENDOR_WEBGL : gl.VENDOR),
                    renderer: gl.getParameter(debugInfo ? debugInfo.UNMASKED_RENDERER_WEBGL : gl.RENDERER),
                    version: gl.getParameter(gl.VERSION),
                    shadingLanguageVersion: gl.getParameter(gl.SHADING_LANGUAGE_VERSION),
                };
            }
        } catch(e) {
            fp.webgl = null;
        }

        // Plugins
        fp.plugins = [];
        for (let i = 0; i < navigator.plugins.length; i++) {
            fp.plugins.push({
                name: navigator.plugins[i].name,
                description: navigator.plugins[i].description,
                filename: navigator.plugins[i].filename,
            });
        }

        // Media devices count (no details for privacy)
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            fp.mediaDevices = {
                audioinput: devices.filter(d => d.kind === 'audioinput').length,
                videoinput: devices.filter(d => d.kind === 'videoinput').length,
                audiooutput: devices.filter(d => d.kind === 'audiooutput').length,
            };
        } catch(e) {
            fp.mediaDevices = null;
        }

        // Chrome-specific properties
        fp.hasChrome = typeof window.chrome !== 'undefined';
        fp.hasChromeRuntime = typeof window.chrome !== 'undefined' && typeof window.chrome.runtime !== 'undefined';

        // webdriver flag
        fp.webdriver = navigator.webdriver;

        // Connection info
        if (navigator.connection) {
            fp.connection = {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt,
            };
        }

        // Permissions API
        fp.permissions = {};
        try {
            const perms = ['geolocation', 'notifications', 'camera', 'microphone'];
            for (const perm of perms) {
                try {
                    const result = await navigator.permissions.query({name: perm});
                    fp.permissions[perm] = result.state;
                } catch(e) {}
            }
        } catch(e) {}

        return fp;
    }

    collectFingerprint().then(fp => {
        document.getElementById('output').textContent = JSON.stringify(fp, null, 2);
        document.getElementById('status').className = 'status done';
        document.getElementById('status').textContent = '✅ Fingerprint captured! Sending to server...';

        // Send to local server
        fetch('/save-fingerprint', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(fp)
        }).then(r => r.json()).then(resp => {
            document.getElementById('status').textContent =
                '✅ Fingerprint saved to ' + resp.path + '! You can close this tab.';
        }).catch(err => {
            document.getElementById('status').textContent =
                '⚠️ Could not send to server. Copy the JSON above manually.';
        });
    });
    </script>
</body>
</html>"""


class FingerprintHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP handler to serve the recorder page and save the fingerprint."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(RECORDER_HTML.encode())

    def do_POST(self):
        if self.path == "/save-fingerprint":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))

            os.makedirs(OUTPUT_DIR, exist_ok=True)
            path = os.path.join(OUTPUT_DIR, "fingerprint.json")
            with open(path, "w") as f:
                json.dump(data, f, indent=2)

            print(f"\n✅ Fingerprint saved to {path}")
            print(f"   User-Agent: {data.get('userAgent', 'N/A')}")
            print(f"   Platform: {data.get('platform', 'N/A')}")
            print(f"   WebGL: {data.get('webgl', {}).get('renderer', 'N/A')}")
            print(f"   webdriver: {data.get('webdriver', 'N/A')}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"path": path}).encode())

    def log_message(self, format, *args):
        pass  # Suppress default HTTP logging


def main():
    port = 8787
    server = http.server.HTTPServer(("127.0.0.1", port), FingerprintHandler)

    print("=" * 50)
    print("🔍 FINGERPRINT RECORDER")
    print("=" * 50)
    print(f"\n👉 Open this URL in your REAL Chrome browser:\n")
    print(f"   http://localhost:{port}\n")
    print("The fingerprint will be captured automatically.")
    print("Press Ctrl+C to stop the server.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
