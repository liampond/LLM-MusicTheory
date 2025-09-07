"""Experiment specification loading and execution utilities.

High‑level *experiment* abstraction tailored for a non‑programmer collaborator
(e.g., a musicologist) to iteratively design and reorder prompt components
without touching Python code.

Public entrypoints:
  load_experiment(path) -> Experiment

See `spec.py` for dataclass definitions and parsing logic.
"""

from .spec import Experiment, load_experiment, run_experiment  # re-export

__all__ = ["Experiment", "load_experiment", "run_experiment"]
