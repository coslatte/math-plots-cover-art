# PlottyArt

PlottyArt generates abstract images from math-driven generators. The CLI is subcommand based, so you can inspect presets first and then render exactly what you want.

## Quick Start

```bash
plottyart --help
python main.py --help
plottyart config
plottyart generators
plottyart palettes
plottyart templates
plottyart generate fractal --count 4
plottyart generate all --palette aurora
plottyart batch --template validation
plottyart organize --output-dir output
```

`settings` is kept as an alias for `config`.

Defaults:

- Single-generator runs use 3000x3000 output unless you pass `--size`.
- `generate all` renders 5 images per generator by default.
- If you do not pass `--output-dir` to `generate all`, PlottyArt creates a folder named like `output/run-1-2026-04-13-generate-all/`.

## Output Layout

Single-generator runs are written as:

```text
output/<generator>/<generator>_1.png
```

Batch runs use set folders:

```text
output/set_1/<generator>/<generator>_1.png
output/set_2/<generator>/<generator>_1.png
```

Template-based batch runs default to `output/validation_runs/`.

The repository also includes sample validation output in `output/validation_runs_20260412/`.

## Available Commands

- `config`: show the default runtime configuration or a template preview.
- `generate`: render one generator, a random generator, all generators, or a template-defined subset.
- `batch`: render every registered generator across multiple sets.
- `generators`: list the generator registry or inspect one generator.
- `palettes`: list the named palette presets or inspect one palette.
- `templates`: list the reusable batch templates or inspect one template.
- `organize`: consolidate generated files into per-generator folders and move loose images into `misc`.

## Adding a Generator

1. Add a plotting function in `src/plottyart/functions.py`.
2. Register it in the generator spec list at the bottom of that module.
3. If you want it included in a template, add its key to the template preset in `src/plottyart/templates.py`.
4. The new generator will then appear in `plottyart generators`, `plottyart generate`, `plottyart batch`, and any template that references it.

## Development

```bash
Z:/_projects/personal/plottyArt/.venv/Scripts/python.exe -m unittest discover -s tests
```

The project metadata and runtime dependencies live in `pyproject.toml`.
