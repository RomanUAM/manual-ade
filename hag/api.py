from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .director import HAGDirector


class HAGRequestHandler(BaseHTTPRequestHandler):
    director: HAGDirector

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self.send_json(200, {"status": "ok", "service": "hag"})
            return
        if path == "/nodes":
            nodes = [node.to_dict() for node in self.director.kb.nodes.values()]
            self.send_json(200, {"nodes": nodes})
            return
        if path == "/audit":
            result = self.director.audit()
            self.send_json(200 if result.status == "pass" else 409, result.to_dict())
            return
        self.send_json(404, {"error": "ruta no encontrada"})


def run_server(root: Path, host: str, port: int) -> None:
    HAGRequestHandler.director = HAGDirector(root)
    server = ThreadingHTTPServer((host, port), HAGRequestHandler)
    print(f"API HAG en http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="API REST local del HAG")
    parser.add_argument("--root", default=".")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    run_server(Path(args.root).expanduser().resolve(), args.host, args.port)


if __name__ == "__main__":
    main()
