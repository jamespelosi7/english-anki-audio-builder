#!/usr/bin/env python3
"""
copy_audio_to_anki.py — copia os MP3 de collection.media/ para a pasta
collection.media do Anki (detecta o caminho automaticamente).

Uso:
    python scripts/copy_audio_to_anki.py                 # detecção automática
    python scripts/copy_audio_to_anki.py "CAMINHO/..."   # caminho manual
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "collection.media"


def candidate_anki_dirs() -> list[Path]:
    home = Path.home()
    bases = [
        home / "AppData" / "Roaming" / "Anki2",               # Windows
        home / "Library" / "Application Support" / "Anki2",    # macOS
        home / ".local" / "share" / "Anki2",                   # Linux
    ]
    found: list[Path] = []
    for base in bases:
        if base.exists():
            for profile in base.iterdir():
                media = profile / "collection.media"
                if media.is_dir():
                    found.append(media)
    return found


def main() -> None:
    targets = [Path(sys.argv[1])] if len(sys.argv) > 1 else candidate_anki_dirs()
    if not targets:
        sys.exit("❌ Pasta do Anki não encontrada. Informe o caminho:\n"
                 '   python scripts/copy_audio_to_anki.py "C:\\...\\collection.media"')
    if len(targets) > 1:
        print("Vários perfis encontrados. Escolha passando o caminho manualmente:")
        for t in targets:
            print(f"  {t}")
        return

    dest = targets[0]
    dest.mkdir(parents=True, exist_ok=True)
    mp3s = list(SRC.glob("*.mp3"))
    for mp3 in mp3s:
        shutil.copy2(mp3, dest / mp3.name)
    print(f"✔  Copiei {len(mp3s)} arquivos para:\n   {dest}")
    print("   Feche e reabra o Anki para o áudio tocar.")


if __name__ == "__main__":
    main()
