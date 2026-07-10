# anki-audio-builder

Turn a simple CSV into **Anki flashcards with native-sounding audio** — in *any*
language. Powered by free Microsoft Edge TTS (no API key). Edit one CSV, run one
command, import into Anki.

Originally built to prep for an English oral exam, then generalized so anyone can
use it for **any language and any words or phrases** they want.

> **New to the terminal or Python?** Follow the detailed, zero-assumptions
> step-by-step guide: **[TUTORIAL.md](TUTORIAL.md)** (English) — it walks you
> through everything, from installing Python to hearing your first card.

## Why it's easy to maintain

There's a **single source of truth**: the CSVs you edit. One command rebuilds
everything else.

```
config.toml  +  data/*.csv   ──►  python scripts/build.py  ──►  collection.media/*.mp3
                                                            └──►  build/anki_import_*.csv
```

`build.py` figures out the audio filenames itself, generates only the files that
are missing (safe to re-run), and writes Anki import files with `[sound:...]`
already wired in. No manual syncing, no naming audio by hand.

## Any language, one line

Switch languages by changing a single line in `config.toml`:

```toml
voice = "es-ES-ElviraNeural"   # Spanish
# voice = "fr-FR-DeniseNeural"  # French
# voice = "ja-JP-NanamiNeural"  # Japanese
# voice = "pt-BR-FranciscaNeural" # Portuguese
```

Run `edge-tts --list-voices` to see every available voice.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/build.py            # generate audio + import files
python scripts/copy_audio_to_anki.py   # copy MP3s into Anki (auto-detects the folder)
```

Then in Anki: **File → Import** each `build/anki_import_*.csv`
(Separator: **Semicolon**, Allow HTML in fields: **✅**, fields → Front / Back / Tags).

## The CSV format

Every CSV uses the same four columns, separated by `;`:

| Column | Meaning |
| --- | --- |
| `Front` | Front of the card (word, phrase, or prompt) |
| `Back`  | Back of the card. HTML allowed. Put `{{audio}}` where you want a play button |
| `Audio` | Text to speak. Multiple phrases separated by `\|` |
| `Tags`  | Anki tags (optional) |

Example row:

```
hello;olá<br><br>Hello, how are you? {{audio}};Hello, how are you?;greetings
```

Each `{{audio}}` is replaced, in order, by the matching audio. Leave it out and
the audio is appended to the end of the card.

## Adding new cards

1. Open a CSV in `data/` (use a text editor / VS Code, not Excel — it mangles `;` and encoding).
2. Add a row.
3. `python scripts/build.py && python scripts/copy_audio_to_anki.py`
4. Re-import the CSV in Anki (it updates existing cards and adds new ones).

To add a whole new set (e.g. another language or topic), create a CSV in `data/`
and register it in `config.toml` under a new `[[deck]]`.

## Project structure

```
├── config.toml                 # voice + which CSVs to build
├── data/                       # YOUR source CSVs (single source of truth)
├── scripts/
│   ├── build.py                # audio + Anki import generator
│   └── copy_audio_to_anki.py   # copies MP3s into Anki
├── build/                      # generated import CSVs (gitignored)
├── collection.media/           # generated MP3s (gitignored)
└── requirements.txt
```

## Requirements

- Python 3.9+ (on 3.9/3.10 the `tomli` backport is installed automatically)
- [`edge-tts`](https://pypi.org/project/edge-tts/) — the only dependency

## License

MIT — see [LICENSE](LICENSE).
