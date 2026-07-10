#!/usr/bin/env python3
"""
build.py — pipeline de áudio + importação do Anki, para QUALQUER idioma.

Fonte única da verdade: você edita os CSVs listados em config.toml.
Este script:
  1. calcula sozinho o nome de cada arquivo de áudio;
  2. gera os MP3 que faltam (idempotente — pula os que já existem);
  3. gera os CSVs de importação do Anki já com [sound:...] embutido.

Esquema universal de cada CSV (separador ";"):

    Front;Back;Audio;Tags

  • Front  — frente do card (a palavra, frase ou pergunta)
  • Back   — verso do card; pode conter HTML e marcadores {{audio}}
  • Audio  — texto(s) a serem falados. Vários? separe com  |
  • Tags   — tags do Anki (opcional)

Onde o som aparece: cada {{audio}} no Back é trocado, em ordem, pelo botão de
áudio correspondente. Se não houver {{audio}}, os áudios são colocados no fim.

Uso:
    python scripts/build.py                 # gera tudo, conforme config.toml
    python scripts/build.py --voice ryan    # sobrescreve a voz da config
    python scripts/build.py --dry-run       # simula, sem criar arquivos
    python scripts/build.py --only vocabulary   # processa só um deck
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts não instalado. Rode:  pip install -r requirements.txt")

# ─── Caminhos ────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.toml"
MEDIA_DIR = ROOT / "collection.media"
BUILD_DIR = ROOT / "build"

# Apelidos opcionais de voz (atalhos). Qualquer nome completo do Edge TTS também vale.
VOICE_ALIASES = {
    "jenny": "en-US-JennyNeural", "guy": "en-US-GuyNeural", "aria": "en-US-AriaNeural",
    "ryan": "en-GB-RyanNeural", "sonia": "en-GB-SoniaNeural",
    "elvira": "es-ES-ElviraNeural", "denise": "fr-FR-DeniseNeural",
    "francisca": "pt-BR-FranciscaNeural", "katja": "de-DE-KatjaNeural",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def safe_id(text: str) -> str:
    """'Buenos días' -> 'buenos_d_as' ; slug seguro e estável para nome de arquivo."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60] or "item"


def resolve_voice(voice: str) -> str:
    return VOICE_ALIASES.get(voice.lower(), voice)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(f"config.toml não encontrado em {CONFIG_PATH}")
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


@dataclass
class AudioTask:
    text: str
    filename: str


@dataclass
class Card:
    front: str
    back: str
    tags: str


# ─── Leitura de um deck ──────────────────────────────────────────────────────

def split_audio(cell: str) -> list[str]:
    return [p.strip() for p in (cell or "").split("|") if p.strip()]


def parse_deck(deck_name: str, csv_path: Path):
    """Lê um CSV e devolve (tasks_de_audio, cards_para_importar)."""
    tasks: list[AudioTask] = []
    cards: list[Card] = []
    if not csv_path.exists():
        print(f"⚠️  Arquivo não encontrado: {csv_path} (pulando deck '{deck_name}')")
        return tasks, cards

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            front = (row.get("Front") or "").strip()
            if not front:
                continue
            phrases = split_audio(row.get("Audio", ""))
            sound_tags: list[str] = []
            for i, phrase in enumerate(phrases, start=1):
                filename = f"{deck_name}_{safe_id(front)}_{i}.mp3"
                tasks.append(AudioTask(phrase, filename))
                sound_tags.append(f"[sound:{filename}]")
            back = render_back((row.get("Back") or "").strip(), sound_tags)
            cards.append(Card(front, back, (row.get("Tags") or "").strip()))
    return tasks, cards


def render_back(back: str, sound_tags: list[str]) -> str:
    """Troca cada {{audio}} pelo próximo [sound:...]; sobras vão para o fim."""
    remaining = list(sound_tags)
    while "{{audio}}" in back and remaining:
        back = back.replace("{{audio}}", remaining.pop(0), 1)
    back = back.replace("{{audio}}", "")            # remove marcadores sem par
    if remaining:                                   # sobrou áudio sem marcador
        tail = "<br>".join(remaining)
        back = f"{back}<br>{tail}" if back else tail
    return back


# ─── Geração de áudio (concorrente, idempotente) ─────────────────────────────

async def generate_one(task: AudioTask, voice: str, sem: asyncio.Semaphore,
                       dry_run: bool) -> str:
    dest = MEDIA_DIR / task.filename
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  ⏭  SKIP   {task.filename}")
        return "skip"
    if dry_run:
        print(f"  🔎 DRY    {task.filename}")
        return "dry"
    async with sem:
        try:
            await edge_tts.Communicate(task.text, voice).save(str(dest))
            if dest.stat().st_size == 0:
                raise RuntimeError("TTS retornou arquivo vazio")
            print(f"  ✅ OK     {task.filename}")
            return "ok"
        except Exception as e:  # noqa: BLE001
            dest.unlink(missing_ok=True)   # nunca deixa arquivo quebrado
            print(f"  ❌ ERRO   {task.filename}  ({e})")
            return "error"


async def generate_all(tasks: list[AudioTask], voice: str, parallel: int,
                       dry_run: bool) -> None:
    MEDIA_DIR.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(parallel)
    await asyncio.gather(*(generate_one(t, voice, sem, dry_run) for t in tasks))


# ─── Escrita do CSV de importação ────────────────────────────────────────────

def write_import(cards: list[Card], out: Path) -> int:
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        for c in cards:
            w.writerow([c.front, c.back, c.tags])
    return len(cards)


# ─── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Gera áudio + importação do Anki (qualquer idioma).")
    parser.add_argument("--voice", "-v", help="Sobrescreve a voz da config.")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Simula, sem gravar.")
    parser.add_argument("--only", help="Processa só o deck com este nome.")
    args = parser.parse_args()

    cfg = load_config()
    voice = resolve_voice(args.voice or cfg.get("voice", "en-US-JennyNeural"))
    parallel = int(cfg.get("max_parallel", 8))
    decks = cfg.get("deck", [])
    if args.only:
        decks = [d for d in decks if d.get("name") == args.only]
        if not decks:
            sys.exit(f"Nenhum deck chamado '{args.only}' em config.toml")

    print(f"\n🎙  Voz: {voice}")
    if args.dry_run:
        print("   (dry-run: nada será gravado)")

    all_tasks: list[AudioTask] = []
    deck_cards: list[tuple[str, list[Card]]] = []
    for d in decks:
        name, file = d["name"], ROOT / d["file"]
        tasks, cards = parse_deck(name, file)
        all_tasks.extend(tasks)
        deck_cards.append((name, cards))

    print(f"\n🔊  Áudios ({len(all_tasks)} necessários)")
    asyncio.run(generate_all(all_tasks, voice, parallel, args.dry_run))

    if not args.dry_run:
        print("\n📝  CSVs de importação do Anki")
        for name, cards in deck_cards:
            out = BUILD_DIR / f"anki_import_{name}.csv"
            n = write_import(cards, out)
            print(f"  ✅ build/anki_import_{name}.csv  ({n} cards)")
        mp3s = len(list(MEDIA_DIR.glob("*.mp3")))
        print(f"\n✔  Pronto! {mp3s} MP3 em collection.media/  •  imports em build/")
    else:
        print("\n✔  Dry-run finalizado.")


if __name__ == "__main__":
    main()
