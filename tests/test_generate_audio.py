"""Unit tests for generate_audio.py — run with: pytest"""

import sys
from pathlib import Path

# Make scripts/ importable
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_audio import (  # noqa: E402
    AudioTask,
    read_connector_tasks,
    read_vocabulary_tasks,
    resolve_voice,
    safe_id,
)


# ─── safe_id ─────────────────────────────────────────────────────────────────

class TestSafeId:
    def test_simple_phrase(self):
        assert safe_id("A piece of") == "a_piece_of"

    def test_apostrophe(self):
        assert safe_id("Don't worry") == "don_t_worry"

    def test_special_characters(self):
        assert safe_id("Hello, world! (test)") == "hello_world_test"

    def test_leading_trailing_spaces(self):
        assert safe_id("  spaced out  ") == "spaced_out"

    def test_accents_removed(self):
        # Accented chars are non [a-z0-9] so become underscores
        assert safe_id("café") == "caf"

    def test_max_length_60(self):
        long_text = "word " * 50
        assert len(safe_id(long_text)) <= 60

    def test_never_starts_or_ends_with_underscore(self):
        result = safe_id("!!!hello!!!")
        assert not result.startswith("_")
        assert not result.endswith("_")


# ─── resolve_voice ───────────────────────────────────────────────────────────

class TestResolveVoice:
    def test_alias_jenny(self):
        assert resolve_voice("jenny") == "en-US-JennyNeural"

    def test_alias_guy(self):
        assert resolve_voice("guy") == "en-US-GuyNeural"

    def test_alias_ryan(self):
        assert resolve_voice("ryan") == "en-GB-RyanNeural"

    def test_alias_case_insensitive(self):
        assert resolve_voice("JENNY") == "en-US-JennyNeural"

    def test_full_name_passthrough(self):
        assert resolve_voice("en-AU-NatashaNeural") == "en-AU-NatashaNeural"


# ─── CSV parsing ─────────────────────────────────────────────────────────────

class TestReadVocabularyTasks:
    def test_parses_three_sentences_per_word(self, tmp_path):
        csv_file = tmp_path / "vocab.csv"
        csv_file.write_text(
            "Front;Sentence_1_EN;Sentence_2_EN;Sentence_3_EN\n"
            "A piece of;First sentence.;Second sentence.;Third sentence.\n",
            encoding="utf-8",
        )
        tasks = read_vocabulary_tasks(csv_file)
        assert len(tasks) == 3
        assert tasks[0] == AudioTask("First sentence.", "vocab_a_piece_of_1.mp3")
        assert tasks[2].filename == "vocab_a_piece_of_3.mp3"

    def test_skips_empty_sentences(self, tmp_path):
        csv_file = tmp_path / "vocab.csv"
        csv_file.write_text(
            "Front;Sentence_1_EN;Sentence_2_EN;Sentence_3_EN\n"
            "word;Only one.;;\n",
            encoding="utf-8",
        )
        tasks = read_vocabulary_tasks(csv_file)
        assert len(tasks) == 1

    def test_skips_rows_without_front(self, tmp_path):
        csv_file = tmp_path / "vocab.csv"
        csv_file.write_text(
            "Front;Sentence_1_EN;Sentence_2_EN;Sentence_3_EN\n"
            ";Orphan sentence.;;\n",
            encoding="utf-8",
        )
        assert read_vocabulary_tasks(csv_file) == []

    def test_missing_file_returns_empty(self, tmp_path):
        assert read_vocabulary_tasks(tmp_path / "nope.csv") == []


class TestReadConnectorTasks:
    def test_parses_one_sentence_per_connector(self, tmp_path):
        csv_file = tmp_path / "conn.csv"
        csv_file.write_text(
            "Front;Sentence_EN\n"
            "however;However, I disagree.\n"
            "therefore;Therefore, we won.\n",
            encoding="utf-8",
        )
        tasks = read_connector_tasks(csv_file)
        assert len(tasks) == 2
        assert tasks[0] == AudioTask("However, I disagree.", "connector_however.mp3")

    def test_missing_file_returns_empty(self, tmp_path):
        assert read_connector_tasks(tmp_path / "nope.csv") == []


# ─── Real project data (integration) ────────────────────────────────────────

class TestRealData:
    """Validates the actual CSVs shipped in data/."""

    DATA = Path(__file__).parent.parent / "data"

    def test_vocabulary_has_180_sentences(self):
        tasks = read_vocabulary_tasks(self.DATA / "01_vocabulary_60_oral_test.csv")
        assert len(tasks) == 180  # 60 words × 3 sentences

    def test_connectors_has_40_sentences(self):
        tasks = read_connector_tasks(self.DATA / "02_connectors_40_oral_test.csv")
        assert len(tasks) == 40

    def test_no_duplicate_filenames(self):
        vocab = read_vocabulary_tasks(self.DATA / "01_vocabulary_60_oral_test.csv")
        conn = read_connector_tasks(self.DATA / "02_connectors_40_oral_test.csv")
        filenames = [t.filename for t in vocab + conn]
        assert len(filenames) == len(set(filenames)), "Duplicate audio filenames!"

    def test_all_filenames_are_safe(self):
        vocab = read_vocabulary_tasks(self.DATA / "01_vocabulary_60_oral_test.csv")
        for task in vocab:
            assert " " not in task.filename
            assert task.filename.endswith(".mp3")
