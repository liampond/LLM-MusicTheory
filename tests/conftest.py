# conftest.py - Centralized Test Configuration
"""
Shared pytest configuration and fixtures for the LLM-MusicTheory test suite.

This file provides:
- Common fixtures used across multiple test files
- Test configuration and markers
- Mock utilities and test data generators
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import types
from typing import Dict, Any

# Ensure the package is importable in a src/ layout
_TESTS_DIR = Path(__file__).resolve().parent
_ROOT = _TESTS_DIR.parent
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from llm_music_theory.models.base import LLMInterface, PromptInput


# ===============================================================================
# SHARED FIXTURES
# ===============================================================================

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing that captures queries without API calls."""
    
    class MockLLM(LLMInterface):
        def __init__(self):
            self.last_query = None
            self.captured_queries = []
            self.response = "Mock test response"
        
        def query(self, input: PromptInput) -> str:
            self.last_query = input
            self.captured_queries.append(input)
            return self.response
    
    return MockLLM()


@pytest.fixture
def temp_project_structure():
    """Create a complete temporary project structure for testing.
    
    This fixture creates a realistic project directory structure with all
    necessary files for testing, eliminating dependencies on real project data.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create main project structure
        src_dir = temp_path / "src" / "llm_music_theory"
        src_dir.mkdir(parents=True)

        data_dir = temp_path / "data" / "RCM6"  # legacy dataset name (formerly LLM-RCM)
        data_dir.mkdir(parents=True)

        # Create encoded music files
        encoded_dir = data_dir / "encoded"
        for datatype in ["mei", "musicxml", "abc", "humdrum"]:
            datatype_dir = encoded_dir / datatype
            datatype_dir.mkdir(parents=True)
            
            # Create sample files
            if datatype == "mei":
                (datatype_dir / "Q1a.mei").write_text("<mei><music>test</music></mei>")
                (datatype_dir / "Q1b.mei").write_text("<mei><music>test2</music></mei>")
            elif datatype == "musicxml":
                (datatype_dir / "Q1a.musicxml").write_text("<?xml version='1.0'?><score-partwise></score-partwise>")
                (datatype_dir / "Q1b.musicxml").write_text("<?xml version='1.0'?><score-partwise></score-partwise>")
            elif datatype == "abc":
                (datatype_dir / "Q1a.abc").write_text("X:1\nT:Test\nK:C\nCDEF|")
                (datatype_dir / "Q1b.abc").write_text("X:1\nT:Test2\nK:G\nGABc|")
            elif datatype == "humdrum":
                (datatype_dir / "Q1a.krn").write_text("**kern\n4c\n4d\n*-")
                (datatype_dir / "Q1b.krn").write_text("**kern\n4g\n4a\n*-")
        
        # Create prompt templates
        prompts_dir = data_dir / "prompts"
        base_dir = prompts_dir / "base"
        base_dir.mkdir(parents=True)
        
        # Base format prompts
        (base_dir / "system_prompt.txt").write_text("You are a music theory expert.")
        (base_dir / "base_mei.txt").write_text("Analyze this MEI notation.")
        (base_dir / "base_musicxml.txt").write_text("Analyze this MusicXML notation.")
        (base_dir / "base_abc.txt").write_text("Analyze this ABC notation.")
        (base_dir / "base_humdrum.txt").write_text("Analyze this Humdrum notation.")
        
        # Question files
        questions_context_dir = prompts_dir / "questions" / "context"
        questions_nocontext_dir = prompts_dir / "questions" / "no_context"
        questions_context_dir.mkdir(parents=True)
        questions_nocontext_dir.mkdir(parents=True)
        
        (questions_context_dir / "Q1a.txt").write_text("What is the key signature? Consider the context.")
        (questions_context_dir / "Q1b.txt").write_text("Identify the time signature? Consider the context.")
        (questions_nocontext_dir / "Q1a.txt").write_text("What is the key signature?")
        (questions_nocontext_dir / "Q1b.txt").write_text("Identify the time signature?")
        
        # Guide files
        guides_dir = data_dir / "guides"
        guides_dir.mkdir(parents=True)
        (guides_dir / "key_signatures.txt").write_text("Key signatures appear at the beginning of the staff.")
        (guides_dir / "time_signatures.txt").write_text("Time signatures indicate the meter.")
        
        # Create pyproject.toml for project root detection
        (temp_path / "pyproject.toml").write_text("""
[tool.poetry]
name = "test-project"
version = "0.1.0"
""")
        
        # Create outputs directory
        outputs_dir = temp_path / "outputs"
        outputs_dir.mkdir()
        
        yield {
            'root': temp_path,
            'src': src_dir,
            'data': data_dir,
            'base_dirs': {
                "encoded": encoded_dir,
                "prompts": prompts_dir,
                "questions": prompts_dir / "questions",
                "guides": guides_dir,
                "outputs": outputs_dir,
            }
        }


@pytest.fixture
def temp_project_dir(temp_project_structure):
    """Compatibility alias: return project root Path for tests expecting temp_project_dir."""
    return temp_project_structure['root']


@pytest.fixture
def mock_api_keys(monkeypatch):
    """Mock all API keys to prevent real API calls and missing key errors."""
    mock_keys = {
        "openai": "test-openai-key",
        "anthropic": "test-anthropic-key",
        "google": "test-google-key", 
        "deepseek": "test-deepseek-key"
    }
    
    # Set environment variables
    for key, value in mock_keys.items():
        monkeypatch.setenv(f"{key.upper()}_API_KEY", value)
    
    # Mock the settings module
    monkeypatch.setattr("llm_music_theory.config.settings.API_KEYS", mock_keys)
    
    return mock_keys


@pytest.fixture
def sample_prompt_input():
    """Create a sample PromptInput for testing."""
    return PromptInput(
        system_prompt="You are a music theory expert.",
        user_prompt="Analyze this musical excerpt: <mei>test</mei>",
        temperature=0.7,
        max_tokens=500
    )


# ===============================================================================
# MOCK UTILITIES
# ===============================================================================

class MockResponse:
    """Utility class for mocking API responses."""
    
    def __init__(self, content: str):
        self.content = content
        self.choices = [Mock(message=Mock(content=content))]


def create_mock_openai_client(response_content: str = "Mock OpenAI response"):
    """Create a mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = MockResponse(response_content)
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def create_mock_anthropic_client(response_content: str = "Mock Anthropic response"):
    """Create a mock Anthropic client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text=response_content)]
    mock_client.messages.create.return_value = mock_response
    return mock_client


# ===============================================================================
# TEST CONFIGURATION
# ===============================================================================

# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "comprehensive: mark test as a comprehensive/end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring API mocking"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and name."""
    for item in items:
        # Mark tests by file
        if "test_models" in item.nodeid:
            item.add_marker(pytest.mark.api)
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_comprehensive" in item.nodeid:
            item.add_marker(pytest.mark.comprehensive)
        elif "test_runner" in item.nodeid or "test_prompt" in item.nodeid or "test_path" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            
        # Mark slow tests
        if "comprehensive" in item.name or "integration" in item.name:
            item.add_marker(pytest.mark.slow)


def pytest_ignore_collect(path, config):
    """Ignore legacy duplicate tests to avoid double coverage and conflicts."""
    p = str(path)
    if p.endswith("_fixed.py") or p.endswith("_new.py"):
        return True
    return False


# ===============================================================================
# ENVIRONMENT SETUP
# ===============================================================================

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Automatically set up a clean test environment for all tests."""
    # Ensure no real API keys are used
    api_key_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "GOOGLE_API_KEY",
        "DEEPSEEK_API_KEY"
    ]
    
    for var in api_key_vars:
        if var in os.environ:
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv(var, f"test-{var.lower()}")


@pytest.fixture(autouse=True)
def stub_external_sdks(monkeypatch):
    """Provide lightweight stubs for third-party SDKs used by model classes.

    This avoids import-time failures for optional dependencies during tests.
    """
    # Stub 'openai' with minimal OpenAI client
    if 'openai' not in sys.modules:
        openai_mod = types.ModuleType('openai')

        class _OpenAI:
            def __init__(self, *args, **kwargs):
                self.chat = types.SimpleNamespace(
                    completions=types.SimpleNamespace(
                        create=lambda **kwargs: types.SimpleNamespace(
                            choices=[types.SimpleNamespace(
                                message=types.SimpleNamespace(content="stubbed response")
                            )]
                        )
                    )
                )

        openai_mod.OpenAI = _OpenAI
        sys.modules['openai'] = openai_mod

    # Stub 'anthropic' with minimal Anthropic client
    if 'anthropic' not in sys.modules:
        anthropic_mod = types.ModuleType('anthropic')

        class _Anthropic:
            def __init__(self, *args, **kwargs):
                self.messages = types.SimpleNamespace(
                    create=lambda **kwargs: types.SimpleNamespace(
                        content=[types.SimpleNamespace(text="stubbed response")]
                    )
                )

        anthropic_mod.Anthropic = _Anthropic
        sys.modules['anthropic'] = anthropic_mod

    # Stub 'google.genai' under top-level 'google' package
    # Ensure top-level 'google' package exists
    google_pkg = sys.modules.get('google')
    if google_pkg is None:
        google_pkg = types.ModuleType('google')
        sys.modules['google'] = google_pkg

    # Create 'google.genai' submodule if missing
    if 'google.genai' not in sys.modules:
        genai_mod = types.ModuleType('google.genai')

        class _ModelsNS:
            def generate_content(self, **kwargs):
                return types.SimpleNamespace(text="stubbed response")

        class _Client:
            def __init__(self, *args, **kwargs):
                self.models = _ModelsNS()

        genai_mod.Client = _Client

        # Attach as attribute of 'google' package and register in sys.modules
        setattr(google_pkg, 'genai', genai_mod)
        sys.modules['google.genai'] = genai_mod


# ===============================================================================
# TEST DATA GENERATORS
# ===============================================================================

def generate_test_music_data(format_type: str, question_id: str = "Q1a") -> str:
    """Generate synthetic music data for testing."""
    if format_type == "mei":
        return f"""<mei xmlns="http://www.music-encoding.org/ns/mei">
    <music>
        <body>
            <mdiv>
                <score>
                    <scoreDef>
                        <staffGrp>
                            <staffDef n="1" lines="5" clef.shape="G" clef.line="2"/>
                        </staffGrp>
                    </scoreDef>
                    <section>
                        <measure n="1">
                            <staff n="1">
                                <layer n="1">
                                    <note pname="c" oct="4" dur="4"/>
                                </layer>
                            </staff>
                        </measure>
                    </section>
                </score>
            </mdiv>
        </body>
    </music>
</mei>"""
    elif format_type == "musicxml":
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="3.1">
    <part-list>
        <score-part id="P1">
            <part-name>Test Part</part-name>
        </score-part>
    </part-list>
    <part id="P1">
        <measure number="1">
            <note>
                <pitch>
                    <step>C</step>
                    <octave>4</octave>
                </pitch>
                <duration>4</duration>
                <type>quarter</type>
            </note>
        </measure>
    </part>
</score-partwise>"""
    elif format_type == "abc":
        return f"""X:1
T:Test Tune for {question_id}
M:4/4
L:1/4
K:C
C D E F | G A B c |"""
    elif format_type == "humdrum":
        return f"""**kern
*clefG2
*k[]
*M4/4
4c
4d
4e
4f
*-"""
    else:
        raise ValueError(f"Unknown format type: {format_type}")
