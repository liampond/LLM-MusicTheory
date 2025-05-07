#!/usr/bin/env python3
# cli/run_batch.py

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.utils.path_utils import list_questions, list_datatypes


def find_project_root(marker_files=("pyproject.toml", ".git")) -> Path:
    """
    Walk upwards from the current working directory to find the project root,
    defined as the first directory containing one of the marker files.
    """
    cwd = Path.cwd()
    for parent in (cwd, *cwd.parents):
        if any((parent / m).exists() for m in marker_files):
            return parent
    raise RuntimeError("Could not locate project root")


def load_project_env():
    """
    Load environment variables from the .env at the project root.
    """
    root = find_project_root()
    dotenv_path = root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    else:
        logging.warning(f"No .env found at {dotenv_path}; relying on existing environment")


def worker(task):
    """
    Execute one prompt task.
    task = (model_name, question, datatype, context, dirs, temperature, max_tokens, save, overwrite)
    """
    model_name, question, datatype, context, dirs, temperature, max_tokens, save, overwrite = task
    model = get_llm(model_name)
    runner = PromptRunner(
        model=model,
        question_number=question,
        datatype=datatype,
        context=context,
        exam_date="",  # unused for now
        base_dirs=dirs,
        temperature=temperature,
        max_tokens=max_tokens,
        save=save,
    )
    out_path = runner.save_to

    # Skip if exists and not overwriting
    if save and out_path and out_path.exists() and not overwrite:
        logging.info(f"Skipping {model_name}/{question}/{datatype} (already exists)")
        return True

    try:
        runner.run()
        return True
    except Exception as e:
        logging.error(f"[{model_name}][{question}][{datatype}] failed: {e}")
        return False


def main():
    # Load .env and configure logging
    load_project_env()
    parser = argparse.ArgumentParser("Batch-run music-theory prompts")

    # Models & context
    parser.add_argument(
        "--models", required=True,
        help="Comma-separated models (e.g. chatgpt,claude) or 'all'"
    )
    parser.add_argument(
        "--context", action="store_true",
        help="Include contextual guides"
    )

    # Selection filters
    parser.add_argument(
        "--questions", nargs="*",
        help="List of question IDs (default: all)"
    )
    parser.add_argument(
        "--datatypes", nargs="*",
        help="List of formats (default: all)"
    )

    # Data & output directories
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path.cwd() / "data",
        help="Root folder for encoded/ and prompts/ (default: ./data)"
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=Path.cwd() / "outputs",
        help="Where to save model responses (default: ./outputs)"
    )

    # Run parameters
    parser.add_argument(
        "--temperature", type=float, default=0.0,
        help="Sampling temperature"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=None,
        help="Optional token cap"
    )
    parser.add_argument(
        "--save", action="store_true",
        help="Save outputs to disk"
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing outputs"
    )
    parser.add_argument(
        "--retry", type=int, default=0,
        help="Number of retries for failed runs"
    )
    parser.add_argument(
        "--jobs", type=int, default=1,
        help="Number of parallel jobs"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Configure logging level
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=level)

    # Build base_dirs mapping
    dirs = {
        "encoded":   args.data_dir / "encoded",
        "prompts":   args.data_dir / "prompts",
        "questions": args.data_dir / "prompts" / "questions",
        "guides":    args.data_dir / "prompts" / "guides",
        "outputs":   args.outputs_dir,
    }

    # Resolve models list
    if args.models.lower() == "all":
        models = ["chatgpt", "claude", "gemini", "deepseek"]
    else:
        models = [m.strip() for m in args.models.split(",")]

    # Resolve question IDs and datatypes
    q_ids = args.questions or list_questions(dirs["questions"])
    dts   = args.datatypes or list_datatypes(dirs["encoded"])

    # Build task list
    tasks = [
        (m, q, dt, args.context, dirs, args.temperature,
         args.max_tokens, args.save, args.overwrite)
        for m in models for q in q_ids for dt in dts
    ]

    # Execute in parallel
    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        future_map = {pool.submit(worker, t): t for t in tasks}
        for fut in as_completed(future_map):
            if not fut.result():
                failures.append(future_map[fut])

    # Retries
    for attempt in range(args.retry):
        if not failures:
            break
        logging.info(f"Retry attempt {attempt+1} for {len(failures)} failures")
        new_failures = []
        for t in failures:
            if not worker(t):
                new_failures.append(t)
        failures = new_failures

    # Summary and exit
    if failures:
        logging.error("Batch completed with failures:")
        for t in failures:
            logging.error(f"  {t}")
        sys.exit(1)

    logging.info("Batch completed successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()
