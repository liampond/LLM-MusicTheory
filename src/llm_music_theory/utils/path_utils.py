from pathlib import Path
from typing import List, Optional


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
    candidate = encoded_dir / f"{question_number}{ext_map[key]}"
    if not candidate.exists():
        if required:
            raise FileNotFoundError(f"No encoded file found at {candidate}")
        return None
    return candidate


def find_question_file(
    question_number: str,
    context: bool,
    questions_dir: Path,
    required: bool = True
) -> Optional[Path]:
    """
    Locate the question prompt file (contextual or not) for a given question.
    - context=True  → looks for Q1a.context.txt
    - context=False → looks for Q1a.nocontext.txt

    Returns the Path if found, or None if required=False and file is missing.
    Raises FileNotFoundError if required=True and file is missing.
    """
    suffix = "context" if context else "nocontext"
    candidate = questions_dir / f"{question_number}.{suffix}.txt"
    if not candidate.exists():
        if required:
            raise FileNotFoundError(f"Question file not found: {candidate}")
        return None
    return candidate


def list_questions(questions_dir: Path) -> List[str]:
    """
    Return all unique question IDs in the folder, e.g. ["Q1a","Q1b",...].
    Scans both context and nocontext variants.
    """
    ids = set()
    for file in questions_dir.glob("Q*.txt"):
        ids.add(file.stem.split(".")[0])
    return sorted(ids)


def list_datatypes(encoded_dir: Path) -> List[str]:
    """
    Return all supported datatypes based on file extensions present,
    e.g. ["mei","musicxml","abc","humdrum"].
    """
    ext_map = {".mei": "mei", ".musicxml": "musicxml", ".krn": "humdrum", ".abc": "abc"}
    found = set()
    for file in encoded_dir.iterdir():
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
