#!/usr/bin/env python3
"""Shared TTS utilities for Claude Code simple-tts plugin (usterk/simple-tts)"""

import json
import os
import re
import random
import subprocess
import sys
import time

# Config file location
CONFIG_PATH = os.path.expanduser("~/.claude/simple-tts-config.json")

DEFAULT_CONFIG = {
    "voice": "Krzysztof",
    "rate": 220,
    "name": "",
    "name_chance": 0.3,
}


def load_config():
    """Load plugin config, returning defaults if not found."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            stored = json.load(f)
        return {**DEFAULT_CONFIG, **stored}
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()


def extract_tts_from_transcript(transcript_path, search_lines=50):
    """
    Extract <!-- TTS: message --> tag from the last assistant message in transcript.
    """
    try:
        transcript_path = os.path.expanduser(transcript_path)
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        for line in reversed(lines[-search_lines:]):
            try:
                entry = json.loads(line)
                if entry.get('type') == 'assistant':
                    content = entry.get('message', {}).get('content', [])
                    if isinstance(content, list):
                        for block in content:
                            if block.get('type') == 'text':
                                match = re.search(
                                    r'<!--\s*TTS:\s*(.+?)\s*-->', block.get('text', '')
                                )
                                if match:
                                    return match.group(1).strip()
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        return None
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return None


def sanitize_for_polish_tts(text):
    """
    Make text pronounceable by Polish TTS voice.
    - ALL-CAPS words (2+ letters) get spelled out: "API" -> "A P I"
    - Common English terms get Polish phonetic equivalents
    """
    phonetic = {
        # Dev tools & platforms
        'cache': 'kesz',
        'docker': 'doker',
        'kubernetes': 'kubernetis',
        'nginx': 'en-gin-iks',
        'github': 'githab',
        'webpack': 'łebpak',
        'README': 'ridmi',
        'readme': 'ridmi',
        # Actions & concepts
        'deploy': 'deploj',
        'deployed': 'deplojd',
        'commit': 'komit',
        'committed': 'zakomitowany',
        'push': 'pusz',
        'pushed': 'wypuszony',
        'merge': 'merdż',
        'merged': 'zmerdżowany',
        'fetch': 'fecz',
        'checkout': 'czekałt',
        'rebase': 'ribejs',
        'rollback': 'rolbak',
        'refactor': 'refaktor',
        'build': 'bild',
        'release': 'rilis',
        # Architecture terms
        'queue': 'kju',
        'vue': 'wju',
        'node': 'nołd',
        'pipeline': 'pajplajn',
        'middleware': 'midłer',
        'endpoint': 'endpojnt',
        'runtime': 'rantajm',
        'webhook': 'łebhuk',
        'framework': 'frejmłork',
        'frontend': 'frontendł',
        'backend': 'bakend',
        'database': 'databejs',
        'cluster': 'klaster',
        'container': 'kontener',
        'microservice': 'mikroserwis',
        'repository': 'repozytorium',
        'branch': 'brancz',
        'pull request': 'pul rekłest',
        'code review': 'kod rewju',
        'worktree': 'łork-tri',
        'linter': 'linter',
        'debugger': 'debuger',
    }

    for eng, pol in phonetic.items():
        text = re.sub(re.escape(eng), pol, text, flags=re.IGNORECASE)

    # Spell out ALL-CAPS words (2+ letters)
    def spell_caps(m):
        return ' '.join(m.group(0))
    text = re.sub(r'\b[A-Z]{2,}\b', spell_caps, text)

    return text


LOCK_FILE = os.path.expanduser("~/.claude/simple-tts-last-speak")


def _recently_spoken(max_age=2.0):
    """Check if another hook spoke within the last max_age seconds."""
    try:
        mtime = os.path.getmtime(LOCK_FILE)
        return (time.time() - mtime) < max_age
    except OSError:
        return False


def _mark_spoken():
    """Mark that we just spoke (touch lock file)."""
    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(time.time()))
    except OSError:
        pass


def speak(text, priority=False):
    """
    Speak text using macOS say command with configured voice.
    Sanitizes English terms and optionally prepends user's name.

    priority=True (notification hook): kills any running say, always speaks.
    priority=False (stop hook): stays silent if notification just spoke.
    """
    # Debounce: if notification just spoke, stop hook should stay silent
    if not priority and _recently_spoken():
        return

    # Priority speaker kills any overlapping say process
    if priority:
        subprocess.run(['pkill', '-x', 'say'], capture_output=True)

    config = load_config()
    text = sanitize_for_polish_tts(text)

    name = config.get('name', '')
    if name and random.random() < config.get('name_chance', 0.3):
        if not text.lower().startswith(name.lower()):
            text = f"{name}, {text[0].lower() + text[1:]}" if len(text) > 1 else f"{name}, {text}"

    voice = config.get('voice', 'Krzysztof')
    rate = str(config.get('rate', 220))

    _mark_spoken()
    try:
        subprocess.run(['say', '-v', voice, '-r', rate, text], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"TTS error: {e}", file=sys.stderr)


def read_hook_input():
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
