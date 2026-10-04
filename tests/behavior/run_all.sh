#!/usr/bin/env bash
# Offline deterministic machinery tests; never invokes a model host.
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 -m unittest discover -s tests/behavior -p 'test_*.py'
