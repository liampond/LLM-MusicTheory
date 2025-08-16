"""Project logging utilities.

Centralized helpers to configure and retrieve loggers consistently across the
project without each module invoking ``basicConfig`` independently.

Usage (simple):
	from llm_music_theory.utils.logger import configure_logging, get_logger
	configure_logging()  # safe to call multiple times
	log = get_logger(__name__)
	log.info("Hello")

Environment variables:
	LOG_LEVEL   -> DEBUG | INFO | WARNING | ERROR | CRITICAL (default: INFO)
	LOG_FORMAT  -> "plain" (default) or "json" (structured single‑line JSON)
	LOG_COLOR   -> "1" to enable ANSI color for levels with plain format (default auto)

Design goals:
  * Idempotent configuration (repeated calls are cheap).
  * Optional JSON output for easier ingestion.
  * Minimal (no external dependencies).
  * Allow programmatic override of level while still honoring env defaults.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Optional

__all__ = ["configure_logging", "get_logger"]

_CONFIGURED = False


class _JsonFormatter(logging.Formatter):
	def format(self, record: logging.LogRecord) -> str:  # pragma: no cover (format logic deterministic)
		data = {
			"level": record.levelname,
			"name": record.name,
			"message": record.getMessage(),
			"time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
		}
		if record.exc_info:
			data["exc"] = self.formatException(record.exc_info)
		return json.dumps(data, ensure_ascii=False)


_COLOR_MAP = {
	"DEBUG": "\x1b[37m",  # light gray
	"INFO": "\x1b[36m",  # cyan
	"WARNING": "\x1b[33m",  # yellow
	"ERROR": "\x1b[31m",  # red
	"CRITICAL": "\x1b[41m",  # red background
}
_RESET = "\x1b[0m"


class _ColorFormatter(logging.Formatter):  # pragma: no cover (cosmetic)
	def format(self, record: logging.LogRecord) -> str:
		base = super().format(record)
		color = _COLOR_MAP.get(record.levelname)
		if not color:
			return base
		return f"{color}{base}{_RESET}"


def _env_level() -> int:
	level_name = os.getenv("LOG_LEVEL", "INFO").upper()
	return getattr(logging, level_name, logging.INFO)


def configure_logging(level: Optional[int] = None, force: bool = False) -> None:
	"""Configure root logging once.

	Parameters
	----------
	level: int | None
		Override log level (numeric). If None, derive from ``LOG_LEVEL`` env.
	force: bool
		Reconfigure handlers even if already configured.
	"""
	global _CONFIGURED
	if _CONFIGURED and not force:
		# Allow dynamic level updates
		if level is not None:
			logging.getLogger().setLevel(level)
		return

	fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
	datefmt = "%H:%M:%S"
	handler = logging.StreamHandler(sys.stdout)

	log_format = os.getenv("LOG_FORMAT", "plain").lower()
	use_color = os.getenv("LOG_COLOR", "").strip() == "1" and sys.stdout.isatty()

	if log_format == "json":
		handler.setFormatter(_JsonFormatter())
	else:
		formatter: logging.Formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
		if use_color:
			formatter = _ColorFormatter(fmt=fmt, datefmt=datefmt)
		handler.setFormatter(formatter)

	root = logging.getLogger()
	root.handlers.clear()
	root.addHandler(handler)
	root.setLevel(level if level is not None else _env_level())
	_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
	"""Return a module/component logger.

	Ensures global configuration is applied before first use.
	"""
	if not _CONFIGURED:
		configure_logging()
	return logging.getLogger(name)

