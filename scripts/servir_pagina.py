#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.server
import socketserver
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def main() -> None:
    parser = argparse.ArgumentParser(description="Sirve solo la pagina publica del manual ADE.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Sirviendo solo site/ en http://localhost:{args.port}/")
        print("Los archivos de data/raw no quedan publicados por este servidor.")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
