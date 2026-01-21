import http.server
import socketserver
import os

PORT = 5173
STATIC_DIR = "idm_logger/static"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle /static/ prefix first
        if self.path.startswith('/static/'):
            # Strip /static/ to find file in STATIC_DIR
            # e.g. /static/assets/foo.js -> /assets/foo.js
            self.path = self.path.replace('/static/', '/', 1)

        # Handle root or SPA fallback (if not a file)
        # Check if path has extension
        if '.' not in os.path.basename(self.path):
             self.path = '/index.html'

        super().do_GET()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
