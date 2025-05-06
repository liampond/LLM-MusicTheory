# utils/path_utils.py

from pathlib import Path

def load_text_file(path: Path) -> str:
    with open(path, "r") as f:
        return f.read().strip()

def find_encoded_file(question_number: str, datatype: str, encoded_dir: Path) -> Path:
    ext_map = {
        "mei": ".mei",
        "musicxml": ".musicxml",
        "abc": ".abc",
        "humdrum": ".krn"
    }
    ext = ext_map[datatype.lower()]
    return encoded_dir / f"{question_number}{ext}"
