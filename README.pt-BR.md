# 🎧 English Anki Audio Builder

> 🇺🇸 [English documentation](README.md) — the main README is in English for your portfolio.

Projeto para gerar áudios em inglês para cards do Anki usando **Microsoft Edge TTS (gratuito)**.

## O que tem aqui

| Arquivo | Conteúdo |
|---|---|
| `data/01_vocabulary_60_oral_test.csv` | 60 palavras com 3 frases cada |
| `data/02_connectors_40_oral_test.csv` | 40 connectors com 1 frase cada |
| `data/anki_import_vocabulary_phrases.csv` | CSV pronto para importar no Anki (vocabulário) |
| `data/anki_import_connectors.csv` | CSV pronto para importar no Anki (connectors) |
| `scripts/generate_audio.py` | Gera os MP3 com Edge TTS |
| `scripts/copy_audio_to_anki.py` | Copia os MP3 para o Anki |

---

## ⚡ Início rápido

### 1. Pré-requisitos

- Python 3.11 ou superior → [python.org/downloads](https://www.python.org/downloads/)
- Git → [git-scm.com](https://git-scm.com/)

### 2. Configurar o projeto

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Gerar os áudios

```bash
python scripts/generate_audio.py
```

Saída esperada:

```
🎙  Voz: en-US-JennyNeural

📚  Vocabulário (60 palavras × 3 frases)
  ✅ OK     vocab_a_piece_of_1.mp3
  ✅ OK     vocab_a_piece_of_2.mp3
  ...

🔗  Connectors (40 palavras × 1 frase)
  ✅ OK     connector_and.mp3
  ...

✔  Concluído! 220 arquivos em collection.media/
```

> Rode o script de novo e os arquivos já gerados serão pulados (`⏭ SKIP`).

### 4. Mudar a voz (opcional)

```bash
# Feminina americana (padrão)
python scripts/generate_audio.py --voice jenny

# Masculina americana
python scripts/generate_audio.py --voice guy

# Masculina britânica
python scripts/generate_audio.py --voice ryan

# Feminina britânica
python scripts/generate_audio.py --voice sonia

# Nome completo (qualquer voz do Edge TTS)
python scripts/generate_audio.py --voice en-US-AriaNeural
```

### 5. Importar os CSVs no Anki

1. Abra o **Anki**
2. Crie o deck `James::01 Oral Test Vocabulary`
3. Menu **File → Import**
4. Selecione `data/anki_import_vocabulary_phrases.csv`
5. Configure:
   - **Separator**: `Semicolon`
   - **Allow HTML in fields**: ✅ marcado
6. Clique **Import**

Repita com `data/anki_import_connectors.csv` no deck `James::02 Connectors`.

### 6. Copiar os áudios para o Anki

```bash
# Detecção automática (Windows / Mac / Linux)
python scripts/copy_audio_to_anki.py

# Ou informe o caminho manualmente
python scripts/copy_audio_to_anki.py "C:\Users\SEU_USUARIO\AppData\Roaming\Anki2\User 1\collection.media"
```

---

## 🗂 Git & GitHub

```bash
# Inicializar o repositório
git init
git add .
git commit -m "Initial Anki audio builder"

# Enviar para o GitHub
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/english-anki-audio-builder.git
git push -u origin main
```

---

## 📋 Estrutura do projeto

```
english-anki-audio-builder/
├── data/
│   ├── 01_vocabulary_60_oral_test.csv
│   ├── 02_connectors_40_oral_test.csv
│   ├── anki_import_vocabulary_phrases.csv
│   └── anki_import_connectors.csv
├── scripts/
│   ├── generate_audio.py
│   └── copy_audio_to_anki.py
├── docs/
│   └── PASSO_A_PASSO.md
├── collection.media/          ← gerada pelo script (não versionada)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📖 Documentação completa

Veja [`docs/PASSO_A_PASSO.md`](docs/PASSO_A_PASSO.md) para instruções detalhadas com prints de tela e cronograma de estudos.
