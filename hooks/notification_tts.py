#!/usr/bin/env python3
"""
Claude Code Notification Hook - Speaks short message when user attention is needed.
Always uses the notification message directly (not transcript TTS tag,
which belongs to the previous response, not the current permission request).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from tts_utils import speak, read_hook_input


def translate_notification(message):
    """Produce a short spoken notification."""
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
    tts_text = translate_notification(input_data.get('message', ''))
    speak(tts_text)
    sys.exit(0)


if __name__ == '__main__':
    main()
