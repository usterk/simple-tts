---
description: "Interactive setup wizard for simple-tts plugin. Configures macOS text-to-speech notifications for Claude Code. Also handles uninstall."
user_invocable: true
---

# Simple TTS Setup

You are running an interactive setup wizard for the **simple-tts** plugin. Guide the user through configuration step by step, proposing sensible defaults they can accept with Enter.

## Step 1: Platform check

```bash
uname -s
```

If NOT `Darwin`:
> ⚠️ Ten plugin wymaga **macOS** (używa systemowej komendy `say`). Na Twoim systemie nie zadziała.

Stop here.

## Step 2: Check if already configured

Read `~/.claude/simple-tts-config.json` if it exists. If it does, show current config and ask:

> Simple TTS jest już skonfigurowany:
> - Głos: **{voice}**
> - Imię: **{name}** (lub: nie ustawione)
>
> Co chcesz zrobić?
> 1. Zmienić konfigurację
> 2. Odinstalować
> 3. Anulować

If user picks uninstall → go to **Uninstall** section below.
If user picks cancel → stop.
Otherwise continue with reconfiguration.

## Step 3: Detect available voices

```bash
say -v '?' | grep -E 'pl_PL|en_US|en_GB' | head -20
```

Show the Polish voices and present the choice:

> 🎤 Dostępne głosy polskie:
> {list voices}
>
> Wybierz głos [**Krzysztof**]:

If user presses Enter / says nothing specific → use "Krzysztof".
Validate the chosen voice exists in the output. If not, warn and re-ask.

## Step 4: User's name

> Chcesz, żeby Claude czasem zwracał się do Ciebie po imieniu?
> Podaj imię lub zostaw puste [**pomiń**]:

If user provides a name, confirm: "OK, ~30% wiadomości będzie zaczynać się od «{name}, ...»"

## Step 5: Scope

> Gdzie zainstalować?
> 1. **Globalnie** (~/.claude/) — działa we wszystkich projektach
> 2. **Tylko w tym projekcie** (.claude/) — działa tylko tutaj
>
> Wybierz [**1**]:

Default: global.

## Step 6: Apply configuration

Based on choices:

**6a. Save config file** `~/.claude/simple-tts-config.json`:
```json
{
  "voice": "<chosen>",
  "name": "<name or empty string>",
  "name_chance": 0.3
}
```

**6b. Add CLAUDE.md instruction**

Target file based on scope:
- Global: `~/.claude/CLAUDE.md`
- Project: `CLAUDE.md` in project root

First READ the existing file (if any). Check if it already contains `<!-- TTS:` instruction. If yes, skip this step and tell the user it's already there.

If not present, **APPEND** (never overwrite!) this block:

```
- Add `<!-- TTS: short message -->` tag at the end of your response when:
  1. Completing a task (what you did in context of user's request)
  2. Before user interaction (what you need or found)
  - This tag is read aloud to the user via macOS TTS so they can switch console knowing the gist of your response without reading it. It must be a natural, spoken-language summary — short enough to hear in a few seconds, specific enough to be useful.
  - Max 10 words, contextual to the user's last message
  - Examples: "Poprawiłem parser zgodnie z wytycznymi", "Znalazłem błąd w module auth", "Testy przechodzą, mogę commitować?", "Potrzebuję zgody na uruchomienie migracji"
  - NEVER generic ("Zadanie wykonane") — always relate to what was actually done or needed
  - TTS voice may mispronounce foreign words. Rules:
    - Prefer native-language descriptions over English names when possible
    - If a technical name MUST appear, use phonetic spelling readable by the TTS voice
    - NEVER put acronyms (API, GOPATH, JSON, URL) in the TTS tag — describe what they are instead
```

## Step 7: Test

```bash
say -v "<voice>" "Konfiguracja zakończona!"
```

## Step 8: Done

> ✅ **Simple TTS skonfigurowany!**
>
> Od następnej sesji Claude będzie mówił krótkie podsumowania gdy:
> - skończy zadanie
> - będzie potrzebował Twojej uwagi
>
> Żeby zmienić ustawienia: `/simple-tts-setup`
> Żeby wyłączyć: `/simple-tts-setup` → Odinstaluj

---

## Uninstall

**Step 1:** Ask scope: "Usunąć globalnie, z projektu, czy z obu?"

**Step 2:**
- Remove the TTS instruction block from the appropriate CLAUDE.md. The block starts with `- Add \`<!-- TTS:` and ends before the next line starting with `- ` at the same indent level (or end of file). Be careful to only remove the TTS block, not other content.
- Remove `~/.claude/simple-tts-config.json`

**Step 3:** Tell user:
> ✅ Simple TTS wyłączony.
> Hooki pluginu można wyłączyć: `claude plugin disable simple-tts`
> Żeby włączyć ponownie: `/simple-tts-setup`
