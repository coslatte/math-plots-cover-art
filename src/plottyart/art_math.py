from __future__ import annotations

from typing import Any

import numpy as np


def normalize_image_size(img_size: tuple[int, int] | None, default: tuple[int, int] = (1500, 1500)) -> tuple[int, int]:
    return img_size or default


def julia_escape_iterations(
    img_size: tuple[int, int] | None = None,
    max_iteration: int = 256,
    c: complex | None = None,
    seed: int | None = None,
    xp: Any = np,
) -> Any:
    """Return the Julia-set iteration grid without rendering it."""

    size = normalize_image_size(img_size)
    rng = np.random.default_rng(seed)
    complex_c = c if c is not None else complex(rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8))

    x = xp.linspace(-1.5, 1.5, size[0])
    y = xp.linspace(-1.5, 1.5, size[1])
    X, Y = xp.meshgrid(x, y)
    Z = X + 1j * Y
    img = xp.zeros(Z.shape, dtype=xp.int32)

    for i in range(max_iteration):
        mask = xp.abs(Z) < 2.0
        img[mask] = i
        Z[mask] = Z[mask] ** 2 + complex_c

    return img


def fractal_mask(
    img_size: tuple[int, int] | None = None,
    freq1: float | None = None,
    freq2: float | None = None,
    phase: float | None = None,
    seed: int | None = None,
    xp: Any = np,
) -> Any:
    """Return a binary mask used by the fractal generator."""

    size = normalize_image_size(img_size)
    rng = np.random.default_rng(seed)
    freq1 = freq1 if freq1 is not None else rng.uniform(0.5, 3.5)
    freq2 = freq2 if freq2 is not None else rng.uniform(0.5, 3.5)
    phase = phase if phase is not None else rng.uniform(0, 2 * np.pi)

    x = xp.linspace(-2, 2, size[0])
    y = xp.linspace(-2, 2, size[1])
    X, Y = xp.meshgrid(x, y)
    Z = xp.sin(freq1 * (X**2 + Y**2) + phase)
    Z += xp.cos(freq2 * (X * Y) + phase)
    img = xp.zeros(Z.shape, dtype=xp.uint8)
    img[Z > 0] = 1
    return img


def binary_pattern_indices(
    img_size: tuple[int, int] | None = None,
    palette_size: int = 10,
    seed: int | None = None,
    xp: Any = np,
) -> Any:
    """Return palette indices for the binary pattern generator."""

    size = normalize_image_size(img_size)
    rng = np.random.default_rng(seed)
    return xp.asarray(rng.integers(0, palette_size, size=size))


def lissajous_points(
    n_points: int = 1000,
    randomize_start: bool = True,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return points for a smooth Lissajous curve."""

    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * np.pi, n_points)
    if randomize_start:
        t = t + rng.uniform(0, 2 * np.pi)
    x = np.sin(3 * t)
    y = np.sin(4 * t)
    return x, y


def attractor_points(
    iterations: int = 5000,
    coefficients: tuple[float, float, float, float] | None = None,
    start: tuple[float, float] | None = None,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray, tuple[float, float, float, float], tuple[float, float]]:
    """Return a Clifford-attractor-like point cloud."""

    rng = np.random.default_rng(seed)
    if coefficients is None:
        coefficients = tuple(rng.uniform(-2.5, 2.5, 4))
    if start is None:
        start = (rng.uniform(-1, 1), rng.uniform(-1, 1))

    a, b, c, d = coefficients
    x, y = start
    xs: list[float] = []
    ys: list[float] = []

    for _ in range(iterations):
        x, y = (
            np.sin(a * y) + c * np.cos(a * x),
            np.sin(b * x) + d * np.cos(b * y),
        )
        xs.append(x)
        ys.append(y)

    return np.asarray(xs), np.asarray(ys), coefficients, start


def tensor_field_components(grid_size: tuple[int, int] = (24, 24)) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return vector-field components for the tensor field generator."""

    x = np.linspace(-2, 2, grid_size[0])
    y = np.linspace(-2, 2, grid_size[1])
    X, Y = np.meshgrid(x, y)
    U = np.sin(X) * np.cos(Y)
    V = -np.cos(X) * np.sin(Y)
    return X, Y, U, V


def voronoi_points(n_points: int = 24, seed: int | None = None) -> np.ndarray:
    """Return seed points for a Voronoi diagram."""

    rng = np.random.default_rng(seed)
    return rng.random((n_points, 2)) * 2 - 1


def bezier_control_points(n_points: int = 5, seed: int | None = None) -> np.ndarray:
    """Return control points for spline-based curve art."""

    rng = np.random.default_rng(seed)
    return rng.random((n_points, 2)) * 2 - 1
