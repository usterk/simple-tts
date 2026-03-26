#!/usr/bin/env python3
"""Shared TTS utilities for Claude Code simple-tts plugin"""

import json
import os
import re
import random
import subprocess
import sys

# Config file location
CONFIG_PATH = os.path.expanduser("~/.claude/simple-tts-config.json")

DEFAULT_CONFIG = {
    "voice": "Krzysztof",
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
        'cache': 'kesz',
        'docker': 'doker',
        'kubernetes': 'kubernetis',
        'nginx': 'en-gin-iks',
        'queue': 'kju',
        'vue': 'wju',
        'node': 'nołd',
        'webpack': 'łebpak',
        'github': 'githab',
        'pipeline': 'pajplajn',
        'middleware': 'midłer',
        'endpoint': 'endpojnt',
        'runtime': 'rantajm',
        'webhook': 'łebhuk',
        'deploy': 'deploj',
        'framework': 'frejmłork',
        'README': 'ridmi',
        'readme': 'ridmi',
    }

    for eng, pol in phonetic.items():
        text = re.sub(re.escape(eng), pol, text, flags=re.IGNORECASE)

    # Spell out ALL-CAPS words (2+ letters)
    def spell_caps(m):
        return ' '.join(m.group(0))
    text = re.sub(r'\b[A-Z]{2,}\b', spell_caps, text)

    return text


def speak(text):
    """
    Speak text using macOS say command with configured voice.
    Sanitizes English terms and optionally prepends user's name.
    """
    config = load_config()
    text = sanitize_for_polish_tts(text)

    name = config.get('name', '')
    if name and random.random() < config.get('name_chance', 0.3):
        if not text.lower().startswith(name.lower()):
            text = f"{name}, {text[0].lower() + text[1:]}" if len(text) > 1 else f"{name}, {text}"

    voice = config.get('voice', 'Krzysztof')
    try:
        subprocess.run(['say', '-v', voice, text], check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"TTS error: {e}", file=sys.stderr)


def read_hook_input():
    """Read and parse JSON input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
