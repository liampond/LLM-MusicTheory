#!/usr/bin/env python3
"""CLI to run a high‑level experiment YAML specification."""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
from llm_music_theory.experiments.spec import load_experiment, run_experiment

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("Run an experiment spec")
    p.add_argument("--experiment", required=True, type=Path, help="Path to experiment YAML file")
    p.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Actually call model APIs (default: dry run)")
    p.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return p

def run_main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    exp = load_experiment(args.experiment)
    if args.dry_run != exp.dry_run:
        exp.dry_run = args.dry_run  # type: ignore
    out_dir = run_experiment(exp)
    logging.info("Experiment completed. Output dir: %s", out_dir)
    return 0

def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    raise SystemExit(run_main(argv))

if __name__ == "__main__":  # pragma: no cover
    main()
