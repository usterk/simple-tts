# simple-tts

A [Claude Code](https://claude.ai/code) plugin that speaks short contextual summaries using macOS text-to-speech when Claude finishes a task or needs your attention.

Instead of switching to your terminal to check what Claude did, you just hear it: *"Fixed the auth module as requested"* or *"Need your approval to run migration"*.

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
- Choosing a TTS voice (any voice available on your macOS)
- Setting your name for personalized greetings (optional, ~30% of messages)
- Choosing scope: global or project-only
- Testing the voice

## How it works

1. The plugin adds a CLAUDE.md instruction telling Claude to include a hidden `<!-- TTS: short summary -->` tag at the end of each response
2. When Claude **stops** or sends a **notification**, a hook extracts the tag and speaks it via macOS `say`
3. Foreign terms are automatically sanitized for the chosen voice — acronyms get spelled out (`API` → `A P I`), common English words get phonetic equivalents

### Examples

What Claude writes in the response (invisible to the user):

```html
<!-- TTS: Fixed the parser according to your guidelines -->
<!-- TTS: Found a bug in the auth module -->
<!-- TTS: Tests pass, can I commit? -->
<!-- TTS: Need your approval to run the deploy script -->
```

What you hear when you're in another window:

> *"Fixed the parser according to your guidelines"*

or sometimes:

> *"Sarah, found a bug in the auth module"*

## Available voices

Run `say -v '?'` to see all voices on your system. The setup wizard will show voices for your locale. Some examples:

| Voice | Language | Quality |
|-------|----------|---------|
| Samantha | English (US) | Enhanced |
| Daniel | English (UK) | Enhanced |
| Krzysztof | Polish | Enhanced |
| Ewa | Polish | Premium |
| Thomas | French | Enhanced |
| Anna | German | Enhanced |

## Commands

| Command | Description |
|---------|-------------|
| `/simple-tts-setup` | Interactive setup / reconfigure / uninstall |

## Configuration

Stored in `~/.claude/simple-tts-config.json`:

```json
{
  "voice": "Samantha",
  "name": "Sarah",
  "name_chance": 0.3
}
```

## Phonetic sanitization

The plugin includes a sanitizer that makes technical terms pronounceable by non-English TTS voices:

| Original | Sanitized |
|----------|-----------|
| `API` | `A P I` (spelled out) |
| `GOPATH` | `G O P A T H` |
| `cache` | `kesz` |
| `docker` | `doker` |
| `kubernetes` | `kubernetis` |
| `webhook` | `łebhuk` |

You can extend the phonetic dictionary in `hooks/tts_utils.py`.

## Local development

```bash
claude --plugin-dir ./simple-tts
```

## License

MIT
