# -*- coding: utf-8 -*-
"""audit-tool — black-box audit helpers for anonymous API-served models

Stage 1  fingerprint: catalog-wide configuration scan + uniqueness / --match
Stage 2  runner:      candidate behavioral matrix (identity / capability / format)
Stage 3  runner:      corroboration + cross-length tokenizer differential check

See README.md for usage.
"""
from . import fingerprint, runner  # noqa: F401
from .client import LLMClient, MODELS, register  # noqa: F401

__version__ = "0.1.0"
