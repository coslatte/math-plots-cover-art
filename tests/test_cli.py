from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date as real_date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from plottyart.cli import CLI, RenderDefaults
from plottyart.utils import Constants


class CLITests(unittest.TestCase):
    def test_generate_uses_selected_generator(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch("plottyart.cli.render_generators") as render_generators:
            render_generators.return_value = [Path(temp_dir) / "fractal" / "fractal_1.png"]

            exit_code = CLI().run(["generate", "fractal", "--count", "2", "--output-dir", temp_dir])

            self.assertEqual(exit_code, 0)
            render_generators.assert_called_once()
            call_kwargs = render_generators.call_args.kwargs
            self.assertEqual(call_kwargs["output_dir"], Path(temp_dir))
            self.assertEqual(call_kwargs["images_per_function"], 2)
            self.assertEqual(call_kwargs["image_size"], (3000, 3000))
            self.assertEqual(call_kwargs["dpi"], 100)
            self.assertTrue(call_kwargs["prefer_gpu"])
            self.assertIsNotNone(call_kwargs["palette"])
            self.assertEqual(len(call_kwargs["generators"]), 1)
            self.assertEqual(call_kwargs["generators"][0].__name__, "fractal")

    def test_generate_all_creates_named_run_directory(self) -> None:
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch("plottyart.cli.render_generators") as render_generators,
            patch("plottyart.cli.date") as mock_date,
        ):
            mock_date.today.return_value = real_date(2026, 4, 13)
            render_generators.return_value = []

            cli = CLI()
            cli.defaults = RenderDefaults(output_dir=Path(temp_dir))

            exit_code = cli.run(["generate", "all"])

            self.assertEqual(exit_code, 0)
            call_kwargs = render_generators.call_args.kwargs
            self.assertEqual(call_kwargs["images_per_function"], 5)
            self.assertEqual(call_kwargs["image_size"], (3000, 3000))
            self.assertEqual(call_kwargs["output_dir"].name, "run-1-2026-04-13-generate-all")
            self.assertTrue(call_kwargs["output_dir"].exists())

    def test_generate_all_count_can_be_overridden(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch("plottyart.cli.render_generators") as render_generators:
            render_generators.return_value = []

            cli = CLI()
            cli.defaults = RenderDefaults(output_dir=Path(temp_dir))

            exit_code = cli.run(["generate", "all", "--count", "3"])

            self.assertEqual(exit_code, 0)
            call_kwargs = render_generators.call_args.kwargs
            self.assertEqual(call_kwargs["images_per_function"], 3)

    def test_generate_random_palette_is_lazy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, patch("plottyart.cli.render_generators") as render_generators:
            render_generators.return_value = []

            exit_code = CLI().run(["generate", "fractal", "--palette", "random", "--output-dir", temp_dir])

            self.assertEqual(exit_code, 0)
            call_kwargs = render_generators.call_args.kwargs
            self.assertIsNone(call_kwargs["palette"])

    def test_batch_uses_template_defaults(self) -> None:
        with patch("plottyart.cli.render_all_sets") as render_all_sets:
            render_all_sets.return_value = [Constants.DEFAULT_PATH / "validation_runs" / "set_1" / "julia_set" / "julia_set_1.png"]

            exit_code = CLI().run(["batch", "--template", "validation"])

            self.assertEqual(exit_code, 0)
            render_all_sets.assert_called_once()
            call_kwargs = render_all_sets.call_args.kwargs
            self.assertEqual(call_kwargs["output_dir"], Constants.DEFAULT_PATH / "validation_runs")
            self.assertEqual(call_kwargs["sets"], 3)
            self.assertEqual(call_kwargs["images_per_function"], 1)
            self.assertEqual(call_kwargs["image_size"], (512, 512))
            self.assertEqual(call_kwargs["dpi"], 100)
            self.assertTrue(call_kwargs["prefer_gpu"])
            self.assertIsNotNone(call_kwargs["palette"])
            self.assertEqual(len(call_kwargs["generators"]), 9)

    def test_batch_without_template_defaults_to_hd(self) -> None:
        with patch("plottyart.cli.render_all_sets") as render_all_sets:
            render_all_sets.return_value = []

            exit_code = CLI().run(["batch"])

            self.assertEqual(exit_code, 0)
            call_kwargs = render_all_sets.call_args.kwargs
            self.assertEqual(call_kwargs["image_size"], (3000, 3000))
            self.assertEqual(call_kwargs["images_per_function"], 1)

    def test_generator_listing_includes_registry(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = CLI().run(["generators"])

        output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("julia-set", output)
        self.assertIn("fractal", output)

    def test_settings_alias_prints_defaults(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = CLI().run(["settings"])

        output = buffer.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Default Configuration", output)
        self.assertIn("Image size: 3000x3000", output)
        self.assertIn("Generate all count: 5", output)
        self.assertIn("Image count", output)


if __name__ == "__main__":
    unittest.main()
