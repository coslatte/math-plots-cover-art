from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plottyart.batch import render_all_sets


class RenderBatchTests(unittest.TestCase):
    def test_batch_renderer_creates_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            created_files = render_all_sets(
                output_dir=output_dir,
                sets=1,
                images_per_function=1,
                image_size=(128, 128),
                prefer_gpu=False,
            )

            self.assertGreater(len(created_files), 0)
            for file_path in created_files:
                self.assertTrue(file_path.exists())


if __name__ == "__main__":
    unittest.main()
