from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Types n stuff
Palette = list[tuple[int, int, int]]  # [(255, 255, 255), ...]
PaletteCollection = list[Palette]
Resolution = tuple[int, int]  # (1000, 1000)


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("_", "-")


@dataclass(frozen=True)
class PalettePreset:
    key: str
    label: str
    colors: Palette
    description: str = ""
    aliases: tuple[str, ...] = ()


MIDNIGHT_PALETTE: Palette = [
    (30, 30, 60),
    (60, 20, 80),
    (120, 40, 120),
    (200, 60, 180),
    (20, 120, 120),
    (80, 10, 60),
    (40, 80, 120),
    (100, 30, 90),
    (60, 60, 100),
    (90, 20, 70),
]

AURORA_PALETTE: Palette = [
    (10, 10, 30),
    (40, 20, 60),
    (80, 40, 100),
    (120, 60, 160),
    (200, 80, 220),
    (30, 60, 90),
    (70, 30, 110),
    (110, 50, 150),
    (150, 70, 190),
    (190, 90, 230),
]

SUNSET_PALETTE: Palette = [
    (20, 20, 40),
    (60, 30, 90),
    (100, 50, 130),
    (160, 70, 200),
    (220, 90, 250),
    (50, 100, 150),
    (90, 60, 120),
    (130, 80, 170),
    (170, 100, 210),
    (210, 120, 250),
]

NEBULA_PALETTE: Palette = [
    (15, 15, 35),
    (50, 25, 70),
    (90, 45, 110),
    (140, 65, 170),
    (180, 85, 210),
    (60, 40, 100),
    (100, 60, 140),
    (140, 80, 180),
    (180, 100, 220),
    (220, 120, 255),
]

PALETTE_PRESETS: tuple[PalettePreset, ...] = (
    PalettePreset(
        key="midnight",
        label="Midnight",
        colors=MIDNIGHT_PALETTE,
        description="Deep blue, violet, and teal tones.",
        aliases=("default", "base"),
    ),
    PalettePreset(
        key="aurora",
        label="Aurora",
        colors=AURORA_PALETTE,
        description="Cool neon purples with softer blues.",
        aliases=("electric", "neon"),
    ),
    PalettePreset(
        key="sunset",
        label="Sunset",
        colors=SUNSET_PALETTE,
        description="Brighter magenta and blue contrast.",
        aliases=("dusk",),
    ),
    PalettePreset(
        key="nebula",
        label="Nebula",
        colors=NEBULA_PALETTE,
        description="A lighter violet and indigo blend.",
        aliases=("violet",),
    ),
)

_PALETTE_LOOKUP = {preset.key: preset for preset in PALETTE_PRESETS}
for preset in PALETTE_PRESETS:
    for alias in preset.aliases:
        _PALETTE_LOOKUP[_normalize_key(alias)] = preset


class State(Enum):
    SUCCESS = 1
    FAILURE = 0
    CONFIRMATION = ("yes", "y")
    NEGATION = ("no", "n")

    # Helpful for operations like `if state in State.CONFIRMATION` really well, avoid verbosity :')
    def __contains__(self, item: object) -> bool:
        return item in self.value


class ImageProperties:
    class Resolution(Enum):
        SMALL: Resolution = (1000, 1000)
        NORMAL: Resolution = (1500, 1500)
        HD: Resolution = (3000, 3000)


class Constants:
    DEFAULT_PATH = Path(__file__).resolve().parents[2] / "output"
    DEFAULT_IMG_COUNT: int = 10
    DEFAULT_BASE_PALETTE: Palette = MIDNIGHT_PALETTE
    DEFAULT_PALETTE_NAME: str = "midnight"


def available_palette_presets() -> tuple[PalettePreset, ...]:
    return PALETTE_PRESETS


def palette_preset_names(include_aliases: bool = False) -> list[str]:
    names = [preset.key for preset in PALETTE_PRESETS]
    if include_aliases:
        names.extend(alias for preset in PALETTE_PRESETS for alias in preset.aliases)
    return names


def get_palette_preset(name: str) -> PalettePreset:
    preset = _PALETTE_LOOKUP.get(_normalize_key(name))
    if preset is None:
        available = ", ".join(palette_preset_names())
        raise KeyError(f"Unknown palette preset '{name}'. Available presets: {available}")
    return preset


def resolve_palette(name: str | None = None) -> Palette:
    if name is None:
        return list(DEFAULT_BASE_PALETTE)

    normalized = _normalize_key(name)
    if not normalized or normalized == "random":
        return random_palette()

    return list(get_palette_preset(name).colors)


def random_palette() -> Palette:
    """
    Generates a palette of cool colors (blue, cyan, violet, blue-green) with medium saturation and medium-high luminosity.
    Occasionally (10%) adds a warm color (red, magenta).
    """

    import colorsys
    import random

    palette: Palette = []
    n_colors = random.randint(8, 16)

    for _ in range(n_colors):
        if random.random() < 0.9:
            # 90%: cool tones (blue 200°–260°, cyan 160°–200°, violet 260°–300°)
            h_ranges = [(0.44, 0.56), (0.56, 0.72), (0.72, 0.83)]  # HSL: 160–300°
            h_range = random.choice(h_ranges)
            h = random.uniform(*h_range)
        else:
            # 10%: red/magenta (0°–30° and 330°–360°)
            if random.random() < 0.5:
                h = random.uniform(0.0, 0.08)
            else:
                h = random.uniform(0.92, 1.0)

        saturation = random.uniform(0.45, 0.7)
        luminosity = random.uniform(0.48, 0.72)
        r, g, b = colorsys.hls_to_rgb(h, luminosity, saturation)
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        palette.append(rgb)
    random.shuffle(palette)
    return palette
