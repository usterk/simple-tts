#!/usr/bin/env python3
"""
Claude Code Stop Hook - Speaks contextual TTS summary when Claude finishes.
Reads <!-- TTS: message --> from last_assistant_message or transcript.
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(__file__))
from tts_utils import extract_tts_from_transcript, speak, read_hook_input


def extract_tts_from_message(message):
    """Extract TTS tag directly from the last assistant message string."""
    if not message:
        return None
    match = re.search(r'<!--\s*TTS:\s*(.+?)\s*-->', message)
    return match.group(1).strip() if match else None


def main():
    input_data = read_hook_input()

    if input_data.get('stop_hook_active'):
        sys.exit(0)

    # Strategy 1: Try last_assistant_message (fastest)
    tts_text = extract_tts_from_message(input_data.get('last_assistant_message', ''))

    # Strategy 2: Fall back to transcript parsing
    if not tts_text:
        transcript_path = input_data.get('transcript_path')
        if transcript_path:
            tts_text = extract_tts_from_transcript(transcript_path)

    if not tts_text:
        tts_text = "Skończyłem"

    speak(tts_text)
    sys.exit(0)


if __name__ == '__main__':
    main()
