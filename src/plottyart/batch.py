from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable

from .brain import Brain
from .functions import get_all_functions
from .utils import Constants, Palette, random_palette

PlotFunction = Callable[..., None]


def render_generators(
    output_dir: Path,
    generators: Iterable[PlotFunction] | None = None,
    images_per_function: int = 1,
    image_size: tuple[int, int] = (1024, 1024),
    dpi: int = 100,
    prefer_gpu: bool = True,
    palette: Palette | None = None,
) -> list[Path]:
    """Render a set of generators into one output directory."""

    brain = Brain()
    brain.output_path = output_dir
    brain.img_size = image_size
    brain.dpi = dpi
    brain.prefer_gpu = prefer_gpu

    created_files: list[Path] = []
    functions = (
        list(generators) if generators is not None else list(get_all_functions())
    )

    for func in functions:
        name = func.__name__
        selected_palette = palette or random_palette()

        for image_index in range(1, images_per_function + 1):
            try:
                file_path = brain.save_image(
                    name=name,
                    func=func,
                    output_dir=output_dir,
                    palette=selected_palette,
                    index=image_index,
                )
            except (OSError, ValueError, RuntimeError, TypeError, ImportError) as error:
                print(f"Could not render {name}: {error}")
                continue

            created_files.append(file_path)

    return created_files


def render_all_sets(
    output_dir: Path,
    sets: int = 3,
    images_per_function: int = 1,
    image_size: tuple[int, int] = (1024, 1024),
    dpi: int = 100,
    prefer_gpu: bool = True,
    generators: Iterable[PlotFunction] | None = None,
    palette: Palette | None = None,
) -> list[Path]:
    """Render multiple image sets for every available generator."""

    created_files: list[Path] = []
    functions = (
        list(generators) if generators is not None else list(get_all_functions())
    )

    for set_index in range(1, sets + 1):
        set_dir = output_dir / f"set_{set_index}"
        set_dir.mkdir(parents=True, exist_ok=True)

        set_files = render_generators(
            output_dir=set_dir,
            generators=functions,
            images_per_function=images_per_function,
            image_size=image_size,
            dpi=dpi,
            prefer_gpu=prefer_gpu,
            palette=palette,
        )
        created_files.extend(set_files)

    return created_files


def default_batch_output() -> Path:
    return Constants.DEFAULT_PATH / "validation_runs"
