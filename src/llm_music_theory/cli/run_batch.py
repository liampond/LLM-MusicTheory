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
from llm_music_theory.utils.path_utils import (
    list_questions,
    list_datatypes,
    get_output_path,
)

def worker(task):
    """
    task = (model_name, question, datatype, context, dirs, temp, max_tokens, save, overwrite)
    """
    model_name, question, datatype, context, dirs, temperature, max_tokens, save, overwrite = task
    model = get_llm(model_name)
    runner = PromptRunner(
        model=model,
        question_number=question,
        datatype=datatype,
        context=context,
        exam_date="",  # unused
        base_dirs=dirs,
        temperature=temperature,
        max_tokens=max_tokens,
        save=save,
    )
    out_path = runner.save_to if save else None

    # Skip if exists and not overwriting
    if save and out_path.exists() and not overwrite:
        logging.info(f"Skipping {model_name}/{question}/{datatype} (already exists)")
        return True

    try:
        runner.run()
        return True
    except Exception as e:
        logging.error(f"[{model_name}][{question}][{datatype}] failed: {e}")
        return False

def main():
    load_dotenv()
    parser = argparse.ArgumentParser("Batch-run music-theory prompts")
    parser.add_argument(
        "--models", required=True,
        help="Comma-separated models (e.g. chatgpt,claude) or 'all'"
    )
    parser.add_argument(
        "--context", action="store_true",
        help="Include contextual guides"
    )
    parser.add_argument(
        "--questions", nargs="*",
        help="List of question IDs (default: all)"
    )
    parser.add_argument(
        "--datatypes", nargs="*",
        help="List of formats (default: all)"
    )
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

    # Logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=level)

    # Base dirs
    project_root = Path(__file__).resolve().parent.parent
    dirs = {
        "prompts":  project_root / "prompts",
        "questions": project_root / "prompts" / "questions",
        "encoded":  project_root / "encoded",
        "guides":   project_root / "prompts" / "guides",
        "outputs":  project_root / "outputs",
    }

    # Resolve models
    if args.models.lower() == "all":
        models = ["chatgpt", "claude", "gemini", "deepseek"]
    else:
        models = [m.strip() for m in args.models.split(",")]

    # Resolve question IDs and datatypes
    q_ids = args.questions or list_questions(dirs["questions"])
    dts   = args.datatypes or list_datatypes(dirs["encoded"])

    # Build task list
    tasks = []
    for model_name in models:
        for q in q_ids:
            for dt in dts:
                tasks.append((model_name, q, dt, args.context,
                              dirs, args.temperature, args.max_tokens,
                              args.save, args.overwrite))

    # Run with ThreadPoolExecutor
    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        future_to_task = {pool.submit(worker, t): t for t in tasks}
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            success = future.result()
            if not success:
                failures.append(task)

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

    # Summary
    if failures:
        logging.error("Batch completed with failures:")
        for t in failures:
            logging.error(f"  {t}")
        sys.exit(1)
    else:
        logging.info("Batch completed successfully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
