"""
Serve ``index.html`` and answer its requests, with the standard library only.

Run it with ``python serve.py`` and open ``http://127.0.0.1:8000``. Set the environment
variable ``PORT`` to use a different port. The server listens only on this computer. Each
answer to an htmx request is a piece of HTML, and every value from the person is escaped
before it goes into that HTML. The server sends no data to another computer.
"""

from __future__ import annotations

import html
import http.server
import os
import pathlib
import urllib.parse

PAGE = pathlib.Path(__file__).with_name("index.html")
ADDRESS = ("127.0.0.1", int(os.environ.get("PORT", "8000")))


class Handler(http.server.BaseHTTPRequestHandler):
    """Answer the page and its htmx requests."""

    def answer(self, status: int, body: str) -> None:
        """Send one HTML answer."""
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        """Send the page."""
        if self.path == "/":
            self.answer(200, PAGE.read_text(encoding="utf-8"))
        else:
            self.answer(404, "This page does not exist. Open / to see the artifact.")

    def do_POST(self) -> None:
        """Answer the form with a greeting."""
        if self.path != "/greeting":
            self.answer(404, "This action does not exist.")
            return
        length = int(self.headers.get("Content-Length", "0"))
        fields = urllib.parse.parse_qs(self.rfile.read(length).decode())
        name = fields.get("name", [""])[0].strip()
        if name:
            self.answer(200, f"Hello, {html.escape(name)}.")
        else:
            self.answer(200, "The name is empty. Type a name and try again.")


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(ADDRESS, Handler) as server:
        print(f"Serving at http://{ADDRESS[0]}:{ADDRESS[1]} (press ctrl+c to stop)")
        server.serve_forever()
