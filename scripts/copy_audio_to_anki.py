"""
copy_audio_to_anki.py
---------------------
Copia os arquivos .mp3 gerados para a pasta collection.media do Anki.

Uso:
    python scripts/copy_audio_to_anki.py                  # detecta automaticamente no Windows
    python scripts/copy_audio_to_anki.py "CAMINHO_MANUAL" # caminho explícito

Caminhos padrão do Anki:
    Windows : C:\\Users\\<usuário>\\AppData\\Roaming\\Anki2\\User 1\\collection.media
    Mac     : ~/Library/Application Support/Anki2/User 1/collection.media
    Linux   : ~/.local/share/Anki2/User 1/collection.media
"""

import shutil
import sys
import platform
from pathlib import Path

# ─── Detecção automática do caminho do Anki ──────────────────────────────────

def find_anki_media() -> Path | None:
    """Tenta localizar a pasta collection.media do Anki automaticamente."""
    system = platform.system()

    if system == "Windows":
        base = Path.home() / "AppData" / "Roaming" / "Anki2"
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "Anki2"
    else:
        base = Path.home() / ".local" / "share" / "Anki2"

    if not base.exists():
        return None

    # Procura a primeira pasta de usuário com collection.media
    for user_dir in sorted(base.iterdir()):
        candidate = user_dir / "collection.media"
        if candidate.is_dir():
            return candidate

    return None


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    source = Path("collection.media")

    if not source.exists() or not list(source.glob("*.mp3")):
        print("❌  Pasta collection.media/ está vazia ou não existe.")
        print("    Rode primeiro: python scripts/generate_audio.py")
        sys.exit(1)

    # Destino: argumento CLI ou detecção automática
    if len(sys.argv) >= 2:
        destination = Path(sys.argv[1])
        print(f"📁  Destino (manual): {destination}")
    else:
        destination = find_anki_media()
        if destination:
            print(f"🔍  Anki detectado automaticamente: {destination}")
        else:
            print("⚠️  Não foi possível detectar o Anki automaticamente.")
            print("    Passe o caminho manualmente:")
            print()
            print('    Windows:')
            print(r'    python scripts/copy_audio_to_anki.py "C:\Users\SEU_USUARIO\AppData\Roaming\Anki2\User 1\collection.media"')
            print()
            print('    Mac:')
            print('    python scripts/copy_audio_to_anki.py "/Users/SEU_USUARIO/Library/Application Support/Anki2/User 1/collection.media"')
            sys.exit(1)

    destination.mkdir(parents=True, exist_ok=True)

    mp3_files = list(source.glob("*.mp3"))
    copied = 0
    skipped = 0

    for file in sorted(mp3_files):
        dest_file = destination / file.name
        if dest_file.exists():
            skipped += 1
        else:
            shutil.copy2(file, dest_file)
            copied += 1

    print()
    print(f"✅  {copied} arquivo(s) copiado(s)")
    if skipped:
        print(f"⏭  {skipped} arquivo(s) já existiam (pulados)")
    print("\n🎉  Pronto! Feche e reabra o Anki para carregar os áudios.")


if __name__ == "__main__":
    main()
