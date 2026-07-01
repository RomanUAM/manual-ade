from __future__ import annotations

import argparse
import json
from pathlib import Path

from .director import HAGDirector


def root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.root).expanduser().resolve()


def cmd_init(args: argparse.Namespace) -> None:
    director = HAGDirector(root_from_args(args))
    kb = director.init()
    print(f"Base HAG inicializada: {kb.path.relative_to(director.root)}")


def cmd_build(args: argparse.Namespace) -> None:
    director = HAGDirector(root_from_args(args))
    result = director.build()
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if result.status == "fail":
        raise SystemExit(2)


def cmd_audit(args: argparse.Namespace) -> None:
    director = HAGDirector(root_from_args(args))
    result = director.audit()
    director.write_audit(result)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if result.status == "fail":
        raise SystemExit(2)


def cmd_status(args: argparse.Namespace) -> None:
    director = HAGDirector(root_from_args(args))
    nodes = list(director.kb.nodes.values())
    print(f"Nodos: {len(nodes)}")
    for node in nodes:
        print(f"- {node.id}: {node.title} ({len(node.artifacts)} artefactos registrados)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI del sistema HAG")
    parser.add_argument("--root", default=".", help="Raiz del proyecto")
    sub = parser.add_subparsers(required=True)
    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("build").set_defaults(func=cmd_build)
    sub.add_parser("audit").set_defaults(func=cmd_audit)
    sub.add_parser("status").set_defaults(func=cmd_status)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
