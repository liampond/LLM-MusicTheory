#!/usr/bin/env python3
# cli/run_single.py

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.utils.path_utils import (
    list_questions,
    list_datatypes,
    list_guides
)


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


def main():
    # Load env first
    load_project_env()

    # Configure logging
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO
    )

    parser = argparse.ArgumentParser(
        description="Run a single music-theory prompt against an LLM"
    )

    # --- Listing flags ---
    list_group = parser.add_argument_group("Listing", "List available resources and exit")
    list_group.add_argument(
        "--list-questions",
        action="store_true",
        help="List all question IDs (e.g. Q1a, Q1b) and exit"
    )
    list_group.add_argument(
        "--list-datatypes",
        action="store_true",
        help="List supported encoding formats and exit"
    )
    list_group.add_argument(
        "--list-guides",
        action="store_true",
        help="List available guides and exit"
    )

    # --- Run flags ---
    run_group = parser.add_argument_group("Run", "Execute a single prompt")
    run_group.add_argument(
        "--model", required=True,
        choices=["chatgpt", "claude", "gemini", "deepseek"],
        help="LLM to use"
    )
    run_group.add_argument(
        "--question", required=True,
        help="Question ID (e.g., Q1a)"
    )
    run_group.add_argument(
        "--datatype", required=True,
        choices=["mei", "musicxml", "abc", "humdrum"],
        help="Encoding format"
    )
    run_group.add_argument(
        "--context", action="store_true",
        help="Include contextual guides"
    )
    run_group.add_argument(
        "--examdate", default="August2024",
        help="Exam version/folder name (unused for now)"
    )
    run_group.add_argument(
        "--temperature", type=float, default=0.0,
        help="Sampling temperature (0.0–1.0)"
    )
    run_group.add_argument(
        "--max-tokens", type=int, default=None,
        help="Optional max tokens for the response"
    )
    run_group.add_argument(
        "--save", action="store_true",
        help="Save response under outputs/<Model>/"
    )

    # --- Data & output directories ---
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

    args = parser.parse_args()

    # Build base_dirs mapping
    base_dirs = {
        "encoded":   args.data_dir / "encoded",
        "prompts":   args.data_dir / "prompts",
        "questions": args.data_dir / "prompts" / "questions",
        "guides":    args.data_dir / "prompts" / "guides",
        "outputs":   args.outputs_dir,
    }

    # Handle early listings
    if args.list_questions:
        print("\n".join(list_questions(base_dirs["questions"])))
        sys.exit(0)
    if args.list_datatypes:
        print("\n".join(list_datatypes(base_dirs["encoded"])))
        sys.exit(0)
    if args.list_guides:
        print("\n".join(list_guides(base_dirs["guides"])))
        sys.exit(0)

    # Dynamically load the requested model
    model = get_llm(args.model)

    # Configure and run the prompt
    runner = PromptRunner(
        model=model,
        question_number=args.question,
        datatype=args.datatype,
        context=args.context,
        exam_date=args.examdate,
        base_dirs=base_dirs,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        save=args.save
    )

    logging.info(
        f"Invoking {args.model} on {args.question} "
        f"[{args.datatype}, context={args.context}]"
    )

    try:
        response = runner.run()
    except Exception as e:
        logging.error(f"Failed to run prompt: {e}")
        sys.exit(1)

    # Print and optionally save the response
    print("\n=== Model Response ===\n")
    print(response)

    if args.save and runner.save_to:
        logging.info(f"Response saved to {runner.save_to}")
        print(f"\nSaved response to: {runner.save_to}")


if __name__ == "__main__":
    main()
