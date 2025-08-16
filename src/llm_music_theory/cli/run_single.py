#!/usr/bin/env python3
# cli/run_single.py

import argparse
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.utils.path_utils import (
    find_project_root,
    list_file_ids,
    list_datatypes,
    list_guides,
)


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
        "--list-files",
        action="store_true",
        help="List all available file IDs (derived from encoded filenames) and exit"
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
    # Legacy compatibility: old flag name
    list_group.add_argument(
        "--list-questions",
        action="store_true",
        help=argparse.SUPPRESS  # hidden legacy alias for listing files/questions
    )

    # --- Run flags ---
    run_group = parser.add_argument_group("Run", "Execute a single prompt")
    run_group.add_argument(
        "--model",
        choices=["chatgpt", "claude", "gemini", "deepseek"],
        help="LLM to use"
    )
    run_group.add_argument(
        "--model-name",
        dest="model_name_override",
        help="Provider model ID override (e.g. gemini-2.5-pro). If omitted, project default is used."
    )
    run_group.add_argument(
        "--file",
        help="File ID (stem of encoded file, e.g., Q1b)"
    )
    run_group.add_argument(
        "--datatype",
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
        help="Root data directory containing dataset folders (default: ./data)"
    )
    parser.add_argument(
        "--dataset",
        default="fux-counterpoint",
        help="Dataset name inside data-dir (default: fux-counterpoint)"
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=Path.cwd() / "outputs",
        help="Where to save model responses (default: ./outputs)"
    )

    args = parser.parse_args()

    dataset_root = args.data_dir / args.dataset
    base_dirs = {
        "encoded": dataset_root / "encoded",
        "prompts": dataset_root / "prompts",
        "questions": dataset_root / "prompts" / "questions",  # legacy
        "guides": dataset_root / "guides",
        "outputs": args.outputs_dir,
    }

    # Handle early listings
    if args.list_files:
        print("\n".join(list_file_ids(base_dirs["encoded"])))
        sys.exit(0)
    if args.list_datatypes:
        print("\n".join(list_datatypes(base_dirs["encoded"])))
        sys.exit(0)
    if args.list_guides:
        print("\n".join(list_guides(base_dirs["guides"])))
        sys.exit(0)
    if getattr(args, "list_questions", False):  # legacy: map to file ids
        print("\n".join(list_file_ids(base_dirs["encoded"])))
        sys.exit(0)
    
    # Require these only if not listing
    if not (args.list_files or args.list_datatypes or args.list_guides or getattr(args, "list_questions", False)):
        missing = []
        if not args.model:
            missing.append("--model")
        if not args.file:
            missing.append("--file")
        if not args.datatype:
            missing.append("--datatype")
        if missing:
            parser.error(f"The following arguments are required: {', '.join(missing)}")

    # Basic API key validation for models that require an external key.
    # (Currently all implemented models except potential purely local ones.)
    if args.model in {"chatgpt", "claude", "gemini", "deepseek"}:
        # Map each model to its specific env var so unrelated placeholder keys don't block runs.
        model_key_map = {
            "chatgpt": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",  # google-genai SDK expects GOOGLE_API_KEY
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_var = model_key_map[args.model]
        api_key = os.getenv(env_var)
        # Placeholder / invalid heuristics (allow short Google keys; just check placeholder token)
        if not api_key or "your_" in api_key.lower():
            logging.error(
                f"Required key {env_var} missing or placeholder. Add a real key to your .env before running this model."
            )
            sys.exit(2)

    # Dynamically load the requested model now that key sanity check passed
    model = get_llm(args.model)
    # If user supplied a provider-specific model name override, try to set attribute
    if getattr(args, "model_name_override", None):
        # Most model wrappers expose model_name; set if present
        if hasattr(model, "model_name"):
            setattr(model, "model_name", args.model_name_override)
        else:
            logging.warning("Model override ignored; wrapper has no 'model_name' attribute")

    # Configure and run the prompt
    runner = PromptRunner(
        model=model,
        file_id=args.file,
        datatype=args.datatype,
        context=args.context,
        dataset=args.dataset,
        base_dirs=base_dirs,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        save=args.save,
    )

    logging.info(
        f"Running {args.model} on file={args.file} dataset={args.dataset} "
        f"datatype={args.datatype} context={args.context}]"
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
