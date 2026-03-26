# simple-tts

A [Claude Code](https://claude.ai/code) plugin that speaks short contextual summaries using macOS text-to-speech when Claude finishes a task or needs your attention.

Instead of switching to your terminal to check what Claude did, you just hear it: *"Poprawiłem parser zgodnie z wytycznymi"* or *"Potrzebuję zgody na uruchomienie migracji"*.

> **Requires macOS** — uses the built-in `say` command.

## Installation

```bash
# Add marketplace
/plugin marketplace add usterk/simple-tts

# Install
/plugin install simple-tts@usterk-simple-tts
```

Then run the interactive setup wizard:

```
/simple-tts-setup
```

The wizard will guide you through:
- Choosing a voice (default: **Krzysztof** — Polish, high quality)
- Setting your name for personalized greetings (optional, ~30% of messages)
- Choosing scope: global or project-only
- Testing the voice

## How it works

1. Claude adds a hidden `<!-- TTS: short summary -->` tag at the end of each response
2. When Claude **stops** or sends a **notification**, a hook extracts the tag and speaks it via `say`
3. English terms are automatically sanitized for non-English voices (acronyms get spelled out, common words get phonetic equivalents)

## Available voices

Run `say -v '?' | grep pl_PL` to see Polish voices on your system. Common options:

| Voice | Quality |
|-------|---------|
| Krzysztof | Enhanced |
| Ewa | Premium |
| Zosia | Standard / Enhanced |

## Commands

| Command | Description |
|---------|-------------|
| `/simple-tts-setup` | Interactive setup / reconfigure / uninstall |

## Configuration

Stored in `~/.claude/simple-tts-config.json`:

```json
{
  "voice": "Krzysztof",
  "name": "Paweł",
  "name_chance": 0.3
}
```

## Local development

```bash
claude --plugin-dir ./simple-tts
```

## License

MIT
