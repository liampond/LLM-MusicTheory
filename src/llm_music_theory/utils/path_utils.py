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
    """Return stems of all guide ``.txt`` and ``.md`` files (non‑recursive)."""
    if not guides_dir.exists():
        return []
    guides = []
    for ext in ["*.txt", "*.md"]:
        guides.extend([f.stem for f in guides_dir.glob(ext) if f.is_file()])
    return sorted(guides)


def ensure_dir(path: Path) -> None:
    """Create directory (and parents) if missing (idempotent)."""
    path.mkdir(parents=True, exist_ok=True)


def _get_next_run_number(base_path: Path) -> int:
    """Find the next available run number for a given base path."""
    if not base_path.parent.exists():
        return 1
    
    # Extract the base filename pattern (everything before the extension)
    base_name = base_path.stem
    extension = base_path.suffix
    
    # Look for existing files with pattern: base_name_N.extension
    existing_numbers = []
    for existing_file in base_path.parent.iterdir():
        if existing_file.is_file() and existing_file.suffix == extension:
            # Check if it matches our pattern
            name = existing_file.stem
            if name == base_name:
                # This is the base file (no number), treat as run 1
                existing_numbers.append(1)
            elif name.startswith(base_name + "_") and name[len(base_name + "_"):].isdigit():
                # This has a number suffix
                number = int(name[len(base_name + "_"):])
                existing_numbers.append(number)
    
    if not existing_numbers:
        return 1
    
    return max(existing_numbers) + 1


def get_output_path(
    outputs_dir: Path,
    model_name: str,
    file_id: Optional[str] = None,
    datatype: str = "mei",
    context: bool = False,
    guide: Optional[str] = None,
    dataset: Optional[str] = None,
    ext: str = ".txt",
    question_number: Optional[str] = None,
) -> Path:
    """Return path for model output file with folder-based organization.

    Structure: ``outputs/<dataset>/<model>/[context|no-context]/[<guide>/]<file_id>_N<ext>``
    Only creates directories when they're actually needed.
    """
    fid = file_id or question_number
    if not fid:
        raise ValueError("file_id (or legacy question_number) is required for output path")
    
    if dataset:
        # New structure: outputs/dataset/model/context-folder/[guide-folder/]filename
        model_folder = outputs_dir / dataset / model_name
        
        # Create context-based subfolder
        if context:
            context_folder = model_folder / "context"
            if guide:
                # Further organize by guide when one is specified
                final_folder = context_folder / guide
            else:
                # Context enabled but no specific guide (uses all guides)
                final_folder = context_folder / "all-guides"
        else:
            final_folder = model_folder / "no-context"
    else:
        # Legacy structure: outputs/model/filename (with metadata in filename for backward compatibility)
        context_flag = "context" if context else "nocontext"
        guide_suffix = f"_{guide}" if guide else ""
        base_filename = f"{fid}_{datatype}_{context_flag}{guide_suffix}"
        final_folder = outputs_dir / model_name
        
        # Create the base path to check for existing files
        base_path = final_folder / f"{base_filename}{ext}"
        ensure_dir(final_folder)
        
        # Get the next run number for legacy format
        run_number = _get_next_run_number(base_path)
        final_filename = f"{base_filename}_{run_number}{ext}"
        return final_folder / final_filename
    
    # For new structure, create clean filename
    base_filename = f"{fid}"
    
    # Only create the directory when we actually need it
    ensure_dir(final_folder)
    
    # Create the base path to check for existing files
    base_path = final_folder / f"{base_filename}{ext}"
    
    # Get the next run number
    run_number = _get_next_run_number(base_path)
    
    # Create the final filename with run number
    final_filename = f"{base_filename}_{run_number}{ext}"
    return final_folder / final_filename
