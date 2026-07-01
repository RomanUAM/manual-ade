#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python3 -m pip install -e .
python3 -m unittest discover -s tests -p 'test_*.py'
echo "HAG instalado en modo editable. Comandos: hag-ade, hag-ade-api"
