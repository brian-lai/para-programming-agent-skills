#!/usr/bin/env bash
set -euo pipefail
PYTHONDONTWRITEBYTECODE=1 python3 "$(dirname "$0")/install_pull_updates.py"
