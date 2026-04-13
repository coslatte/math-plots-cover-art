import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import librosa
import numpy as np

from matplotlib.axes import Axes
from scipy.interpolate import make_interp_spline
from scipy.spatial import Voronoi, voronoi_plot_2d

from .art_math import (
    attractor_points,
    bezier_control_points,
    binary_pattern_indices,
    fractal_mask,
    julia_escape_iterations,
    lissajous_points,
    tensor_field_components,
    voronoi_points,
)
from .utils import Palette
from .render_backend import get_array_module, to_numpy

PlotFunction = Callable[..., None]


@dataclass(frozen=True)
class GeneratorSpec:
    key: str
    label: str
    func: PlotFunction
    aliases: tuple[str, ...] = ()


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "-").replace("_", "-")


def _img_size(img_size: tuple[int, int] | None) -> tuple[int, int]:
    return img_size or (1500, 1500)


def _palette_array(palette: Palette) -> np.ndarray:
    return np.asarray(palette, dtype=np.uint8)


def _mpl_color(color: tuple[int, int, int]) -> tuple[float, float, float]:
    return tuple(channel / 255 for channel in color)


def get_all_functions(ret_type: str | Callable = Callable) -> list[str] | list[PlotFunction]:
    if ret_type not in (str, Callable):
        raise TypeError("Function has to be type str or Callable")

    if ret_type is str:
        return [spec.label for spec in _GENERATOR_SPECS]
    if ret_type is Callable:
        return [spec.func for spec in _GENERATOR_SPECS]


def available_generator_specs() -> tuple[GeneratorSpec, ...]:
    return _GENERATOR_SPECS


def generator_names(include_aliases: bool = False) -> list[str]:
    names = [spec.key for spec in _GENERATOR_SPECS]
    if include_aliases:
        names.extend(alias for spec in _GENERATOR_SPECS for alias in spec.aliases)
    return names


def get_generator_spec(name: str) -> GeneratorSpec:
    spec = _GENERATOR_LOOKUP.get(_normalize_key(name))
    if spec is None:
        available = ", ".join(generator_names(include_aliases=True))
        raise KeyError(f"Unknown generator '{name}'. Available generators: {available}")
    return spec


def julia_set(
    ax: Axes,
    palette: Palette,
    img_size: tuple[int, int] | None = None,
    prefer_gpu: bool = True,
    max_iteration: int = 256,
) -> None:
    """Classic Julia set with a random complex parameter."""

    size = _img_size(img_size)
    xp = get_array_module(prefer_gpu)
    img = julia_escape_iterations(size, max_iteration=max_iteration, xp=xp)
    idx = to_numpy(img) % len(palette)
    rgb = _palette_array(palette)[idx]
    ax.imshow(rgb, origin="lower")
    ax.axis("off")


def hilbert_curve(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Plot a Hilbert curve (order 6)."""

    _ = img_size, prefer_gpu

    def hilbert(n: int) -> list[tuple[float, float]]:
        def hilbert_recursive(
            x0: float,
            y0: float,
            xi: float,
            xj: float,
            yi: float,
            yj: float,
            n: int,
        ) -> list[tuple[float, float]]:
            if n <= 0:
                x = x0 + (xi + yi) / 2
                y = y0 + (xj + yj) / 2
                return [(x, y)]
            else:
                points = []
                points.extend(hilbert_recursive(x0, y0, yi / 2, yj / 2, xi / 2, xj / 2, n - 1))
                points.extend(
                    hilbert_recursive(
                        x0 + xi / 2,
                        y0 + xj / 2,
                        xi / 2,
                        xj / 2,
                        yi / 2,
                        yj / 2,
                        n - 1,
                    )
                )
                points.extend(
                    hilbert_recursive(
                        x0 + xi / 2 + yi / 2,
                        y0 + xj / 2 + yj / 2,
                        xi / 2,
                        xj / 2,
                        yi / 2,
                        yj / 2,
                        n - 1,
                    )
                )
                points.extend(
                    hilbert_recursive(
                        x0 + xi / 2 + yi,
                        y0 + xj / 2 + yj,
                        -yi / 2,
                        -yj / 2,
                        -xi / 2,
                        -xj / 2,
                        n - 1,
                    )
                )
                return points

        return hilbert_recursive(0, 0, 1, 0, 0, 1, n)

    points = hilbert(6)
    x, y = zip(*points)
    ax.plot(x, y, color=_mpl_color(palette[0]))
    ax.axis("off")


def lissajous(
    ax: Axes,
    palette: Palette,
    img_size: tuple[int, int] | None = None,
    prefer_gpu: bool = True,
    randomize_start: bool = True,
) -> None:
    """Simple Lissajous curve with fixed frequency ratio."""

    _ = img_size, prefer_gpu
    x, y = lissajous_points(randomize_start=randomize_start)
    ax.plot(x, y, color=_mpl_color(palette[0]))
    ax.axis("off")


def voronoi_diagram(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Voronoi diagram filled with random palette colors."""

    _ = img_size, prefer_gpu

    points = voronoi_points(seed=random.randint(0, 1_000_000))
    vor = Voronoi(points)
    voronoi_plot_2d(vor, ax=ax, show_points=False, show_vertices=False, line_colors="none")
    for i, region in enumerate(vor.regions):
        if not region or -1 in region:
            continue
        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), color=_mpl_color(random.choice(palette)))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")


def bezier_curve(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Smooth curve through random points using cubic spline as Bézier-like art."""

    _ = img_size, prefer_gpu

    n_points = np.random.randint(3, 8)
    points = bezier_control_points(n_points=n_points)
    t_control = np.linspace(0, 1, n_points)
    t = np.linspace(0, 1, 1000)
    spl = make_interp_spline(t_control, points, k=min(3, n_points - 1))
    smooth_points = spl(t)
    ax.plot(smooth_points[:, 0], smooth_points[:, 1], color=_mpl_color(random.choice(palette)))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")


def fractal(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Thresholded combination of sinusoidal fields over a grid."""

    size = _img_size(img_size)
    xp = get_array_module(prefer_gpu)
    img = fractal_mask(size, xp=xp)
    fractal_palette = np.asarray([palette[0], palette[min(1, len(palette) - 1)]], dtype=np.uint8)
    ax.imshow(fractal_palette[to_numpy(img)], origin="lower")
    ax.axis("off")


def attractor(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Clifford attractor variant with simple line plotting."""

    _ = img_size, prefer_gpu

    xs, ys, _, _ = attractor_points()
    ax.plot(xs, ys, color=_mpl_color(random.choice(palette)), linewidth=0.7)
    ax.axis("off")


def binary_pattern(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Random palette-indexed grid with optional noise."""

    size = _img_size(img_size)
    xp = get_array_module(prefer_gpu)
    arr = binary_pattern_indices(size, palette_size=len(palette), xp=xp)
    if np.random.rand() > 0.5:
        arr = xp.bitwise_xor(arr, xp.random.randint(0, len(palette), size=size))
    arr = xp.mod(arr, len(palette))
    img = _palette_array(palette)[to_numpy(arr)]
    if np.random.rand() > 0.5:
        img = np.clip(img + np.random.randint(0, 40, img.shape), 0, 255)
    ax.imshow(img, origin="lower")
    ax.axis("off")


def tensor_field(ax: Axes, palette: Palette, img_size: tuple[int, int] | None = None, prefer_gpu: bool = True) -> None:
    """Simple vector field using sine/cosine relations."""

    _ = img_size, prefer_gpu

    X, Y, U, V = tensor_field_components((np.random.randint(5, 50), np.random.randint(5, 50)))
    ax.quiver(X, Y, U, V, color=_mpl_color(random.choice(palette)))
    ax.axis("off")


def lissajous_harmonics_from_music(
    ax: Axes,
    palette: Palette,
    binario: str,
    music_folder: str,
    img_size: tuple[int, int] | None = None,
    prefer_gpu: bool = True,
    randomize_start: bool = True,
    randomize_phases: bool = True,
) -> bool:
    """
    Generates a Lissajous harmonic image using the detected base frequency of the fundamental note
    from an audio file whose name matches the binary. If no audio is found, generates a generic Lissajous curve.
    """

    music_path = Path(music_folder)
    if not music_path.exists() or not music_path.is_dir():
        print(f"[INFO] Music folder '{music_folder}' is not available. A generic Lissajous curve will be generated.")
        lissajous(ax, palette, randomize_start=randomize_start)
        return True

    audio_file = None
    try:
        for fname in os.listdir(music_folder):
            if binario in fname and fname.lower().endswith((".mp3", ".wav", ".ogg", ".flac")):
                audio_file = os.path.join(music_folder, fname)
                break
    except OSError:
        print(f"[INFO] Unable to read music folder '{music_folder}'. A generic Lissajous curve will be generated.")
        lissajous(ax, palette, randomize_start=randomize_start)
        return True

    if audio_file is None:
        print(f"[INFO] No audio file found for {binario}. A generic Lissajous curve will be generated.")
        lissajous(ax, palette, randomize_start=randomize_start)
        return True

    # Process audio and generate harmonic curve
    try:
        y_audio, _sr = librosa.load(audio_file, sr=None, mono=True, duration=10.0)
        f0, _voiced_flag, _voiced_probs = librosa.pyin(
            y_audio, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        freq_base = np.nanmedian(f0)
        if np.isnan(freq_base):
            freq_base = librosa.note_to_hz("C2")
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Error analyzing {audio_file}: {e}")
        freq_base = librosa.note_to_hz("C2")

    _ = img_size, prefer_gpu

    N = int(binario, 2)
    if N == 0:
        N = 3  # minimum

    # --- OPTIMIZATION ---
    N_POINTS = 20000
    N_SPLINE = 100000

    if randomize_start:
        t_offset = np.random.uniform(0, 2 * np.pi)
        t = np.linspace(0, 2 * np.pi, N_POINTS, dtype=np.float32) + t_offset
    else:
        t = np.linspace(0, 2 * np.pi, N_POINTS, dtype=np.float32)
    x = np.zeros_like(t)
    y = np.zeros_like(t)

    decay_start = 1.0
    decay_end = 0.2
    decay_factors = np.linspace(decay_start, decay_end, N)
    for n in range(1, N + 1):
        decay = decay_factors[n - 1]
        freq_x = n * freq_base
        freq_y = (N - n + 1) * freq_base
        if randomize_phases:
            phase_x = np.random.uniform(0, 2 * np.pi)
            phase_y = np.random.uniform(0, 2 * np.pi)
        else:
            phase_x = 0
            phase_y = np.pi / 2
        x += decay * (1 / n) * np.sin(freq_x * t + phase_x)
        y += decay * (1 / n) * np.sin(freq_y * t + phase_y)

    # Normalization
    x /= np.max(np.abs(x))
    y /= np.max(np.abs(y))

    # Cubic spline for smoothness
    t_smooth = np.linspace(t.min(), t.max(), N_SPLINE, dtype=np.float32)
    spl_x = make_interp_spline(t, x, k=3)
    spl_y = make_interp_spline(t, y, k=3)
    x_smooth = spl_x(t_smooth)
    y_smooth = spl_y(t_smooth)

    # Post-spline normalization
    x_smooth /= np.max(np.abs(x_smooth))
    y_smooth /= np.max(np.abs(y_smooth))

    # Artistic touch: subtle noise
    noise_strength = 0.002
    x_smooth += np.random.normal(0, noise_strength, size=x_smooth.shape)
    y_smooth += np.random.normal(0, noise_strength, size=y_smooth.shape)

    # Color and artistic style
    color = np.clip(
        np.array(random.choice(palette)) / 255 + np.random.uniform(-0.05, 0.05, 3),
        0,
        1,
    )
    linewidth = np.random.uniform(1.8, 2.6)
    alpha = np.random.uniform(0.82, 0.95)

    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.plot(x_smooth, y_smooth, color=color, linewidth=linewidth, alpha=alpha)
    ax.axis("off")
    return True


_GENERATOR_SPECS: tuple[GeneratorSpec, ...] = (
    GeneratorSpec("julia-set", "Julia set", julia_set, ("julia", "julia_set", "1")),
    GeneratorSpec("hilbert-curve", "Hilbert curve", hilbert_curve, ("hilbert", "hilbert_curve", "2")),
    GeneratorSpec("lissajous", "Lissajous", lissajous, ("lissajous_curve", "3")),
    GeneratorSpec("voronoi-diagram", "Voronoi diagram", voronoi_diagram, ("voronoi", "voronoi_diagram", "4")),
    GeneratorSpec("bezier-curve", "Bezier curve", bezier_curve, ("bezier", "bezier_curve", "5")),
    GeneratorSpec("fractal", "Fractal", fractal, ("6",)),
    GeneratorSpec("attractor", "Attractor", attractor, ("7",)),
    GeneratorSpec("binary-pattern", "Binary pattern", binary_pattern, ("binary", "binary_pattern", "8")),
    GeneratorSpec("tensor-field", "Tensor field", tensor_field, ("tensor", "tensor_field", "9")),
)

_GENERATOR_LOOKUP: dict[str, GeneratorSpec] = {}
for spec in _GENERATOR_SPECS:
    _GENERATOR_LOOKUP[_normalize_key(spec.key)] = spec
    _GENERATOR_LOOKUP[_normalize_key(spec.label)] = spec
    _GENERATOR_LOOKUP[_normalize_key(spec.func.__name__)] = spec
    for alias in spec.aliases:
        _GENERATOR_LOOKUP[_normalize_key(alias)] = spec
