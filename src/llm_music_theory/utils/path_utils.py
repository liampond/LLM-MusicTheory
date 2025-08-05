from pathlib import Path
from typing import List, Optional


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Find the project root by looking for pyproject.toml file.
    Returns the directory containing pyproject.toml.
    """
    if start_path is None:
        start_path = Path(__file__).parent
    
    current = start_path.resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    
    raise FileNotFoundError("Could not find project root with pyproject.toml")


def load_text_file(path: Path) -> str:
    """
    Read a text file and return its contents stripped of leading/trailing whitespace.
    Raises FileNotFoundError if the file does not exist.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Expected file at {path}, but none was found.")
    return path.read_text(encoding="utf-8").strip()


def find_encoded_file(
    question_number: str,
    datatype: str,
    encoded_dir: Path,
    required: bool = True
) -> Optional[Path]:
    """
    Locate the encoded music file for a given question and format.
    - question_number: e.g. "Q1a"
    - datatype: one of ["mei","musicxml","abc","humdrum"]
    - encoded_dir: base folder where encoded files live

    Returns the Path if found, or None if required=False and file is missing.
    Raises ValueError for unsupported datatype.
    Raises FileNotFoundError if required=True and file is missing.
    """
    ext_map = {"mei": ".mei", "musicxml": ".musicxml", "abc": ".abc", "humdrum": ".krn"}
    key = datatype.lower()
    if key not in ext_map:
        raise ValueError(f"Unknown datatype '{datatype}'. Valid options: {list(ext_map)}")
    
    # First try exact match (for backwards compatibility)
    candidate = encoded_dir / f"{question_number}{ext_map[key]}"
    if candidate.exists():
        return candidate
    
    # If exact match not found, search for files containing the question number
    if encoded_dir.exists():
        pattern = f"*{question_number}{ext_map[key]}"
        matches = list(encoded_dir.glob(pattern))
        if matches:
            return matches[0]  # Return first match
    
    if required:
        raise FileNotFoundError(f"No encoded file found for {question_number} in {encoded_dir}")
    return None


def find_question_file(
    question_number: str,
    context: bool,
    questions_dir: Path,
    required: bool = True
) -> Optional[Path]:
    """
    Locate the question prompt file (contextual or not) for a given question.
    - context=True  → looks for Q1a.context.txt or *Q1a*ContextPrompt.txt
    - context=False → looks for Q1a.nocontext.txt or *Q1a*NoContextPrompt.txt

    Returns the Path if found, or None if required=False and file is missing.
    Raises FileNotFoundError if required=True and file is missing.
    """
    # First try the exact match format (for backwards compatibility)
    suffix = "context" if context else "nocontext"
    candidate = questions_dir / f"{question_number}.{suffix}.txt"
    if candidate.exists():
        return candidate
    
    # If exact match not found, search for files containing the question number
    if questions_dir.exists():
        if context:
            pattern = f"*{question_number}*ContextPrompt.txt"
        else:
            pattern = f"*{question_number}*NoContextPrompt.txt"
        
        matches = list(questions_dir.glob(pattern))
        if matches:
            return matches[0]  # Return first match
    
    if required:
        raise FileNotFoundError(f"Question file not found for {question_number} in {questions_dir}")
    return None


def list_questions(questions_dir: Path) -> List[str]:
    """
    Return all unique question IDs in the folder, e.g. ["Q1a","Q1b",...].
    Scans both context and nocontext variants.
    """
    return sorted(
        set(
            f.stem
            for f in questions_dir.rglob("*.txt")
        )
    )


def list_datatypes(encoded_dir: Path) -> List[str]:
    """
    Return all supported datatypes based on file extensions present,
    e.g. ["mei","musicxml","abc","humdrum"].
    Searches both direct files and in subdirectories.
    """
    ext_map = {".mei": "mei", ".musicxml": "musicxml", ".krn": "humdrum", ".abc": "abc"}
    found = set()
    
    if not encoded_dir.exists():
        return []
    
    # Search for files directly in the directory
    for file in encoded_dir.iterdir():
        if file.is_file():
            dt = ext_map.get(file.suffix)
            if dt:
                found.add(dt)
    
    # Search for subdirectories that match datatypes or contain files with matching extensions
    for subdir in encoded_dir.iterdir():
        if subdir.is_dir():
            # Check if the directory name itself is a datatype
            if subdir.name in ext_map.values():
                found.add(subdir.name)
            else:
                # Search for files in subdirectories
                for file in subdir.rglob("*"):
                    if file.is_file():
                        dt = ext_map.get(file.suffix)
                        if dt:
                            found.add(dt)
    
    return sorted(found)


def list_guides(guides_dir: Path) -> List[str]:
    """
    Return all guide topics available (filenames without .txt),
    e.g. ["intervals","intervals.determine_top_note",...].
    """
    return sorted([f.stem for f in guides_dir.glob("*.txt")])


def ensure_dir(path: Path) -> None:
    """
    Ensure that the given directory exists, creating it (and parents) if needed.
    """
    path.mkdir(parents=True, exist_ok=True)


def get_output_path(
    outputs_dir: Path,
    model_name: str,
    question_number: str,
    datatype: str,
    context: bool,
    ext: str = ".txt"
) -> Path:
    """
    Build an output file path for storing model responses.
    e.g. outputs/ChatGPT/Q1a_mei_context.txt
    Automatically creates the model-specific folder.
    """
    context_flag = "context" if context else "nocontext"
    model_folder = outputs_dir / model_name
    ensure_dir(model_folder)
    filename = f"{question_number}_{datatype}_{context_flag}{ext}"
    return model_folder / filename
