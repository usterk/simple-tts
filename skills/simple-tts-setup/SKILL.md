---
description: "Interactive setup wizard for simple-tts plugin. Configures macOS text-to-speech notifications for Claude Code. Also handles uninstall."
user_invocable: true
---

# Simple TTS Setup

You are running an interactive setup wizard for the **simple-tts** plugin. Guide the user through configuration step by step, proposing sensible defaults they can accept with Enter.

IMPORTANT: Gather ALL choices first (steps 1-5), then apply everything at once (step 6). Do NOT stop between questions to wait — ask all questions in a single response, each on its own line. The user will answer all at once or press Enter to accept defaults.

## Step 1: Platform check

```bash
uname -s
```

If NOT `Darwin`:
> This plugin requires **macOS** (uses the system `say` command). It won't work on your system.

Stop here.

## Step 2: Check if already configured

Read `~/.claude/simple-tts-config.json` if it exists. If it does, show current config and ask:

> Simple TTS is already configured:
> - Voice: **{voice}**
> - Name: **{name}** (or: not set)
>
> What would you like to do?
> 1. Reconfigure
> 2. Uninstall
> 3. Cancel

If user picks uninstall → go to **Uninstall** section below.
If user picks cancel → stop.
Otherwise continue with reconfiguration.

If not yet configured, proceed to step 3.

## Step 3: Detect available voices

```bash
say -v '?' 2>/dev/null
```

Show voices relevant to the user's locale and present ALL questions at once:

> **Simple TTS Setup**
>
> Available voices on your system:
> {show relevant voices grouped by language}
>
> Please answer these questions (press Enter to accept defaults):
>
> 1. **Voice** [**Krzysztof**]: _which voice to use?_
> 2. **Your name** [**skip**]: _optional — Claude will sometimes greet you by name (~30% of messages)_
> 3. **Scope** [**global**]: _"global" (all projects) or "project" (this project only)_

Wait for the user's single response.

## Step 4: Apply configuration

Based on choices, do ALL of these in one step:

**4a. Copy hook scripts to ~/.claude/hooks/simple-tts/**

Create directory `~/.claude/hooks/simple-tts/` and copy the 3 Python files from the plugin:

```bash
mkdir -p ~/.claude/hooks/simple-tts
```

Then find the plugin's hooks directory in the plugin cache and copy:
```bash
PLUGIN_HOOKS=$(find ~/.claude/plugins -path '*/simple-tts/*/hooks/tts_utils.py' -print -quit 2>/dev/null)
if [ -n "$PLUGIN_HOOKS" ]; then
  PLUGIN_DIR=$(dirname "$PLUGIN_HOOKS")
  cp "$PLUGIN_DIR/tts_utils.py" "$PLUGIN_DIR/stop_tts.py" "$PLUGIN_DIR/notification_tts.py" ~/.claude/hooks/simple-tts/
fi
```

If the plugin cache is not found (e.g. using --plugin-dir), look in the current plugin source directory instead.

**4b. Save config file** `~/.claude/simple-tts-config.json`:
```json
{
  "voice": "<chosen>",
  "name": "<name or empty string>",
  "name_chance": 0.3
}
```

**4c. Add hooks to settings.json**

Use the `update-config` skill or edit directly. The target settings.json depends on scope:
- Global: `~/.claude/settings.json`
- Project: `.claude/settings.json`

Add these hooks (merge with existing hooks, don't overwrite):

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/simple-tts/stop_tts.py",
            "timeout": 5000
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/simple-tts/notification_tts.py",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

IMPORTANT: If hooks already exist for Stop or Notification with paths containing "simple-tts" or "tts", update them in place. Do NOT duplicate. If other non-TTS hooks exist, preserve them.

**4d. Add CLAUDE.md instruction**

Target file based on scope:
- Global: `~/.claude/CLAUDE.md`
- Project: `CLAUDE.md` in project root

First READ the existing file (if any). Check if it already contains `<!-- TTS:` instruction. If yes, skip this step and tell the user it's already there.

If not present, **APPEND** (never overwrite existing content!) this block:

```
- Add `<!-- TTS: short message -->` tag at the end of your response when:
  1. Completing a task (what you did in context of user's request)
  2. Before user interaction (what you need or found)
  - This tag is read aloud to the user via macOS TTS so they can switch console knowing the gist of your response without reading it. It must be a natural, spoken-language summary — short enough to hear in a few seconds, specific enough to be useful.
  - Max 10 words, contextual to the user's last message
  - Examples: "Fixed the parser as requested", "Found a bug in auth module", "Tests pass, can I commit?", "Need your approval to run migration"
  - NEVER generic ("Task complete") — always relate to what was actually done or needed
  - TTS voice may mispronounce foreign words. Rules:
    - Prefer descriptions over acronyms or jargon when possible
    - If a technical name MUST appear, use phonetic spelling readable by the TTS voice
    - NEVER put acronyms (API, GOPATH, JSON, URL) in the TTS tag — describe what they are instead
```

## Step 5: Test

```bash
say -v "<voice>" "Setup complete!"
```

## Step 6: Done

> **Simple TTS configured!**
>
> From the next session, Claude will speak short summaries when:
> - finishing a task
> - needing your attention
>
> To reconfigure: `/simple-tts-setup`
> To uninstall: `/simple-tts-setup` → Uninstall

---

## Uninstall

**Step 1:** Ask scope: "Remove globally, from project, or both?"

**Step 2:**
- Remove the TTS instruction block from the appropriate CLAUDE.md. The block starts with `- Add \`<!-- TTS:` and ends before the next line starting with `- ` at the same indent level (or end of file). Be careful to only remove the TTS block, not other content.
- Remove `~/.claude/simple-tts-config.json`
- Remove hooks from settings.json that reference `simple-tts`
- Remove `~/.claude/hooks/simple-tts/` directory

**Step 3:** Tell user:
> Simple TTS removed.
> You can also disable the plugin: `claude plugin disable simple-tts`
> To re-enable: `/simple-tts-setup`
