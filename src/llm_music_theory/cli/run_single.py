#!/usr/bin/env python3
"""CLI entrypoint to run a single prompt against a selected LLM.

Responsibilities (kept intentionally thin):
 1. Parse & validate command-line arguments.
 2. Load environment (.env) early so API keys are available.
 3. Perform light sanity checks (dataset structure, file existence, API key presence).
 4. Delegate actual prompt assembly & model call to `PromptRunner`.

Non‑goals kept out of this file to preserve testability & clarity:
 - Prompt building logic (lives in prompts module / runner)
 - Model dispatch (handled by dispatcher)
 - Business rules about datasets beyond basic path checks
"""

from __future__ import annotations

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

from llm_music_theory.core.dispatcher import get_llm
from llm_music_theory.core.runner import PromptRunner
from llm_music_theory.utils.path_utils import (
    find_project_root,
    find_encoded_file,
    list_file_ids,
    list_datatypes,
    list_guides,
)

# Mapping of logical model choices to required API key environment variables.
MODEL_ENV_VARS: Dict[str, str] = {
    "chatgpt": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",  # google-genai SDK expects GOOGLE_API_KEY
    "deepseek": "DEEPSEEK_API_KEY",
}


def load_project_env() -> None:
    """Load environment variables from project root `.env` if present."""
    root = find_project_root()
    dotenv_path = root / ".env"
    if dotenv_path.exists():  # idempotent re-load OK
        load_dotenv(dotenv_path=dotenv_path, override=False)
    else:
        logging.debug("No .env file found; proceeding with existing environment.")


def build_argument_parser() -> argparse.ArgumentParser:
    """Create and return the top-level argument parser.

    Separated for easier unit testing (can call parse_known_args in tests).
    """
    parser = argparse.ArgumentParser(
        description="Run a single music-theory prompt against an LLM"
    )

    # --- Listing flags ---
    list_group = parser.add_argument_group("Listing", "List available resources and exit")
    list_group.add_argument(
        "--list-files",
        action="store_true",
        help="List all available file IDs (derived from encoded filenames) and exit",
    )
    list_group.add_argument(
        "--list-datatypes",
        action="store_true",
        help="List supported encoding formats and exit",
    )
    list_group.add_argument(
        "--list-guides",
        action="store_true",
        help="List available guides and exit",
    )
    list_group.add_argument(
        "--list-questions",
        action="store_true",
        help=argparse.SUPPRESS,  # hidden legacy alias for listing files/questions
    )

    # --- Run flags ---
    run_group = parser.add_argument_group("Run", "Execute a single prompt")
    run_group.add_argument(
        "--model",
        choices=["chatgpt", "claude", "gemini", "deepseek"],
        help="LLM to use",
    )
    run_group.add_argument(
        "--model-name",
        dest="model_name_override",
        help="Provider model ID override (e.g. gemini-2.5-pro). If omitted, project default is used.",
    )
    run_group.add_argument(
        "--file",
        help="File ID (stem of encoded file, e.g., Q1b)",
    )
    run_group.add_argument(
        "--datatype",
        choices=["mei", "musicxml", "abc", "humdrum"],
        help="Encoding format",
    )
    run_group.add_argument(
        "--context",
        action="store_true",
        help="Include contextual guides",
    )
    run_group.add_argument(
        "--examdate",
        default="August2024",
        help="Exam version/folder name (unused for now)",
    )
    run_group.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature (0.0–1.0)",
    )
    run_group.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Optional max tokens for the response",
    )
    run_group.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save response to outputs/ directory (default: save responses)",
    )

    # --- Data & output directories ---
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path.cwd() / "data",
        help="Root data directory containing dataset folders (default: ./data)",
    )
    parser.add_argument(
        "--dataset",
        default="fux-counterpoint",
        help="Dataset name inside data-dir (default: fux-counterpoint)",
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=Path.cwd() / "outputs",
        help="Where to save model responses (default: ./outputs)",
    )
    return parser


def listing_requested(args: argparse.Namespace) -> bool:
    """Return True if any listing flag was supplied."""
    return any(
        getattr(args, flag)
        for flag in ("list_files", "list_datatypes", "list_guides", "list_questions")
    )


def validate_api_key(model_name: str) -> None:
    """Ensure the required API key for the chosen model is present.

    Raises SystemExit with code 2 if missing/placeholder.
    """
    env_var = MODEL_ENV_VARS.get(model_name)
    if not env_var:
        return  # Model without external key (future local model)
    api_key = os.getenv(env_var)
    if not api_key or "your_" in api_key.lower():  # simple placeholder heuristic
        logging.error(
            "Required key %s missing or placeholder. Add a real key to your .env before running this model.",
            env_var,
        )
        raise SystemExit(2)


def build_base_dirs(data_dir: Path, dataset: str) -> Dict[str, Path]:
    dataset_root = data_dir / dataset
    return {
        "encoded": dataset_root / "encoded",
        "prompts": dataset_root / "prompts",
        "questions": dataset_root / "prompts" / "questions",  # legacy
        "guides": dataset_root / "guides",
        "outputs": Path.cwd() / "outputs",  # user override applied later if needed
    }


def main(argv: list[str] | None = None) -> int:
    """Program entrypoint.

    Returns an integer exit status for easier testing.
    """
    # Load env first (logging not configured yet; only debug message inside)
    load_project_env()

    # Configure logging (idempotent; if already configured in tests this won't duplicate handlers)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO,
    )

    parser = build_argument_parser()
    args = parser.parse_args(argv)

    base_dirs = build_base_dirs(args.data_dir, args.dataset)
    base_dirs["outputs"] = args.outputs_dir  # apply override

    dataset_root = args.data_dir / args.dataset
    if not dataset_root.exists():
        logging.error("Dataset root does not exist: %s", dataset_root)
        return 2
    for required_sub in ("encoded", "prompts"):
        sub_path = dataset_root / required_sub
        if not sub_path.exists():
            logging.error("Missing required dataset subdirectory: %s", sub_path)
            return 2

    # Handle early listings
    if args.list_files:
        print("\n".join(list_file_ids(base_dirs["encoded"])))
        return 0
    if args.list_datatypes:
        print("\n".join(list_datatypes(base_dirs["encoded"])))
        return 0
    if args.list_guides:
        print("\n".join(list_guides(base_dirs["guides"])))
        return 0
    if getattr(args, "list_questions", False):  # legacy: map to file ids
        print("\n".join(list_file_ids(base_dirs["encoded"])))
        return 0
    
    # Require these only if not listing
    if not listing_requested(args):
        missing: list[str] = []
        if not args.model:
            missing.append("--model")
        if not args.file:
            missing.append("--file")
        if not args.datatype:
            missing.append("--datatype")
        if missing:
            parser.error(f"The following arguments are required: {', '.join(missing)}")

    # Validate API key if a model is chosen (skip if listing only)
    if not listing_requested(args) and args.model:
        validate_api_key(args.model)

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
        save=not args.no_save,  # Save by default, unless --no-save is specified
    )

    logging.info(
        "Running %s file=%s dataset=%s datatype=%s context=%s",  # noqa: E501
        args.model,
        args.file,
        args.dataset,
        args.datatype,
        args.context,
    )

    # Existence check for encoded file (after logging so user sees parameters)
    datatype_dir = base_dirs["encoded"] / args.datatype
    try:
        encoded_file = find_encoded_file(args.file, args.datatype, datatype_dir, required=True)
    except FileNotFoundError as e:
        logging.error("Encoded source file not found: %s", e)
        return 2

    try:
        response = runner.run()
    except Exception as e:  # pragma: no cover (rare unexpected errors)
        logging.error("Failed to run prompt: %s", e)
        return 1

    # Print and optionally save the response
    print("\n=== Model Response ===\n")
    print(response)

    if not args.no_save and runner.save_to:
        logging.info("Response saved to %s", runner.save_to)
        print(f"\nSaved response to: {runner.save_to}")
    return 0


if __name__ == "__main__":  # pragma: no cover - entrypoint convenience
    sys.exit(main())
