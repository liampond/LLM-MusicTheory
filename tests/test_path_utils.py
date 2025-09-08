"""
Test path utilities and data loading functions.
"""
from pathlib import Path
import tempfile
import pytest

from llm_music_theory.utils.path_utils import (
    load_text_file,
    find_encoded_file,
    find_question_file,
    list_questions,
    list_datatypes,
    list_guides,
    get_output_path,
    ensure_dir,
    find_project_root
)


class TestPathUtils:
    """Test utility functions for path handling and file discovery."""

    @pytest.fixture
    def temp_structure(self):
        """Create a temporary directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create encoded files
            encoded_dir = temp_path / "encoded" / "test_exam"
            encoded_dir.mkdir(parents=True)
            
            # Create files directly in the encoded_dir (simpler structure)
            (encoded_dir / "Q1a.mei").write_text("<mei>test</mei>")
            (encoded_dir / "Q2b.mei").write_text("<mei>test2</mei>")
            (encoded_dir / "Q1a.abc").write_text("X:1\nT:Test")
            
            # Create question files
            questions_dir = temp_path / "questions"
            questions_dir.mkdir()
            
            (questions_dir / "Q1a.context.txt").write_text("Context question")
            (questions_dir / "Q1a.nocontext.txt").write_text("No context question")  
            (questions_dir / "Q2b.nocontext.txt").write_text("Another question")
            
            # Create guides
            guides_dir = temp_path / "guides"
            guides_dir.mkdir()
            (guides_dir / "harmonic_analysis.txt").write_text("Harmonic guide")
            (guides_dir / "form_analysis.txt").write_text("Form guide")
            
            yield temp_path

    def test_load_text_file(self, temp_structure):
        """Test loading text files."""
        test_file = temp_structure / "test.txt"
        test_file.write_text("Test content")
        
        content = load_text_file(test_file)
        assert content == "Test content"

    def test_load_text_file_not_exists(self, temp_structure):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_text_file(temp_structure / "nonexistent.txt")

    def test_find_encoded_file(self, temp_structure):
        """Test finding encoded music files."""
        encoded_dir = temp_structure / "encoded" / "test_exam"
        
        # Find MEI file
        mei_file = find_encoded_file("Q1a", "mei", encoded_dir)
        assert mei_file.name == "Q1a.mei"
        assert mei_file.exists()
        
        # Find ABC file
        abc_file = find_encoded_file("Q1a", "abc", encoded_dir)
        assert abc_file.name == "Q1a.abc"
        assert abc_file.exists()

    def test_find_encoded_file_not_found(self, temp_structure):
        """Test finding non-existent encoded file."""
        encoded_dir = temp_structure / "encoded" / "test_exam"
        
        with pytest.raises(FileNotFoundError):
            find_encoded_file("Q99", "mei", encoded_dir)

    def test_find_question_file_context(self, temp_structure):
        """Test finding question file with context."""
        questions_dir = temp_structure / "questions"
        
        question_file = find_question_file("Q1a", True, questions_dir)
        assert question_file.name == "Q1a.context.txt"
        assert question_file.exists()

    def test_find_question_file_no_context(self, temp_structure):
        """Test finding question file without context."""
        questions_dir = temp_structure / "questions"
        
        question_file = find_question_file("Q1a", False, questions_dir)
        assert question_file.name == "Q1a.nocontext.txt"
        assert question_file.exists()

    def test_find_question_file_not_required(self, temp_structure):
        """Test finding non-existent question file when not required."""
        questions_dir = temp_structure / "questions"
        
        question_file = find_question_file("Q99", True, questions_dir, required=False)
        assert question_file is None

    def test_list_questions(self, temp_structure):
        """Test listing available questions."""
        questions_dir = temp_structure / "questions"
        
        questions = list_questions(questions_dir)
        # The list_questions function gets stems, so:
        # "Q1a.context.txt" -> "Q1a.context"
        # "Q1a.nocontext.txt" -> "Q1a.nocontext"
        # "Q2b.nocontext.txt" -> "Q2b.nocontext"
        expected_stems = {"Q1a.context", "Q1a.nocontext", "Q2b.nocontext"}
        assert expected_stems.issubset(set(questions))

    def test_list_datatypes(self, temp_structure):
        """Test listing available data types."""
        # Use the main encoded dir, not a subdirectory
        encoded_dir = temp_structure / "encoded"
        
        # Create datatype subdirectories like our real structure
        mei_dir = encoded_dir / "mei"
        abc_dir = encoded_dir / "abc"
        mei_dir.mkdir(parents=True)
        abc_dir.mkdir(parents=True)
        
        # Add some files to make them valid
        (mei_dir / "Q1a.mei").write_text("<mei>test</mei>")
        (abc_dir / "Q1a.abc").write_text("X:1\nT:Test")
        
        datatypes = list_datatypes(encoded_dir)
        assert "mei" in datatypes
        assert "abc" in datatypes
        assert len(datatypes) == 2

    def test_list_guides(self, temp_structure):
        """Test listing available guides."""
        guides_dir = temp_structure / "guides"
        
        guides = list_guides(guides_dir)
        assert "harmonic_analysis" in guides
        assert "form_analysis" in guides
        assert len(guides) == 2

    def test_get_output_path(self, temp_structure):
        """Test generating output file paths."""
        outputs_dir = temp_structure / "outputs"
        
        output_path = get_output_path(
            outputs_dir=outputs_dir,
            model_name="TestModel",
            question_number="Q1a",
            datatype="mei",
            context=True
        )
        
        expected = outputs_dir / "TestModel" / "Q1a_mei_context_1.txt"
        assert output_path == expected

    def test_get_output_path_no_context(self, temp_structure):
        """Test generating output file paths without context."""
        outputs_dir = temp_structure / "outputs"
        
        output_path = get_output_path(
            outputs_dir=outputs_dir,
            model_name="TestModel",
            question_number="Q2b",
            datatype="abc",
            context=False
        )
        
        expected = outputs_dir / "TestModel" / "Q2b_abc_nocontext_1.txt"
        assert output_path == expected

    def test_find_project_root(self):
        """Test finding project root directory."""
        # This should find the project root containing pyproject.toml
        root = find_project_root()
        assert root.is_dir()
        assert (root / "pyproject.toml").exists()


class TestDataIntegrity:
    """Test data file integrity and structure."""

    def test_data_directory_exists(self):
        """Test that fux-counterpoint dataset directory exists in the project."""
        root = find_project_root()
        data_dir = root / "data" / "fux-counterpoint"
        assert data_dir.exists(), "fux-counterpoint dataset missing"
        assert data_dir.is_dir()

    def test_required_subdirectories_exist(self):
        """Test that core subdirectories exist for fux-counterpoint."""
        root = find_project_root()
        data_dir = root / "data" / "fux-counterpoint"
        required_dirs = ["encoded", "prompts", "guides"]
        for name in required_dirs:
            d = data_dir / name
            assert d.exists(), f"Missing required directory: {name}"
            assert d.is_dir()

    def test_base_prompts_exist(self):
        """Test that available base prompt files exist for supported types."""
        root = find_project_root()
        base_dir = root / "data" / "fux-counterpoint" / "prompts" / "base"
        assert base_dir.exists()
        # Only mei & musicxml currently required
        for stem in ["base_mei", "base_musicxml"]:
            md_file = base_dir / f"{stem}.md"
            assert md_file.exists(), f"Missing required file: {md_file.name}"
            assert md_file.stat().st_size > 0

    def test_sample_encoded_files_exist(self):
        """Test that encoded mei & musicxml files exist in fux dataset."""
        root = find_project_root()
        encoded_dir = root / "data" / "fux-counterpoint" / "encoded"
        assert encoded_dir.exists()
        for sub in ["mei", "musicxml"]:
            d = encoded_dir / sub
            assert d.exists(), f"Missing encoded/{sub} directory"
            files = list(d.glob(f"*.{sub if sub!='musicxml' else 'musicxml'}"))
            assert files, f"No {sub} files found"

    def test_file_naming_conventions(self):
        """Basic naming checks for supported datatypes in fux dataset."""
        root = find_project_root()
        encoded_dir = root / "data" / "fux-counterpoint" / "encoded"
        if not encoded_dir.exists():
            pytest.skip("fux-counterpoint encoded directory missing")
        for datatype_dir in encoded_dir.iterdir():
            if not datatype_dir.is_dir():
                continue
            if datatype_dir.name not in {"mei", "musicxml"}:
                continue
            for file_path in datatype_dir.iterdir():
                if not file_path.is_file():
                    continue
                if datatype_dir.name == "mei":
                    assert file_path.suffix == ".mei"
                elif datatype_dir.name == "musicxml":
                    assert file_path.suffix == ".musicxml"
