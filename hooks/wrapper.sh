#!/bin/bash
# Thin wrapper that runs the latest version of a hook script from plugin cache.
# Usage: wrapper.sh <script_name> (e.g. wrapper.sh stop_tts.py)
# Installed to ~/.claude/hooks/simple-tts/ during setup — never needs updating.

SCRIPT="$1"
shift

# Find the script in plugin cache (latest version wins by directory sort)
FOUND=$(find ~/.claude/plugins/cache -path "*/simple-tts/*/hooks/$SCRIPT" 2>/dev/null | sort -V | tail -1)

if [ -z "$FOUND" ]; then
    # Fallback: try local copy (pre-update installs)
    DIR="$(dirname "$0")"
    if [ -f "$DIR/$SCRIPT" ]; then
        FOUND="$DIR/$SCRIPT"
    else
        exit 0
    fi
fi

exec python3 "$FOUND"
