#!/usr/bin/env python3
"""
Claude Code Notification Hook - Speaks contextual message when user attention is needed.
Tries TTS tag from transcript first, falls back to translated notification.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from tts_utils import extract_tts_from_transcript, speak, read_hook_input


def translate_notification(message):
    """Translate common notification messages to Polish."""
    if not message:
        return "Potrzebuję Twojej uwagi"

    msg = message.lower()
    if 'permission' in msg:
        return "Potrzebuję zgody"
    if 'waiting' in msg or 'input' in msg:
        return "Czekam na odpowiedź"
    if 'error' in msg or 'failed' in msg:
        return "Wystąpił problem"
    return "Potrzebuję Twojej uwagi"


def main():
    input_data = read_hook_input()

    # Try contextual TTS tag from transcript first
    transcript_path = input_data.get('transcript_path')
    tts_text = None
    if transcript_path:
        tts_text = extract_tts_from_transcript(transcript_path)

    if not tts_text:
        tts_text = translate_notification(input_data.get('message', ''))

    speak(tts_text)
    sys.exit(0)


if __name__ == '__main__':
    main()
