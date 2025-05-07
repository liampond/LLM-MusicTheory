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

def main():
    # Load environment variables and configure logging
    load_dotenv()
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

    args = parser.parse_args()

    # Base directory resolution
    project_root = Path(__file__).resolve().parent.parent
    base_dirs = {
        "prompts":  project_root / "prompts",
        "questions": project_root / "prompts" / "questions",
        "encoded":  project_root / "encoded",
        "guides":   project_root / "prompts" / "guides",
        "outputs":  project_root / "outputs",
    }

    # Handle listings
    if args.list_questions:
        print("\n".join(list_questions(base_dirs["questions"])))
        sys.exit(0)
    if args.list_datatypes:
        print("\n".join(list_datatypes(base_dirs["encoded"])))
        sys.exit(0)
    if args.list_guides:
        print("\n".join(list_guides(base_dirs["guides"])))
        sys.exit(0)

    # Load the model dynamically
    model = get_llm(args.model)

    # Configure and run
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

    # Output
    print("\n=== Model Response ===\n")
    print(response)

    if args.save and runner.save_to:
        logging.info(f"Response saved to {runner.save_to}")
        print(f"\nSaved response to: {runner.save_to}")

if __name__ == "__main__":
    main()
