"""Helpers for optional hardware-accelerated array work."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import cupy as cp  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    cp = None


def get_array_module(prefer_gpu: bool = True):
    """Return ``cupy`` when available and requested, otherwise ``numpy``."""

    if prefer_gpu and cp is not None:
        return cp
    return np


def to_numpy(array: Any) -> np.ndarray:
    """Convert an array from the active backend to a NumPy array."""

    if cp is not None and isinstance(array, cp.ndarray):
        return cp.asnumpy(array)
    return np.asarray(array)
