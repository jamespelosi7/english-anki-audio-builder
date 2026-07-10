# Step-by-step tutorial (no experience needed)

This guide assumes **zero** experience with the terminal or Python. Follow it
top to bottom and by the end you'll have Anki flashcards that speak to you.
It takes about 15 minutes the first time; after that, adding new cards takes 2.

---

## Part 1 — One-time setup

### Step 1. Install Anki

Download and install Anki from [apps.ankiweb.net](https://apps.ankiweb.net/).
Open it once so it creates its folders, then you can close it.

### Step 2. Open the terminal

- **Mac:** press `Cmd + Space`, type `Terminal`, press Enter.
- **Windows:** press the Windows key, type `PowerShell`, press Enter.
- **Linux:** you already know where it is 🙂

A window with text appears. You'll type commands into it and press Enter to
run them. That's all the terminal is.

### Step 3. Check that Python is installed

Type this and press Enter:

```bash
python3 --version
```

(on Windows, try `python --version` if that doesn't work)

- If you see something like `Python 3.9.6` or higher → you're good, go to Step 4.
- If you see an error → install Python from [python.org/downloads](https://www.python.org/downloads/)
  (on Windows, tick **"Add Python to PATH"** during installation), then close
  and reopen the terminal and try again.

### Step 4. Download this project

**Option A (no Git needed):** on the [project page](https://github.com/jamespelosi7/english-anki-audio-builder),
click the green **Code** button → **Download ZIP**. Unzip it somewhere easy,
like your `Documents` folder.

**Option B (with Git):**

```bash
git clone https://github.com/jamespelosi7/english-anki-audio-builder.git
```

### Step 5. Enter the project folder in the terminal

```bash
cd Documents/english-anki-audio-builder
```

Adjust the path to wherever you put the folder. Tip: type `cd ` (with a space)
and **drag the folder** from your file explorer into the terminal window — it
pastes the full path for you. Press Enter.

### Step 6. Create the environment and install (copy-paste, one line at a time)

**Mac / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

When it works, the line in your terminal starts with `(.venv)`. This step is
only needed once.

> ⚠️ **Windows:** if you get an error about "running scripts is disabled",
> run this once and try again:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

## Part 2 — Your first deck with audio

### Step 7. Look at an example CSV

Open the file `data/spanish_basics.csv` with **TextEdit, Notepad, or VS Code**
(not Excel — it corrupts the format). Each line is one card, with 4 parts
separated by `;`:

```
Front;Back;Audio;Tags
gracias;obrigado(a)<br><br>Muchas gracias por tu ayuda. {{audio}};Muchas gracias por tu ayuda.;saludos
```

- **Front** → what you see first (the word)
- **Back** → the answer. `<br>` = line break, `{{audio}}` = where the play button goes
- **Audio** → the exact text that will be spoken
- **Tags** → optional labels

### Step 8. Generate the audio

Back in the terminal (still inside the project folder, with `(.venv)` showing):

```bash
python scripts/build.py --only spanish_basics --voice es-ES-ElviraNeural
```

You should see `✅ OK` lines — each one is an MP3 being created. This needs
internet (the voices come from Microsoft's free service).

### Step 9. Copy the audio into Anki

```bash
python scripts/copy_audio_to_anki.py
```

It finds your Anki folder automatically and copies the MP3s there.

### Step 10. Import the cards into Anki

1. Open **Anki**.
2. Menu **File → Import**.
3. Choose the file `build/anki_import_spanish_basics.csv` (inside the project folder).
4. In the import window, set:
   - **Field separator:** Semicolon
   - **Allow HTML in fields:** ✅ checked
   - Field 1 → **Front**, Field 2 → **Back**, Field 3 → **Tags**
5. Click **Import**.

Study the deck — when the answer appears, the audio plays. 🎉

---

## Part 3 — Making it yours

### Adding your own words

1. Open a CSV in `data/` and add lines following the same 4-column format.
2. Run steps 8–10 again. Done. (Re-importing updates existing cards and adds
   the new ones — no duplicates.)

### Using another language

Every language = a voice. Some examples:

| Language | Voice |
|---|---|
| English (US) | `en-US-JennyNeural` |
| Spanish | `es-ES-ElviraNeural` |
| French | `fr-FR-DeniseNeural` |
| German | `de-DE-KatjaNeural` |
| Italian | `it-IT-ElsaNeural` |
| Japanese | `ja-JP-NanamiNeural` |
| Portuguese (BR) | `pt-BR-FranciscaNeural` |

To see all of them: `edge-tts --list-voices`

To create a deck in a new language:

1. Create a new CSV in `data/`, e.g. `data/french_basics.csv` (same 4 columns).
2. Register it in `config.toml`:

   ```toml
   [[deck]]
   name = "french_basics"
   file = "data/french_basics.csv"
   ```

3. Build it with the right voice:

   ```bash
   python scripts/build.py --only french_basics --voice fr-FR-DeniseNeural
   python scripts/copy_audio_to_anki.py
   ```

4. Import `build/anki_import_french_basics.csv` in Anki.

### Coming back another day

Only one extra step: reactivate the environment when you open a new terminal.

```bash
cd Documents/english-anki-audio-builder
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

Then edit CSVs and run steps 8–10 as usual.

---

## Troubleshooting

**"command not found: python3"** → Python isn't installed (Step 3), or on
Windows use `python` instead.

**"No module named edge_tts"** → the environment isn't active. Run the
`activate` command (see "Coming back another day"), or redo Step 6.

**Audio doesn't play in Anki** → run `python scripts/copy_audio_to_anki.py`
again, then close and reopen Anki.

**Cards imported but look like raw code (`<br>` visible)** → you forgot to
check **Allow HTML in fields** during import. Delete the deck and import again.

**❌ ERRO lines during build** → usually no internet, or a firewall blocking
Microsoft's TTS service. Check your connection and run the same command again
(already-created files are skipped, so nothing is lost).

**Excel ruined my CSV** → edit CSVs with a plain text editor (TextEdit,
Notepad, VS Code). Restore the file from Git or re-download the project.
