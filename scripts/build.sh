#!/bin/bash
set -e

# Get script directory
SCRIPTS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"

DIST_DIR="$PROJECT_ROOT/dist"
KEY_FILE="$PROJECT_ROOT/key.pem"

# Ensure dist directory exists
mkdir -p "$DIST_DIR"

# Switch context to project root
cd "$PROJECT_ROOT"

# Run python pack script
# source is "." (project root)
# output is to dist/...
python3 "$SCRIPTS_DIR/pack_crx.py" . "$DIST_DIR/wikilink-helper-1.3.0.crx" --key "$KEY_FILE"

echo "Build successful!"
