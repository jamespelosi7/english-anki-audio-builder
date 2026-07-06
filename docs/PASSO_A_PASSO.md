# 📖 Passo a Passo Detalhado — English Anki Audio Builder

> Guia completo para Windows, com instruções de instalação, geração de áudio, importação no Anki e versionamento no GitHub.

---

## Fase 1 — Instalar o Python

1. Acesse [python.org/downloads](https://www.python.org/downloads/)
2. Baixe a versão mais recente (3.11 ou superior)
3. Na instalação, marque **"Add Python to PATH"** ✅
4. Clique em **Install Now**
5. Verifique a instalação:

```powershell
python --version
# Saída esperada: Python 3.12.x
```

---

## Fase 2 — Instalar o Git

1. Acesse [git-scm.com](https://git-scm.com/)
2. Baixe e instale com as opções padrão
3. Verifique:

```powershell
git --version
# Saída esperada: git version 2.x.x
```

---

## Fase 3 — Preparar o projeto

1. Baixe o ZIP do projeto
2. Extraia para uma pasta de fácil acesso, ex: `C:\Projetos\english-anki-audio-builder`
3. Abra o **PowerShell** ou **VS Code Terminal** dentro da pasta

```powershell
# Navegue até a pasta (ajuste o caminho)
cd C:\Projetos\english-anki-audio-builder
```

---

## Fase 4 — Criar ambiente virtual e instalar dependências

```powershell
# 1. Criar o ambiente virtual
python -m venv .venv

# 2. Ativar
.venv\Scripts\activate

# Você verá (.venv) no início do terminal — isso é correto!

# 3. Instalar edge-tts
pip install -r requirements.txt
```

> **Dica**: sempre que abrir um novo terminal, ative o venv antes de rodar qualquer script.

---

## Fase 5 — Gerar os áudios

```powershell
python scripts/generate_audio.py
```

### Saída esperada:

```
🎙  Voz: en-US-JennyNeural

📚  Vocabulário (60 palavras × 3 frases)
  ✅ OK     vocab_a_piece_of_1.mp3
  ✅ OK     vocab_a_piece_of_2.mp3
  ✅ OK     vocab_a_piece_of_3.mp3
  ✅ OK     vocab_a_loaf_of_1.mp3
  ...

🔗  Connectors (40 palavras × 1 frase)
  ✅ OK     connector_and.mp3
  ✅ OK     connector_but.mp3
  ...

✔  Concluído! 220 arquivos em collection.media/
```

### Rodar de novo sem reprocessar:

```powershell
python scripts/generate_audio.py
# Arquivos existentes mostram ⏭ SKIP
```

### Mudar a voz:

```powershell
# Masculina americana
python scripts/generate_audio.py --voice guy

# Britânica masculina
python scripts/generate_audio.py --voice ryan
```

### Ver o que seria gerado sem criar arquivos:

```powershell
python scripts/generate_audio.py --dry-run
```

---

## Fase 6 — Importar os cards no Anki

### Criar os decks

1. Abra o **Anki**
2. Clique em **Create Deck** (canto inferior esquerdo)
3. Digite `James::01 Oral Test Vocabulary` e confirme
4. Repita para `James::02 Connectors`

### Importar vocabulário

1. Menu **File → Import**
2. Selecione o arquivo: `data/anki_import_vocabulary_phrases.csv`
3. Configure as opções:
   - **Type**: Basic (ou o tipo que usar)
   - **Deck**: `James::01 Oral Test Vocabulary`
   - **Separator**: `Semicolon`
   - **Allow HTML in fields**: ✅
4. Clique **Import**

### Importar connectors

1. Menu **File → Import**
2. Selecione: `data/anki_import_connectors.csv`
3. Mesmo processo — deck: `James::02 Connectors`

---

## Fase 7 — Copiar os áudios para o Anki

### Opção 1 — Script automático (recomendado)

```powershell
python scripts/copy_audio_to_anki.py
```

O script detecta automaticamente o caminho do Anki no Windows.

### Opção 2 — Caminho manual

```powershell
python scripts/copy_audio_to_anki.py "C:\Users\SEU_USUARIO\AppData\Roaming\Anki2\User 1\collection.media"
```

### Opção 3 — Copiar manualmente

1. No Anki: **Tools → Add-ons → View Files**
2. Volte uma pasta (de `addons21` para `Anki2`)
3. Entre em `User 1\collection.media`
4. Copie todos os `.mp3` da pasta `collection.media\` do projeto para cá

### Verificar no Anki

Feche e reabra o Anki. Ao revisar um card, o áudio deve tocar automaticamente.

---

## Fase 8 — Versionar com Git e subir no GitHub

### Configurar o Git (uma vez só)

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

### Inicializar o repositório

```powershell
git init
git add .
git commit -m "Initial Anki audio builder"
```

### Criar o repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique em **New repository**
3. Nome: `english-anki-audio-builder`
4. Deixe **privado** se não quiser compartilhar
5. Não marque "Initialize this repository"
6. Clique **Create repository**

### Enviar para o GitHub

```powershell
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/english-anki-audio-builder.git
git push -u origin main
```

### Próximos commits (quando editar os CSVs)

```powershell
git add .
git commit -m "Adiciona mais 10 palavras ao vocabulário"
git push
```

---

## Cronograma de estudo sugerido

| Dia | Foco | Meta |
|-----|------|------|
| Sexta | Food & containers | 20 palavras |
| Sábado | Hobbies & shopping | 20 palavras |
| Domingo | Descrições & connectors | 20 palavras + 20 connectors básicos |
| Segunda | Revisão geral | Falar respostas em voz alta |

---

## Problemas comuns

### `edge-tts` não encontrado

```powershell
pip install edge-tts
```

### Python não reconhecido no terminal

Reinstale o Python marcando **"Add Python to PATH"**.

### Áudio não toca no Anki

- Verifique se os `.mp3` estão na pasta `collection.media` **do Anki** (não do projeto)
- Feche e reabra o Anki após copiar
- Verifique se o card tem o campo `[sound:nome_do_arquivo.mp3]`

### Erro de permissão ao copiar

Execute o PowerShell como Administrador, ou copie manualmente os arquivos.
