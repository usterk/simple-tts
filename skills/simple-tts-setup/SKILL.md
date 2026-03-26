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

Group voices by language. Detect the user's system language from the `LANG` environment variable (e.g. `pl_PL` → Polish, `en_US` → English, `de_DE` → German). Use that as the default language.

Present ALL questions at once:

> **Simple TTS Setup**
>
> Available voices on your system:
> {show voices grouped by language, highlight the detected default language}
>
> Please answer these questions (press Enter to accept defaults):
>
> 1. **Language** [**{detected, e.g. Polish}**]: _language for TTS messages_
> 2. **Voice** [**{best voice for chosen language}**]: _which voice to use?_
> 3. **Speed** [**250**]: _words per minute (200=normal, 250=slightly faster, 300=fast)_
> 4. **Your name** [**skip**]: _optional — Claude will sometimes greet you by name (~30% of messages)_
> 5. **Scope** [**global**]: _"global" (all projects) or "project" (this project only)_
> 6. **Preview?** [**no**]: _say "yes" to hear a sample with your chosen settings_

Default voice per language (pick the highest quality available):
- Polish: Krzysztof (Enhanced) or Ewa (Premium)
- English: Samantha (Enhanced) or Daniel
- German: Anna (Enhanced)
- French: Thomas (Enhanced)
- For other languages, pick the first Enhanced/Premium voice available

Wait for the user's single response.

## Step 4: Apply configuration

Based on choices, do ALL of these in one step:

**4a. Install wrapper script to ~/.claude/hooks/simple-tts/**

The wrapper is a thin shell script that always runs the latest version of hook scripts from the plugin cache. This means `plugin update` automatically updates the hooks — no re-setup needed.

```bash
mkdir -p ~/.claude/hooks/simple-tts
```

Find and copy only the wrapper:
```bash
WRAPPER=$(find ~/.claude/plugins/cache -path '*/simple-tts/*/hooks/wrapper.sh' 2>/dev/null | sort -V | tail -1)
if [ -n "$WRAPPER" ]; then
  cp "$WRAPPER" ~/.claude/hooks/simple-tts/wrapper.sh
  chmod +x ~/.claude/hooks/simple-tts/wrapper.sh
fi
```

If the plugin cache is not found (e.g. using --plugin-dir), look in the source directory for wrapper.sh instead.

**4b. Preview (if requested)**

If the user said "yes" to preview, run:
```bash
say -v "<voice>" -r <rate> "This is how I will sound. Testing one two three."
```
Use a sentence in the chosen language. After preview, ask: "Sound good? (Enter=yes, or adjust voice/speed)"
If user wants changes, go back to questions.

**4c. Save config file** `~/.claude/simple-tts-config.json`:
```json
{
  "voice": "<chosen>",
  "rate": <chosen rate, default 250>,
  "language": "<chosen language>",
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
            "command": "~/.claude/hooks/simple-tts/wrapper.sh stop_tts.py",
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
            "command": "~/.claude/hooks/simple-tts/wrapper.sh notification_tts.py",
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

If not present, **APPEND** (never overwrite existing content!) a block adapted to the chosen language.

Use this template, replacing `{language}` and `{examples}` based on user's language choice:

```
- Add `<!-- TTS: short message in {language} -->` tag at the end of your response when:
  1. Completing a task (what you did in context of user's request)
  2. Before user interaction (what you need or found)
  - This tag is read aloud to the user via macOS TTS so they can switch console knowing the gist of your response without reading it. It must be a natural, spoken-language summary — short enough to hear in a few seconds, specific enough to be useful.
  - Max 10 words, in {language}, contextual to the user's last message
  - Examples: {examples}
  - NEVER generic — always relate to what was actually done or needed
  - TTS voice is {gender} — use {gender_grammar_rule}
  - TTS voice may mispronounce foreign words. Rules:
    - Prefer {language} descriptions over English acronyms or jargon
    - If a technical name MUST appear, use phonetic spelling readable by the TTS voice
    - NEVER put acronyms (API, GOPATH, JSON, URL) in the TTS tag — describe what they are instead
```

**Gender and grammar rules** — determine from the chosen voice name:

Known male voices: Krzysztof, Daniel, Thomas, Alex, Jorge, Luca
Known female voices: Ewa, Zosia, Samantha, Anna, Amélie, Monica

`{gender}` = "male" or "female"
`{gender_grammar_rule}` depends on language:
- **Polish**: male → "masculine verb forms (zrobiłem, znalazłem, naprawiłem)", female → "feminine verb forms (zrobiłam, znalazłam, naprawiłam)"
- **German**: male → "masculine forms where applicable", female → "feminine forms where applicable"
- **English/French**: "no grammatical gender adjustment needed"
- For unknown voices, default to masculine

Example values per language:
- **Polish (male)**: `"Poprawiłem parser zgodnie z wytycznymi", "Znalazłem błąd w module auth", "Testy przechodzą, mogę commitować?", "Potrzebuję zgody na uruchomienie migracji"`
- **Polish (female)**: `"Poprawiłam parser zgodnie z wytycznymi", "Znalazłam błąd w module auth", "Testy przechodzą, mogę commitować?", "Potrzebuję zgody na uruchomienie migracji"`
- **English**: `"Fixed the parser as requested", "Found a bug in auth module", "Tests pass, can I commit?", "Need your approval to run migration"`
- **German**: `"Parser wie gewünscht korrigiert", "Fehler im Auth-Modul gefunden", "Tests bestanden, soll ich committen?", "Brauche Genehmigung für Migration"`
- **French**: `"Parseur corrigé comme demandé", "Bug trouvé dans le module auth", "Tests réussis, je commit?", "Besoin d'approbation pour la migration"`
- For other languages, translate the English examples into the chosen language.

## Step 5: Test

```bash
say -v "<voice>" -r <rate> "Setup complete!"
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
