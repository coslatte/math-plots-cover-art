from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plottyart.art_math import (
    attractor_points,
    bezier_control_points,
    binary_pattern_indices,
    fractal_mask,
    julia_escape_iterations,
    lissajous_points,
    normalize_image_size,
    tensor_field_components,
    voronoi_points,
)


class ArtMathTests(unittest.TestCase):
    def test_normalize_image_size_uses_default(self) -> None:
        self.assertEqual(normalize_image_size(None), (1500, 1500))

    def test_julia_escape_iterations_shape_and_type(self) -> None:
        img = julia_escape_iterations((64, 32), max_iteration=12, seed=7)
        self.assertEqual(img.shape, (32, 64))
        self.assertTrue(np.issubdtype(img.dtype, np.integer))

    def test_fractal_mask_binary_values(self) -> None:
        mask = fractal_mask((48, 48), seed=11)
        self.assertEqual(mask.shape, (48, 48))
        self.assertTrue(set(np.unique(mask)).issubset({0, 1}))

    def test_binary_pattern_indices_range(self) -> None:
        indices = binary_pattern_indices((20, 30), palette_size=7, seed=22)
        self.assertEqual(indices.shape, (20, 30))
        self.assertGreaterEqual(indices.min(), 0)
        self.assertLess(indices.max(), 7)

    def test_lissajous_points_match_length(self) -> None:
        x, y = lissajous_points(n_points=120, randomize_start=False)
        self.assertEqual(len(x), 120)
        self.assertEqual(len(y), 120)

    def test_attractor_points_length(self) -> None:
        xs, ys, coeffs, start = attractor_points(iterations=256, seed=5)
        self.assertEqual(len(xs), 256)
        self.assertEqual(len(ys), 256)
        self.assertEqual(len(coeffs), 4)
        self.assertEqual(len(start), 2)

    def test_voronoi_points_shape(self) -> None:
        points = voronoi_points(n_points=14, seed=9)
        self.assertEqual(points.shape, (14, 2))
        self.assertTrue(np.all(points >= -1))
        self.assertTrue(np.all(points <= 1))

    def test_bezier_control_points_shape(self) -> None:
        points = bezier_control_points(n_points=6, seed=13)
        self.assertEqual(points.shape, (6, 2))

    def test_tensor_field_components_shapes(self) -> None:
        X, Y, U, V = tensor_field_components((8, 9))
        self.assertEqual(X.shape, (9, 8))
        self.assertEqual(Y.shape, (9, 8))
        self.assertEqual(U.shape, (9, 8))
        self.assertEqual(V.shape, (9, 8))


if __name__ == "__main__":
    unittest.main()
