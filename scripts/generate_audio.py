"""Generate MP3 audio files for Anki cards using Microsoft Edge TTS (free).

Usage:
    python scripts/generate_audio.py
    python scripts/generate_audio.py --voice guy
    python scripts/generate_audio.py --voice en-GB-RyanNeural
    python scripts/generate_audio.py --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import edge_tts
except ImportError:
    edge_tts = None  # checked at runtime in cli(); allows importing pure functions in tests

# ─── Configuration ───────────────────────────────────────────────────────────

DEFAULT_VOICE = "en-US-JennyNeural"

AVAILABLE_VOICES: dict[str, str] = {
    "jenny": "en-US-JennyNeural",   # female, US (default)
    "guy":   "en-US-GuyNeural",     # male, US
    "ryan":  "en-GB-RyanNeural",    # male, UK
    "sonia": "en-GB-SoniaNeural",   # female, UK
    "aria":  "en-US-AriaNeural",    # female, US
}

DATA_DIR = Path("data")
MEDIA_DIR = Path("collection.media")
MAX_CONCURRENT = 8  # parallel TTS requests (be kind to the free API)


# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class AudioTask:
    """A single sentence to be converted to speech."""
    text: str
    filename: str


# ─── Pure helpers (unit-testable) ────────────────────────────────────────────

def safe_id(text: str) -> str:
    """Convert arbitrary text to a safe filename slug.

    >>> safe_id("A piece of")
    'a_piece_of'
    >>> safe_id("  Don't worry!  ")
    'don_t_worry'
    """
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60]


def resolve_voice(voice_arg: str) -> str:
    """Accept a short alias (jenny, guy, ryan) or a full Edge TTS voice name."""
    return AVAILABLE_VOICES.get(voice_arg.lower(), voice_arg)


def read_vocabulary_tasks(csv_path: Path) -> list[AudioTask]:
    """Parse the vocabulary CSV into audio tasks (3 sentences per word)."""
    tasks: list[AudioTask] = []
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return tasks

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            front = (row.get("Front") or "").strip()
            if not front:
                continue
            for n in (1, 2, 3):
                text = (row.get(f"Sentence_{n}_EN") or "").strip()
                if text:
                    tasks.append(AudioTask(text, f"vocab_{safe_id(front)}_{n}.mp3"))
    return tasks


def read_connector_tasks(csv_path: Path) -> list[AudioTask]:
    """Parse the connectors CSV into audio tasks (1 sentence per connector)."""
    tasks: list[AudioTask] = []
    if not csv_path.exists():
        print(f"⚠️  File not found: {csv_path}")
        return tasks

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            front = (row.get("Front") or "").strip()
            text = (row.get("Sentence_EN") or "").strip()
            if front and text:
                tasks.append(AudioTask(text, f"connector_{safe_id(front)}.mp3"))
    return tasks


# ─── TTS generation (concurrent) ─────────────────────────────────────────────

async def generate_one(
    task: AudioTask,
    voice: str,
    semaphore: asyncio.Semaphore,
    dry_run: bool = False,
) -> str:
    """Generate a single MP3. Returns 'ok', 'skip', 'dry' or 'error'."""
    output = MEDIA_DIR / task.filename

    if output.exists():
        print(f"  ⏭  SKIP   {task.filename}")
        return "skip"

    if dry_run:
        preview = task.text[:60] + ("…" if len(task.text) > 60 else "")
        print(f"  🔍 DRY    {task.filename}  →  \"{preview}\"")
        return "dry"

    async with semaphore:  # limit concurrent API calls
        try:
            communicate = edge_tts.Communicate(text=task.text, voice=voice)
            await communicate.save(str(output))
            print(f"  ✅ OK     {task.filename}")
            return "ok"
        except Exception as e:
            print(f"  ❌ ERROR  {task.filename}  →  {e}")
            return "error"


async def generate_all(tasks: list[AudioTask], voice: str, dry_run: bool) -> dict[str, int]:
    """Generate all audio files concurrently. Returns result counts."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    results = await asyncio.gather(
        *(generate_one(t, voice, semaphore, dry_run) for t in tasks)
    )
    counts: dict[str, int] = {}
    for r in results:
        counts[r] = counts.get(r, 0) + 1
    return counts


# ─── Main ────────────────────────────────────────────────────────────────────

async def main(voice: str, dry_run: bool) -> int:
    MEDIA_DIR.mkdir(exist_ok=True)

    print(f"\n🎙  Voice: {voice}")
    if dry_run:
        print("   (--dry-run mode: no files will be created)")
    print()

    print("📚  Vocabulary (60 words × 3 sentences)")
    vocab_tasks = read_vocabulary_tasks(DATA_DIR / "01_vocabulary_60_oral_test.csv")
    vocab_counts = await generate_all(vocab_tasks, voice, dry_run)

    print("\n🔗  Connectors (40 words × 1 sentence)")
    conn_tasks = read_connector_tasks(DATA_DIR / "02_connectors_40_oral_test.csv")
    conn_counts = await generate_all(conn_tasks, voice, dry_run)

    total_ok = vocab_counts.get("ok", 0) + conn_counts.get("ok", 0)
    total_skip = vocab_counts.get("skip", 0) + conn_counts.get("skip", 0)
    total_err = vocab_counts.get("error", 0) + conn_counts.get("error", 0)

    print(f"\n✔  Done! generated={total_ok}  skipped={total_skip}  errors={total_err}")
    print(f"   Files in: {MEDIA_DIR}/")

    return 1 if total_err else 0


def cli() -> None:
    if edge_tts is None:
        print("❌  edge-tts not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Generate Anki audio with Edge TTS")
    parser.add_argument(
        "--voice", "-v",
        default=DEFAULT_VOICE,
        help=f"Voice alias {list(AVAILABLE_VOICES)} or full name. Default: {DEFAULT_VOICE}",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be generated without creating files.",
    )
    args = parser.parse_args()
    exit_code = asyncio.run(main(voice=resolve_voice(args.voice), dry_run=args.dry_run))
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
