"""Filesystem and path discovery helpers.

Design goals:
    * Keep IO minimal (avoid repeated directory scans where possible).
    * Provide clear errors for missing required artifacts while allowing
        optional lookups (required=False) to return None gracefully.
    * Support legacy naming conventions while nudging toward the new layout.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Set, Iterable, Dict

__all__ = [
        "find_project_root",
        "load_text_file",
        "find_encoded_file",
        "find_question_file",
        "list_questions",
        "list_file_ids",
        "list_datatypes",
        "list_guides",
        "ensure_dir",
        "get_output_path",
]

_ROOT_CACHE: Optional[Path] = None
_DATATYPE_EXT: Dict[str, str] = {"mei": ".mei", "musicxml": ".musicxml", "abc": ".abc", "humdrum": ".krn"}


def _normalize_datatype(datatype: str) -> str:
        key = datatype.lower().strip()
        if key not in _DATATYPE_EXT:
                raise ValueError(f"Unknown datatype '{datatype}'. Valid: {sorted(_DATATYPE_EXT)}")
        return key


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """Locate and cache the project root containing ``pyproject.toml``.

    Parameters
    ----------
    start_path: Path | None
        Starting directory (defaults to this file's parent). Accepts a file path.
    """
    global _ROOT_CACHE
    if _ROOT_CACHE and _ROOT_CACHE.exists():  # pragma: no cover (cache branch)
        return _ROOT_CACHE
    if start_path is None:
        start_path = Path(__file__).parent
    start_path = start_path if start_path.is_dir() else start_path.parent
    current = start_path.resolve()
    while True:
        if (current / "pyproject.toml").exists():
            _ROOT_CACHE = current
            return current
        if current.parent == current:
            break
        current = current.parent
    raise FileNotFoundError("Could not locate project root containing pyproject.toml")


def load_text_file(path: Path) -> str:
    """Read UTF‑8 text file returning stripped contents.

    Raises
    ------
    FileNotFoundError
        If the path is not an existing file.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Expected file at {path} but none was found")
    return path.read_text(encoding="utf-8").strip()


def find_encoded_file(
    question_number: str,
    datatype: str,
    encoded_dir: Path,
    required: bool = True,
) -> Optional[Path]:
    """Locate encoded music file for ``question_number`` with given ``datatype``.

    Returns the first match (exact first, fallback glob) or None if ``required`` is False.
    Raises ValueError for unsupported datatypes & FileNotFoundError when required and missing.
    """
    key = _normalize_datatype(datatype)
    ext = _DATATYPE_EXT[key]
    candidate = encoded_dir / f"{question_number}{ext}"
    if candidate.exists():
        return candidate
    if encoded_dir.exists():
        matches = list(encoded_dir.glob(f"*{question_number}{ext}"))
        if matches:
            return matches[0]
    if required:
        raise FileNotFoundError(f"No encoded file found for {question_number} in {encoded_dir}")
    return None


def find_question_file(
    question_number: str,
    context: bool,
    questions_dir: Path,
    required: bool = True,
) -> Optional[Path]:
    """Locate contextual / non‑contextual question prompt file.

    Supports both exact legacy naming and pattern-based fallback.
    """
    suffix = "context" if context else "nocontext"
    candidate = questions_dir / f"{question_number}.{suffix}.txt"
    if candidate.exists():
        return candidate
    if questions_dir.exists():
        pattern = f"*{question_number}*{'Context' if context else 'NoContext'}Prompt.txt"
        matches = list(questions_dir.glob(pattern))
        if matches:
            return matches[0]
    if required:
        raise FileNotFoundError(f"Question file not found for {question_number} in {questions_dir}")
    return None


def list_questions(questions_dir: Path) -> List[str]:
    """Return sorted stems of all ``.txt`` question prompt files (legacy datasets)."""
    if not questions_dir.exists():
        return []
    return sorted({f.stem for f in questions_dir.rglob("*.txt")})


def list_file_ids(encoded_dir: Path) -> List[str]:
    """Return unique filename stems under each datatype subdirectory."""
    if not encoded_dir.exists():
        return []
    ids: Set[str] = set()
    for sub in encoded_dir.iterdir():
        if not sub.is_dir():
            continue
        for f in sub.iterdir():
            if f.is_file():
                ids.add(f.stem)
    return sorted(ids)


def list_datatypes(encoded_dir: Path) -> List[str]:
    """Return supported datatypes inferred from populated subdirectories."""
    if not encoded_dir.exists():
        return []
    found: Set[str] = set()
    for subdir in encoded_dir.iterdir():
        if subdir.is_dir() and subdir.name in _DATATYPE_EXT:
            try:
                next(subdir.iterdir())  # at least one entry
            except StopIteration:  # empty directory
                continue
            found.add(subdir.name)
    return sorted(found)


def list_guides(guides_dir: Path) -> List[str]:
    """Return stems of all guide ``.txt`` files (non‑recursive)."""
    if not guides_dir.exists():
        return []
    return sorted([f.stem for f in guides_dir.glob("*.txt") if f.is_file()])


def ensure_dir(path: Path) -> None:
    """Create directory (and parents) if missing (idempotent)."""
    path.mkdir(parents=True, exist_ok=True)


def get_output_path(
    outputs_dir: Path,
    model_name: str,
    file_id: Optional[str] = None,
    datatype: str = "mei",
    context: bool = False,
    dataset: Optional[str] = None,
    ext: str = ".txt",
    question_number: Optional[str] = None,
) -> Path:
    """Return path for model output file.

    Pattern: ``outputs/<Model>/<dataset>_<file_id>_<datatype>_<context|nocontext><ext>``
    (dataset prefix omitted if not provided for backward compatibility).
    """
    fid = file_id or question_number
    if not fid:
        raise ValueError("file_id (or legacy question_number) is required for output path")
    context_flag = "context" if context else "nocontext"
    dataset_prefix = f"{dataset}_" if dataset else ""
    filename = f"{dataset_prefix}{fid}_{datatype}_{context_flag}{ext}"
    model_folder = outputs_dir / model_name
    ensure_dir(model_folder)
    return model_folder / filename
