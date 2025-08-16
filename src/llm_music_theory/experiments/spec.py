from __future__ import annotations

"""Experiment specification dataclasses and YAML loader (prototype).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import datetime as _dt
import json
import yaml

from llm_music_theory.prompts.prompt_builder import PromptBuilder
from llm_music_theory.core.dispatcher import get_llm, list_available_models
from llm_music_theory.models.base import PromptInput
from llm_music_theory.utils.path_utils import find_encoded_file


@dataclass
class Question:
    id: str
    enabled: bool
    section: str
    order: int
    blocks: List[str] = field(default_factory=list)
    example_refs: List[str] = field(default_factory=list)
    evaluation: Dict[str, Any] = field(default_factory=dict)
    temperature: Optional[float] = None
    assembled_markdown: Optional[str] = None


@dataclass
class Experiment:
    slug: str
    title: str
    description: str
    models: List[str]
    datatypes: List[str]
    pieces: List[str]
    questions: List[Question]
    sections: List[str]
    dry_run: bool
    output_options: Dict[str, Any]
    root: Path
    default_temperature: float = 0.0

    def enabled_questions(self) -> List[Question]:
        return [q for q in self.questions if q.enabled]


def _read_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):  # pragma: no cover
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def _load_examples_file(path: Path) -> Dict[str, Dict[str, Any]]:
    data = _read_yaml(path)
    examples = data.get("examples") or {}
    if not isinstance(examples, dict):
        raise ValueError(f"'examples' must be a mapping in {path}")
    return examples


def _resolve_example_ref(ref: str, blocks_dir: Path) -> Optional[str]:
    if ":" not in ref:
        raise ValueError(f"Invalid example ref (expected file.yaml:example_id): {ref}")
    file_part, ex_id = ref.split(":", 1)
    file_path = blocks_dir / file_part
    if not file_path.exists():
        raise FileNotFoundError(f"Examples file not found: {file_path}")
    examples = _load_examples_file(file_path)
    ex = examples.get(ex_id)
    if not ex:
        raise ValueError(f"Example id '{ex_id}' not found in {file_path}")
    if not ex.get("enabled", True):
        return None
    text = ex.get("text")
    if not isinstance(text, str):
        raise ValueError(f"Example '{ex_id}' missing text in {file_path}")
    return text.strip()


def _load_block(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _assemble_question_markdown(q: Question, blocks_dir: Path) -> str:
    parts: List[str] = []
    for rel in q.blocks:
        block_path = blocks_dir / rel
        if not block_path.exists():
            raise FileNotFoundError(f"Block file not found: {block_path}")
        parts.append(_load_block(block_path))
    for ref in q.example_refs:
        txt = _resolve_example_ref(ref, blocks_dir)
        if txt:
            parts.append(txt)
    header = f"### Question: {q.id}"
    return "\n\n".join([header, *[p for p in parts if p]])


def load_experiment(path: Path) -> Experiment:
    data = _read_yaml(path)
    slug = str(data.get("slug") or path.stem)
    title = str(data.get("title") or slug)
    description = str(data.get("description") or "")
    models_raw = data.get("models") or []
    if models_raw == "all":
        models = list_available_models()
    else:
        models = [m.strip() for m in models_raw]
    datatypes = [d.strip() for d in (data.get("datatypes") or [])]
    pieces = [p.strip() for p in (data.get("pieces") or [])]
    sections = [s.strip() for s in (data.get("sections") or [])]
    dry_run = bool(data.get("dry_run", False))
    default_temp = float(data.get("temperature", 0.0))
    output_options = data.get("output") or {}
    questions_data = data.get("questions") or []
    root = path.parent.parent

    questions: List[Question] = []
    for qd in questions_data:
        if not isinstance(qd, dict):
            continue
        q = Question(
            id=str(qd.get("id")),
            enabled=bool(qd.get("enabled", True)),
            section=str(qd.get("section") or "General"),
            order=int(qd.get("order", 0)),
            blocks=[str(b) for b in (qd.get("blocks") or [])],
            example_refs=[str(e) for e in (qd.get("examples") or [])],
            evaluation=qd.get("evaluation") or {},
            temperature=(float(qd.get("temperature")) if qd.get("temperature") is not None else None),
        )
        questions.append(q)

    blocks_dir = root / "blocks"
    for q in questions:
        if q.enabled:
            q.assembled_markdown = _assemble_question_markdown(q, blocks_dir)

    return Experiment(
        slug=slug,
        title=title,
        description=description,
        models=models,
        datatypes=datatypes,
        pieces=pieces,
        questions=questions,
        sections=sections,
        dry_run=dry_run,
        output_options=output_options,
        root=root,
        default_temperature=default_temp,
    )


def build_prompt_input(exp: Experiment, piece_id: str, datatype: str, question: Question) -> Tuple[PromptInput, Dict[str, Any]]:
    prompts_base = exp.root / "prompts" / "base"
    system_prompt_path = prompts_base / "system_prompt.txt"
    system_prompt = system_prompt_path.read_text(encoding="utf-8").strip() if system_prompt_path.exists() else "You are a helpful music theory assistant."
    format_prompt_path = None
    for ext in ("md", "txt"):
        candidate = prompts_base / f"base_{datatype}.{ext}"
        if candidate.exists():
            format_prompt_path = candidate
            break
    if not format_prompt_path:
        raise FileNotFoundError(f"Missing base format prompt base_{datatype}.* in {prompts_base}")
    format_prompt = format_prompt_path.read_text(encoding="utf-8").strip()

    encoded_dir = exp.root / "encoded" / datatype
    encoded_path = find_encoded_file(piece_id, datatype, encoded_dir, required=True)
    encoded_data = encoded_path.read_text(encoding="utf-8")

    q_md = question.assembled_markdown or ""
    piece_header = f"### Piece: {piece_id}\n"
    question_prompt = "\n\n".join([piece_header, q_md]).strip()

    ordering = ["question_prompt", "format_prompt", "encoded_data"]
    section_headers = {
        "question_prompt": "Task & Examples",
        "format_prompt": f"Output Format ({datatype.upper()})",
        "encoded_data": f"Encoded {datatype.upper()} Source",
    }

    builder = PromptBuilder(
        system_prompt=system_prompt,
        format_specific_user_prompt=format_prompt,
        encoded_data=encoded_data,
        guides=[],
        question_prompt=question_prompt,
        temperature=question.temperature or exp.default_temperature,
        model_name=None,
        ordering=ordering,
        section_headers=section_headers,
    )
    prompt_input = builder.build()
    meta = {
        "piece_id": piece_id,
        "datatype": datatype,
        "question_id": question.id,
        "temperature": prompt_input.temperature,
        "section": question.section,
    }
    return prompt_input, meta


def ensure_output_dir(exp: Experiment) -> Path:
    base = Path(exp.output_options.get("directory") or "outputs/experiments")
    base.mkdir(parents=True, exist_ok=True)
    if exp.output_options.get("directory"):
        return base
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = base / f"{stamp}_{exp.slug}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def run_experiment(exp: Experiment) -> Path:
    out_dir = ensure_output_dir(exp)
    manifest: Dict[str, Any] = {
        "slug": exp.slug,
        "title": exp.title,
        "description": exp.description,
        "models": exp.models,
        "datatypes": exp.datatypes,
        "pieces": exp.pieces,
        "timestamp": _dt.datetime.utcnow().isoformat() + "Z",
        "dry_run": exp.dry_run,
        "questions": [],
    }
    for q in exp.enabled_questions():
        q_entry = {"id": q.id, "section": q.section, "order": q.order, "evaluation": q.evaluation, "runs": []}
        for piece in exp.pieces:
            for dt in exp.datatypes:
                prompt_input, meta = build_prompt_input(exp, piece, dt, q)
                for model_name in exp.models:
                    run_meta = {**meta, "model": model_name}
                    file_stem = f"{model_name}__{q.id}__{piece}__{dt}"
                    if exp.output_options.get("markdown_preview", True):
                        (out_dir / f"{file_stem}.prompt.md").write_text(prompt_input.user_prompt, encoding="utf-8")
                    if exp.dry_run:
                        run_meta["status"] = "skipped (dry_run)"
                    else:
                        model = get_llm(model_name)
                        response = model.query(prompt_input)
                        (out_dir / f"{file_stem}.response.txt").write_text(response, encoding="utf-8")
                        bundle = {"model": model_name, "prompt": prompt_input.user_prompt, "system_prompt": prompt_input.system_prompt, "metadata": run_meta}
                        (out_dir / f"{file_stem}.input.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
                        run_meta["status"] = "completed"
                    q_entry["runs"].append(run_meta)
        manifest["questions"].append(q_entry)
    if exp.output_options.get("json_manifest", True):
        (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_dir

