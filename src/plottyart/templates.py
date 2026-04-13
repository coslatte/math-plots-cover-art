from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .functions import available_generator_specs, get_generator_spec
from .utils import Constants


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("_", "-")


@dataclass(frozen=True)
class TemplatePreset:
    key: str
    label: str
    description: str
    output_subdir: str
    sets: int = 1
    images_per_function: int = 1
    image_size: tuple[int, int] = (1500, 1500)
    dpi: int = 100
    prefer_gpu: bool = True
    palette_name: str = Constants.DEFAULT_PALETTE_NAME
    generator_keys: tuple[str, ...] = ()

    def resolve_generators(self) -> tuple[Callable[..., None], ...]:
        if not self.generator_keys:
            return tuple(spec.func for spec in available_generator_specs())

        return tuple(
            get_generator_spec(generator_key).func
            for generator_key in self.generator_keys
        )


TEMPLATE_PRESETS: tuple[TemplatePreset, ...] = (
    TemplatePreset(
        key="validation",
        label="Validation run",
        description="Three sets that cover every registered generator.",
        output_subdir="validation_runs",
        sets=3,
        images_per_function=1,
        image_size=(512, 512),
        dpi=100,
        prefer_gpu=True,
        palette_name="midnight",
    ),
    TemplatePreset(
        key="showcase",
        label="Showcase pack",
        description="One larger run tuned for portfolio-style previews.",
        output_subdir="showcase_runs",
        sets=1,
        images_per_function=2,
        image_size=(1500, 1500),
        dpi=140,
        prefer_gpu=True,
        palette_name="aurora",
    ),
    TemplatePreset(
        key="compact",
        label="Compact preview",
        description="Fast preview output using a focused subset of generators.",
        output_subdir="compact_preview",
        sets=1,
        images_per_function=1,
        image_size=(900, 900),
        dpi=120,
        prefer_gpu=False,
        palette_name="sunset",
        generator_keys=("fractal", "bezier-curve", "tensor-field"),
    ),
)

_TEMPLATE_LOOKUP = {preset.key: preset for preset in TEMPLATE_PRESETS}


def available_templates() -> tuple[TemplatePreset, ...]:
    return TEMPLATE_PRESETS


def template_names() -> list[str]:
    return [preset.key for preset in TEMPLATE_PRESETS]


def get_template(name: str) -> TemplatePreset:
    preset = _TEMPLATE_LOOKUP.get(_normalize_key(name))
    if preset is None:
        available = ", ".join(template_names())
        raise KeyError(f"Unknown template '{name}'. Available templates: {available}")
    return preset


def resolve_template_output_dir(base_dir: Path, template: TemplatePreset) -> Path:
    return base_dir / template.output_subdir
