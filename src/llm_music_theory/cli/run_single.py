#!/usr/bin/env python3
# cli/run_single.py

import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.core.runner import PromptRunner

def main():
    # Load environment variables from .env
    load_dotenv()

    # Set up basic logging
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO
    )

    # CLI arguments
    parser = argparse.ArgumentParser(
        description="Run a single music-theory prompt against an LLM"
    )
    parser.add_argument(
        "--model",
        required=True,
        choices=["chatgpt", "claude", "gemini", "deepseek"],
        help="Which LLM to use"
    )
    parser.add_argument(
        "--question",
        required=True,
        help="Question ID (e.g., Q1a)"
    )
    parser.add_argument(
        "--datatype",
        required=True,
        choices=["mei", "musicxml", "abc", "humdrum"],
        help="Encoding format"
    )
    parser.add_argument(
        "--context",
        action="store_true",
        help="Include contextual guides"
    )
    parser.add_argument(
        "--examdate",
        default="August2024",
        help="Exam version or folder name (for future use)"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (0.0–1.0)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Optional max tokens for the response"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the model response to outputs/<Model>/<file>"
    )

    args = parser.parse_args()

    # Resolve base directories relative to project root
    project_root = Path(__file__).resolve().parent.parent
    base_dirs = {
        "prompts": project_root / "prompts",
        "questions": project_root / "prompts" / "questions",
        "encoded": project_root / "encoded",
        "guides": project_root / "prompts" / "guides",
        "outputs": project_root / "outputs",
    }

    # Dynamically load the requested model
    model = get_llm(args.model)

    # Initialize and run the prompt
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
    response = runner.run()

    # Print the response
    print("\n=== Model Response ===\n")
    print(response)

if __name__ == "__main__":
    main()
