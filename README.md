# 🎧 English Anki Audio Builder

[![CI](https://github.com/jamespelosi7/english-anki-audio-builder/actions/workflows/ci.yml/badge.svg)](https://github.com/jamespelosi7/english-anki-audio-builder/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Generate **free English TTS audio** for Anki flashcards using Microsoft Edge TTS. Built to prepare for an oral exam with 60 vocabulary words and 40 connectors — 220 MP3 files generated concurrently in seconds.

> 🇧🇷 [Documentação em português](README.pt-BR.md) · [Passo a passo detalhado](docs/PASSO_A_PASSO.md)

## Features

- **Free TTS** — uses Microsoft Edge neural voices, no API key required
- **Concurrent generation** — async pipeline with a semaphore (8 parallel requests)
- **Idempotent** — re-running skips already-generated files
- **Voice selection** — `--voice jenny|guy|ryan|sonia|aria` or any Edge TTS voice name
- **Dry-run mode** — preview what would be generated with `--dry-run`
- **Anki-ready CSVs** — import files with `[sound:...]` tags already wired
- **Auto-detection** — finds your Anki `collection.media` folder on macOS, Windows, and Linux
- **Tested** — 22 unit + integration tests, linted with ruff, CI on every push

## Quick start

```bash
# 1. Set up
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Generate all 220 audio files
python scripts/generate_audio.py

# 3. Copy them into Anki (auto-detects your Anki folder)
python scripts/copy_audio_to_anki.py
```

Then import `data/anki_import_vocabulary_phrases.csv` and `data/anki_import_connectors.csv` in Anki (**File → Import**, separator: `Semicolon`, allow HTML: ✅).

## Usage

```bash
# Default voice (en-US-JennyNeural)
python scripts/generate_audio.py

# British male voice
python scripts/generate_audio.py --voice ryan

# Any Edge TTS voice
python scripts/generate_audio.py --voice en-AU-NatashaNeural

# Preview without generating
python scripts/generate_audio.py --dry-run
```

## Project structure

```
english-anki-audio-builder/
├── data/                          # Source CSVs + Anki import files
├── scripts/
│   ├── generate_audio.py          # Async TTS pipeline
│   └── copy_audio_to_anki.py      # Cross-platform Anki media copier
├── tests/                         # pytest suite (22 tests)
├── docs/PASSO_A_PASSO.md          # Detailed guide (Portuguese)
├── .github/workflows/ci.yml       # Lint + test on push
└── collection.media/              # Generated MP3s (gitignored)
```

## Development

```bash
pip install -r requirements-dev.txt
pytest tests/ -v      # run tests
ruff check .          # lint
```

## How it works

1. `generate_audio.py` parses the semicolon-delimited CSVs into `AudioTask` dataclasses
2. Tasks run concurrently through `asyncio.gather` with a semaphore limiting parallel TTS requests
3. Filenames are slugified (`safe_id`) so they're filesystem- and Anki-safe
4. The Anki import CSVs reference each MP3 via `[sound:filename.mp3]` tags

## License

MIT — see [LICENSE](LICENSE).
