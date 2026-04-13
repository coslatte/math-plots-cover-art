from __future__ import annotations

import argparse
import random
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Sequence

from . import __version__
from .batch import default_batch_output, render_all_sets, render_generators
from .functions import available_generator_specs, get_generator_spec
from .organize_art import organize_art
from .templates import (
    TemplatePreset,
    available_templates,
    get_template,
    resolve_template_output_dir,
)
from .utils import (
    Constants,
    ImageProperties,
    Palette,
    available_palette_presets,
    get_palette_preset,
)

PlotFunction = Callable[..., None]


class CommandHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


@dataclass(frozen=True)
class RenderDefaults:
    output_dir: Path = Constants.DEFAULT_PATH
    image_size: tuple[int, int] = ImageProperties.Resolution.HD.value
    dpi: int = 100
    image_count: int = Constants.DEFAULT_IMG_COUNT
    generate_all_count: int = 5
    prefer_gpu: bool = True
    palette_name: str = Constants.DEFAULT_PALETTE_NAME


class CLI:
    def __init__(self) -> None:
        self.defaults = RenderDefaults()

    def start(self, argv: Sequence[str] | None = None) -> int:
        return self.run(argv)

    def run(self, argv: Sequence[str] | None = None) -> int:
        parser = self.build_parser()
        args = parser.parse_args(list(argv) if argv is not None else None)

        handler = getattr(args, "handler", None)
        if handler is None:
            parser.print_help()
            return 0

        try:
            return handler(parser, args)
        except (KeyError, ValueError) as error:
            parser.error(str(error))

    def build_parser(self) -> argparse.ArgumentParser:
        description = (
            "PlottyArt renders abstract images from mathematical generators.\n\n"
            "Inspect generators, palettes, and templates before rendering to keep runs predictable."
        )
        epilog = (
            "Examples:\n"
            "  plottyart generate fractal --count 4\n"
            "  plottyart generate all --palette aurora\n"
            "  plottyart batch --template validation\n"
            "  plottyart generators\n"
            "  plottyart palettes aurora\n"
            "  plottyart templates compact\n"
            "  plottyart organize --output-dir output\n\n"
            "Output structure:\n"
            "  output/<generator>/<generator>_1.png\n"
            "  output/set_1/<generator>/<generator>_1.png"
        )
        parser = argparse.ArgumentParser(
            prog="plottyart",
            description=description,
            epilog=epilog,
            formatter_class=CommandHelpFormatter,
        )
        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {__version__}"
        )

        subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

        self._add_config_parser(subparsers)
        self._add_generate_parser(subparsers)
        self._add_batch_parser(subparsers)
        self._add_generators_parser(subparsers)
        self._add_palettes_parser(subparsers)
        self._add_templates_parser(subparsers)
        self._add_organize_parser(subparsers)

        return parser

    def _add_config_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "config",
            aliases=["settings"],
            help="Show the default runtime configuration or a template preview.",
        )
        parser.add_argument(
            "--template", help="Show the resolved configuration for a template."
        )
        parser.set_defaults(handler=self.handle_config)

    def _add_generate_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "generate",
            help="Render one generator, all generators, or a template-defined subset.",
        )
        parser.add_argument(
            "generator", nargs="?", help="Generator name, alias, 'all', or 'random'."
        )
        parser.add_argument("--template", help="Apply defaults from a named template.")
        parser.add_argument(
            "-n", "--count", type=_positive_int, help="Images per generator."
        )
        parser.add_argument(
            "-o", "--output-dir", type=Path, help="Directory where images are written."
        )
        parser.add_argument(
            "-s",
            "--size",
            type=_parse_image_size,
            help="Image size in WIDTHxHEIGHT format.",
        )
        parser.add_argument(
            "--dpi", type=_positive_int, help="Figure DPI for the rendered output."
        )
        parser.add_argument(
            "--palette",
            help="Palette preset to use; pass 'random' to pick a fresh palette per generator.",
        )
        gpu_group = parser.add_mutually_exclusive_group()
        gpu_group.add_argument(
            "--gpu", dest="prefer_gpu", action="store_true", help="Prefer GPU backends."
        )
        gpu_group.add_argument(
            "--no-gpu",
            dest="prefer_gpu",
            action="store_false",
            help="Disable GPU backends.",
        )
        parser.set_defaults(prefer_gpu=None)
        parser.set_defaults(handler=self.handle_generate)

    def _add_batch_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "batch",
            help="Render every registered generator across multiple sets.",
        )
        parser.add_argument(
            "--template", help="Apply defaults from a named batch template."
        )
        parser.add_argument(
            "-o",
            "--output-dir",
            type=Path,
            help="Directory where batch output is written.",
        )
        parser.add_argument(
            "--sets", type=_positive_int, help="Number of sets to render."
        )
        parser.add_argument(
            "--images-per-function",
            type=_positive_int,
            help="Images to render for each generator in each set.",
        )
        parser.add_argument(
            "-s",
            "--size",
            type=_parse_image_size,
            help="Image size in WIDTHxHEIGHT format.",
        )
        parser.add_argument(
            "--dpi", type=_positive_int, help="Figure DPI for the rendered output."
        )
        parser.add_argument(
            "--palette",
            help="Palette preset to use; pass 'random' to pick a fresh palette per generator.",
        )
        parser.add_argument(
            "--generators",
            help="Comma-separated generator names to include instead of the template or default set.",
        )
        gpu_group = parser.add_mutually_exclusive_group()
        gpu_group.add_argument(
            "--gpu", dest="prefer_gpu", action="store_true", help="Prefer GPU backends."
        )
        gpu_group.add_argument(
            "--no-gpu",
            dest="prefer_gpu",
            action="store_false",
            help="Disable GPU backends.",
        )
        parser.set_defaults(prefer_gpu=None)
        parser.set_defaults(handler=self.handle_batch)

    def _add_generators_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "generators", help="List the registered generators."
        )
        parser.add_argument("name", nargs="?", help="Show details for one generator.")
        parser.set_defaults(handler=self.handle_generators)

    def _add_palettes_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "palettes", help="List the named palette presets."
        )
        parser.add_argument(
            "name", nargs="?", help="Show details for one palette preset."
        )
        parser.set_defaults(handler=self.handle_palettes)

    def _add_templates_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "templates", help="List the named batch templates."
        )
        parser.add_argument(
            "name", nargs="?", help="Show details for one template preset."
        )
        parser.set_defaults(handler=self.handle_templates)

    def _add_organize_parser(
        self, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]
    ) -> None:
        parser = subparsers.add_parser(
            "organize",
            help="Group generated files into per-generator folders and move loose images into misc.",
        )
        parser.add_argument(
            "-o", "--output-dir", type=Path, help="Directory to reorganize."
        )
        parser.set_defaults(handler=self.handle_organize)

    def handle_config(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        template = self._resolve_template(args.template)
        if template is None:
            self._print_default_configuration()
            return 0

        self._print_template_configuration(template)
        return 0

    def handle_generate(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        template = self._resolve_template(args.template)
        specs = self._resolve_generate_specs(args.generator, template)
        output_dir = self._resolve_generate_output_dir(args.output_dir, args.generator, template)
        image_size = args.size or (
            template.image_size if template else self.defaults.image_size
        )
        dpi = args.dpi or (template.dpi if template else self.defaults.dpi)
        count = self._resolve_generate_count(args.count, args.generator, template)
        prefer_gpu = self._resolve_prefer_gpu(args.prefer_gpu, template)
        palette_name = args.palette or (
            template.palette_name if template else self.defaults.palette_name
        )
        palette = self._resolve_palette(palette_name)

        self._print_run_summary(
            title="Generate",
            output_dir=output_dir,
            image_size=image_size,
            dpi=dpi,
            prefer_gpu=prefer_gpu,
            palette_name=palette_name,
            palette=palette,
            count=count,
            template=template,
            generator_count=len(specs),
        )

        created_files = render_generators(
            output_dir=output_dir,
            generators=[spec.func for spec in specs],
            images_per_function=count,
            image_size=image_size,
            dpi=dpi,
            prefer_gpu=prefer_gpu,
            palette=palette,
        )

        self._print_result_count(created_files)
        return 0

    def handle_batch(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        template = self._resolve_template(args.template)
        if args.output_dir is not None:
            output_dir = args.output_dir.expanduser()
        elif template is not None:
            output_dir = resolve_template_output_dir(self.defaults.output_dir, template)
        else:
            output_dir = default_batch_output()
        image_size = args.size or (
            template.image_size if template else self.defaults.image_size
        )
        dpi = args.dpi or (template.dpi if template else 100)
        sets = args.sets or (template.sets if template else 3)
        images_per_function = args.images_per_function or (
            template.images_per_function if template else 1
        )
        prefer_gpu = self._resolve_prefer_gpu(args.prefer_gpu, template)
        palette_name = args.palette or (
            template.palette_name if template else self.defaults.palette_name
        )
        palette = self._resolve_palette(palette_name)
        functions = self._resolve_batch_generators(args.generators, template)

        self._print_run_summary(
            title="Batch",
            output_dir=output_dir,
            image_size=image_size,
            dpi=dpi,
            prefer_gpu=prefer_gpu,
            palette_name=palette_name,
            palette=palette,
            count=images_per_function,
            template=template,
            generator_count=len(functions),
            sets=sets,
        )

        created_files = render_all_sets(
            output_dir=output_dir,
            sets=sets,
            images_per_function=images_per_function,
            image_size=image_size,
            dpi=dpi,
            prefer_gpu=prefer_gpu,
            generators=functions,
            palette=palette,
        )

        self._print_result_count(created_files)
        return 0

    def handle_generators(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        if args.name is None:
            self._print_generator_list()
            return 0

        spec = get_generator_spec(args.name)
        self._print_generator_details(spec)
        return 0

    def handle_palettes(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        if args.name is None:
            self._print_palette_list()
            return 0

        preset = get_palette_preset(args.name)
        self._print_palette_details(preset.key)
        return 0

    def handle_templates(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        if args.name is None:
            self._print_template_list()
            return 0

        template = self._resolve_template(args.name)
        if template is None:
            parser.error("Template name is required.")
        self._print_template_details(template)
        return 0

    def handle_organize(
        self, parser: argparse.ArgumentParser, args: argparse.Namespace
    ) -> int:
        base_dir = (args.output_dir or self.defaults.output_dir).expanduser()
        print(f"Organizing output in {base_dir}")
        organize_art(base_dir=base_dir)
        return 0

    def _resolve_template(self, template_name: str | None) -> TemplatePreset | None:
        if template_name is None:
            return None
        return get_template(template_name)

    def _resolve_generate_output_dir(
        self,
        override: Path | None,
        generator_name: str | None,
        template: TemplatePreset | None,
    ) -> Path:
        if override is not None:
            return override.expanduser()
        if template is not None:
            return resolve_template_output_dir(self.defaults.output_dir, template)
        if _normalize_key(generator_name or "") == "all":
            return self._create_generate_all_output_dir(self.defaults.output_dir)
        return self.defaults.output_dir

    def _create_generate_all_output_dir(self, base_dir: Path) -> Path:
        base_dir = base_dir.expanduser()
        base_dir.mkdir(parents=True, exist_ok=True)

        today = date.today().isoformat()
        pattern = re.compile(rf"^run-(\d+)-{re.escape(today)}-generate-all$")
        next_index = 1

        for child_dir in base_dir.iterdir():
            if not child_dir.is_dir():
                continue

            match = pattern.match(child_dir.name)
            if match is None:
                continue

            next_index = max(next_index, int(match.group(1)) + 1)

        run_dir = base_dir / f"run-{next_index}-{today}-generate-all"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def _resolve_generate_count(
        self,
        requested: int | None,
        generator_name: str | None,
        template: TemplatePreset | None,
    ) -> int:
        if requested is not None:
            return requested
        if template is not None:
            return template.images_per_function
        if _normalize_key(generator_name or "") == "all":
            return self.defaults.generate_all_count
        return self.defaults.image_count

    def _resolve_prefer_gpu(
        self, requested: bool | None, template: TemplatePreset | None
    ) -> bool:
        if requested is not None:
            return requested
        if template is not None:
            return template.prefer_gpu
        return self.defaults.prefer_gpu

    def _resolve_palette(self, palette_name: str) -> Palette | None:
        if _normalize_key(palette_name) == "random":
            return None
        return get_palette_preset(palette_name).colors

    def _resolve_generate_specs(
        self,
        generator_name: str | None,
        template: TemplatePreset | None,
    ) -> list:
        if generator_name is None:
            if template is not None and template.generator_keys:
                return [get_generator_spec(name) for name in template.generator_keys]
            if template is not None:
                return list(available_generator_specs())
            raise ValueError(
                "generate requires a generator name unless a template provides generators."
            )

        normalized = _normalize_key(generator_name)
        if normalized == "all":
            return list(available_generator_specs())
        if normalized == "random":
            return [random.choice(available_generator_specs())]
        return [get_generator_spec(generator_name)]

    def _resolve_batch_generators(
        self,
        generator_names: str | None,
        template: TemplatePreset | None,
    ) -> list[PlotFunction]:
        if generator_names:
            names = [
                name.strip() for name in generator_names.split(",") if name.strip()
            ]
            if not names:
                raise ValueError("At least one generator name is required.")
            return [get_generator_spec(name).func for name in names]

        if template is not None and template.generator_keys:
            return [get_generator_spec(name).func for name in template.generator_keys]

        return [spec.func for spec in available_generator_specs()]

    def _print_run_summary(
        self,
        *,
        title: str,
        output_dir: Path,
        image_size: tuple[int, int],
        dpi: int,
        prefer_gpu: bool,
        palette_name: str,
        palette: Palette | None,
        count: int,
        template: TemplatePreset | None,
        generator_count: int,
        sets: int | None = None,
    ) -> None:
        print(f"== {title} ==")
        if template is not None:
            print(f"Template: {template.key} ({template.label})")
        print(f"Output: {output_dir}")
        print(f"Size: {_format_size(image_size)}")
        print(f"DPI: {dpi}")
        print(f"GPU: {'on' if prefer_gpu else 'off'}")
        print(f"Palette: {self._palette_display_name(palette_name, palette)}")
        print(f"Generators: {generator_count}")
        print(f"Images per generator: {count}")
        if sets is not None:
            print(f"Sets: {sets}")
        print()

    def _palette_display_name(self, palette_name: str, palette: Palette | None) -> str:
        if palette is None:
            return "random per generator"
        preset = get_palette_preset(palette_name)
        return f"{preset.label} ({preset.key})"

    def _print_result_count(self, created_files: list[Path]) -> None:
        if not created_files:
            print("No files were created.")
            return
        print(f"Created {len(created_files)} file(s).")

    def _print_default_configuration(self) -> None:
        print("== Default Configuration ==")
        print(f"Output directory: {self.defaults.output_dir}")
        print(f"Batch output directory: {default_batch_output()}")
        print(f"Image size: {_format_size(self.defaults.image_size)}")
        print(f"DPI: {self.defaults.dpi}")
        print(f"Image count: {self.defaults.image_count}")
        print(f"Generate all count: {self.defaults.generate_all_count}")
        print(f"GPU: {'on' if self.defaults.prefer_gpu else 'off'}")
        print(f"Palette: {self.defaults.palette_name}")
        print()
        print(
            "Use 'plottyart generate' or 'plottyart batch' flags to override these per run."
        )

    def _print_template_configuration(self, template: TemplatePreset) -> None:
        output_dir = resolve_template_output_dir(self.defaults.output_dir, template)
        print(f"== Template: {template.key} ==")
        print(f"Label: {template.label}")
        print(f"Output directory: {output_dir}")
        print(f"Sets: {template.sets}")
        print(f"Images per function: {template.images_per_function}")
        print(f"Image size: {_format_size(template.image_size)}")
        print(f"DPI: {template.dpi}")
        print(f"GPU: {'on' if template.prefer_gpu else 'off'}")
        print(f"Palette: {template.palette_name}")
        print(f"Generators: {self._template_generator_summary(template)}")

    def _print_generator_list(self) -> None:
        print("== Generators ==")
        for spec in available_generator_specs():
            print(f"- {spec.key}: {spec.label}")

    def _print_generator_details(self, spec) -> None:
        print(f"== Generator: {spec.key} ==")
        print(f"Label: {spec.label}")
        print(f"Function: {spec.func.__name__}")
        print(f"Aliases: {', '.join(spec.aliases) if spec.aliases else 'none'}")

    def _print_palette_list(self) -> None:
        print("== Palettes ==")
        for preset in available_palette_presets():
            print(f"- {preset.key}: {preset.label} ({len(preset.colors)} colors)")

    def _print_palette_details(self, palette_name: str) -> None:
        preset = get_palette_preset(palette_name)
        print(f"== Palette: {preset.key} ==")
        print(f"Label: {preset.label}")
        print(f"Description: {preset.description or 'none'}")
        print(f"Aliases: {', '.join(preset.aliases) if preset.aliases else 'none'}")
        print(f"Color count: {len(preset.colors)}")
        preview = ", ".join(str(color) for color in preset.colors[:5])
        print(f"Preview: {preview}")

    def _print_template_list(self) -> None:
        print("== Templates ==")
        for template in available_templates():
            print(f"- {template.key}: {template.label}")
            print(f"  {template.description}")

    def _print_template_details(self, template: TemplatePreset) -> None:
        print(f"== Template: {template.key} ==")
        print(f"Label: {template.label}")
        print(f"Description: {template.description}")
        print(f"Output subdir: {template.output_subdir}")
        print(f"Sets: {template.sets}")
        print(f"Images per function: {template.images_per_function}")
        print(f"Image size: {_format_size(template.image_size)}")
        print(f"DPI: {template.dpi}")
        print(f"GPU: {'on' if template.prefer_gpu else 'off'}")
        print(f"Palette: {template.palette_name}")
        print(f"Generators: {self._template_generator_summary(template)}")

    def _template_generator_summary(self, template: TemplatePreset) -> str:
        if not template.generator_keys:
            return "all registered generators"
        return ", ".join(
            get_generator_spec(name).label for name in template.generator_keys
        )


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("_", "-")


def _format_size(size: tuple[int, int]) -> str:
    return f"{size[0]}x{size[1]}"


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Value must be a positive integer.") from error

    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer.")

    return parsed


def _parse_image_size(value: str) -> tuple[int, int]:
    cleaned = value.lower().replace(" ", "")
    if "x" not in cleaned:
        raise argparse.ArgumentTypeError("Image size must use the format WIDTHxHEIGHT.")

    width_text, height_text = cleaned.split("x", 1)
    try:
        width = int(width_text)
        height = int(height_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "Image size must use numeric WIDTHxHEIGHT values."
        ) from error

    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("Image size values must be positive integers.")

    return width, height


def main(argv: Sequence[str] | None = None) -> int:
    return CLI().run(argv)


if __name__ == "__main__":
    raise SystemExit(main())
