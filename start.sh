#!/bin/sh
# Rebuild the question banks from data/raw and start the app at http://localhost:5175
set -e
cd "$(dirname "$0")"
[ -d .venv ] || { python3 -m venv .venv && .venv/bin/pip install -q pymupdf requests; }
.venv/bin/python tools/build_banks.py
cd app
[ -d node_modules ] || npm install
npx vite --port 5175 --open
