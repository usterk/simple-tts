# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Claude Code plugin that uses macOS `say` to speak short TTS summaries when Claude finishes a task or needs user attention. Distributed via the `usterk/simple` marketplace.

## Architecture

- **hooks/tts_utils.py** — shared module: config loading (`~/.claude/simple-tts-config.json`), phonetic sanitization (English→Polish-readable), `speak()` function, transcript TTS tag extraction
- **hooks/stop_tts.py** — Stop hook: extracts `<!-- TTS: message -->` from `last_assistant_message` (preferred) or transcript fallback. Stays silent if no tag found (permission prompts are handled by notification hook)
- **hooks/notification_tts.py** — Notification hook: translates Claude Code notification messages to short spoken phrases. Never reads transcript (avoids repeating stale messages)
- **skills/simple-tts-setup/SKILL.md** — Interactive setup wizard (`/simple-tts-setup`): configures voice, language, name, scope; copies hooks to `~/.claude/hooks/simple-tts/`; appends TTS instruction to CLAUDE.md
- **.claude-plugin/plugin.json** — plugin manifest (version auto-bumped by CI)

## Key design decisions

- A thin **wrapper.sh** is copied to `~/.claude/hooks/simple-tts/` during setup. It dynamically finds and runs the latest hook scripts from the plugin cache, so `plugin update` automatically uses new code without re-running setup
- Stop hook only speaks when a `<!-- TTS: -->` tag exists — silence means Claude stopped for a permission prompt, and the notification hook handles that
- Phonetic dictionary in `tts_utils.py` sanitizes English terms for non-English TTS voices (e.g. `push` → `pusz`, ALL-CAPS get spelled out letter by letter)

## CI/CD

Every push to `main` triggers `.github/workflows/bump-version.yml`:
1. Determines bump type from commit message prefix: `feat:` → minor, `feat!:`/`breaking` → major, everything else → patch
2. Bumps version in `plugin.json`, commits with `[skip ci]`, creates git tag
3. Sends `repository_dispatch` to `usterk/simple` marketplace to update version and `ref`

**Commit message conventions**: prefix with `feat:` for minor bump, `feat!:` or `breaking` for major. No prefix = patch.

## Local testing

```bash
claude --plugin-dir .
```
