"""
BD Modern School - Fast Local Dev Server
-----------------------------------------
Adds gzip compression, aggressive Cache-Control headers,
ETag support, and threading for parallel requests.

Run: python fast_server.py
"""

import gzip
import hashlib
import io
import mimetypes
import os
import socket
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Files cached long-term (images, fonts)
LONG_CACHE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
                   ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".webm"}

# Minimum byte size to bother gzipping
GZIP_MIN_SIZE = 860

# MIME types eligible for compression
COMPRESSIBLE_TYPES = {
    "text/html", "text/css", "text/javascript", "application/javascript",
    "application/json", "text/plain", "image/svg+xml", "application/xml",
    "text/xml"
}


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


class FastHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Vary", "Accept-Encoding")
        super().end_headers()

    def do_GET(self):
        path = self.translate_path(self.path)

        # SPA fallback: serve index.html for unknown routes
        if not os.path.exists(path) or os.path.isdir(path):
            index = os.path.join(DIRECTORY, "index.html")
            if os.path.exists(index):
                path = index
            else:
                self.send_error(404)
                return

        # Read raw file bytes
        try:
            with open(path, "rb") as f:
                content = f.read()
        except OSError:
            self.send_error(404)
            return

        # MIME type
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        # ETag from MD5
        etag = '"' + hashlib.md5(content).hexdigest() + '"'

        # 304 Not Modified shortcut
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", self._cache_control(path))
            self.end_headers()
            return

        # Gzip if client supports it and content type is compressible
        base_mime = mime_type.split(";")[0].strip()
        accepts_gzip = "gzip" in self.headers.get("Accept-Encoding", "")
        should_gzip = (
            accepts_gzip
            and base_mime in COMPRESSIBLE_TYPES
            and len(content) >= GZIP_MIN_SIZE
        )

        if should_gzip:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
                gz.write(content)
            send_content = buf.getvalue()
            ratio = round(len(send_content) / len(content) * 100)
        else:
            send_content = content
            ratio = 100

        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(send_content)))
        self.send_header("ETag", etag)
        self.send_header("Cache-Control", self._cache_control(path))
        if should_gzip:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        self.wfile.write(send_content)

    def _cache_control(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in LONG_CACHE_EXTS:
            return "public, max-age=604800"   # 7 days for images/fonts
        elif ext == ".html":
            return "no-cache"                  # Always revalidate HTML
        elif ext in {".js", ".css", ".json"}:
            return "public, max-age=3600"      # 1 hour for scripts
        return "public, max-age=86400"

    def log_message(self, fmt, *args):
        # Compact, readable log — skip favicon noise
        try:
            line = fmt % args
            if "favicon" in line:
                return
            status = args[1] if len(args) > 1 else "?"
            req = args[0] if args else ""
            try:
                file_path = req.split('"')[1].split(" ")[1]
            except Exception:
                file_path = req
            sys.stdout.buffer.write(f"  {status}  {file_path}\n".encode("utf-8"))
            sys.stdout.buffer.flush()
        except Exception:
            pass


class ThreadedHTTPServer(HTTPServer):
    """Serve each request in its own daemon thread."""
    def process_request(self, request, client_address):
        t = threading.Thread(
            target=self._handle_request,
            args=(request, client_address),
            daemon=True
        )
        t.start()

    def _handle_request(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            pass
        finally:
            self.shutdown_request(request)


if __name__ == "__main__":
    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("image/webp", ".webp")
    mimetypes.add_type("application/manifest+json", ".json")
    mimetypes.add_type("application/vnd.android.package-archive", ".apk")

    server = ThreadedHTTPServer(("", PORT), FastHandler)
    lan_ip = get_lan_ip()

    print(f"\n  BD Modern School -- Fast Dev Server")
    print(f"  " + "-" * 40)
    print(f"  Local   : http://localhost:{PORT}")
    print(f"  Network : http://{lan_ip}:{PORT}  (mobile on same Wi-Fi)")
    print(f"  " + "-" * 40)
    print(f"  [OK] Gzip compression (HTML: ~120KB vs 550KB raw)")
    print(f"  [OK] ETag + Cache-Control (repeat visits = near instant)")
    print(f"  [OK] Threaded -- parallel requests, no blocking")
    print(f"  [OK] Keep-Alive connections\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()
