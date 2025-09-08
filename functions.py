import numpy as np
import random
import os
import librosa

from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.interpolate import make_interp_spline
from typing import Callable
from utils import Palette


def get_all_functions(ret_type: str | Callable = Callable) -> list[str | Callable]:
    r_list: list[Callable] = [
        julia_set,
        hilbert_curve,
        lissajous,
        voronoi_diagram,
        bezier_curve,
        fractal,
        attractor,
        binary_pattern,
        tensor_field,
    ]

    if ret_type not in (str, Callable):
        raise TypeError("Function has to be type str or Callable")

    if ret_type is str:
        return [i.__name__.strip().replace("_", " ").lower().capitalize() for i in r_list]
    if ret_type is Callable:
        return r_list


def julia_set(ax, palette: Palette, max_iteration: int = 256) -> None:
    """Classic Julia set with a random complex parameter."""

    x = np.linspace(-1.5, 1.5, img_size[0])
    y = np.linspace(-1.5, 1.5, img_size[1])
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    c = np.random.uniform(-0.8, 0.8) + 1j * np.random.uniform(-0.8, 0.8)
    img = np.zeros(Z.shape, dtype=int)

    for i in range(max_iteration):
        mask = np.abs(Z) < 2.0
        img[mask] = i
        Z[mask] = Z[mask] ** 2 + c
    idx = (img % len(palette)).astype(int)
    rgb = np.zeros((*img.shape, 3), dtype=np.uint8)
    for i, color in enumerate(palette):
        rgb[idx == i] = color
    ax.imshow(rgb, origin="lower")
    ax.axis("off")


def hilbert_curve(ax, palette: Palette) -> None:
    """Plot a Hilbert curve (order 6)."""

    def hilbert(n):
        def hilbert_recursive(x0, y0, xi, xj, yi, yj, n):
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
    ax.plot(x, y, color=palette[0])
    ax.axis("off")


def lissajous(ax, palette: Palette, randomize_start: bool = True) -> None:
    """Simple Lissajous curve with fixed frequency ratio."""

    t = np.linspace(0, 2 * np.pi, 1000)
    x = np.sin(3 * t)
    y = np.sin(4 * t)
    ax.plot(x, y, color=palette[0])
    ax.axis("off")


def voronoi_diagram(ax, palette: Palette) -> None:
    """Voronoi diagram filled with random palette colors."""

    n_points = np.random.randint(10, 35)
    points = np.random.rand(n_points, 2) * 2 - 1
    vor = Voronoi(points)
    voronoi_plot_2d(vor, ax=ax, show_points=False, show_vertices=False, line_colors="none")
    for i, region in enumerate(vor.regions):
        if not region or -1 in region:
            continue
        polygon = [vor.vertices[i] for i in region]
        ax.fill(*zip(*polygon), color=random.choice(palette))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")


def bezier_curve(ax, palette: Palette) -> None:
    """Smooth curve through random points using cubic spline as Bézier-like art."""

    n_points = np.random.randint(3, 8)
    points = np.random.rand(n_points, 2) * 2 - 1
    t = np.linspace(0, 1, 1000)
    spl = make_interp_spline(t, points, k=min(3, n_points - 1))
    smooth_points = spl(t)
    ax.plot(smooth_points[:, 0], smooth_points[:, 1], color=random.choice(palette))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")


def fractal(ax, palette: Palette) -> None:
    """Thresholded combination of sinusoidal fields over a grid."""

    freq1 = np.random.uniform(0.5, 3.5)
    freq2 = np.random.uniform(0.5, 3.5)
    phase = np.random.uniform(0, 2 * np.pi)
    x = np.linspace(-2, 2, self.img_size[0])
    y = np.linspace(-2, 2, self.img_size[1])
    X, Y = np.meshgrid(x, y)
    Z = np.sin(freq1 * (X**2 + Y**2) + phase)
    Z += np.cos(freq2 * (X * Y) + phase)
    img = np.zeros(Z.shape)
    img[Z > 0] = 1
    ax.imshow(img, origin="lower")
    ax.axis("off")


def attractor(ax, palette: Palette) -> None:
    """Clifford attractor variant with simple line plotting."""

    a, b, c, d = [np.random.uniform(-2.5, 2.5) for _ in range(4)]
    x, y = np.random.uniform(-1, 1), np.random.uniform(-1, 1)
    xs, ys = [], []
    for _ in range(5000):
        x, y = (
            np.sin(a * y) + c * np.cos(a * x),
            np.sin(b * x) + d * np.cos(b * y),
        )
        xs.append(x)
        ys.append(y)
    ax.plot(xs, ys, color=random.choice(palette), linewidth=0.7)
    ax.axis("off")


def binary_pattern(ax, palette: Palette) -> None:
    """Random palette-indexed grid with optional noise."""

    arr = np.random.randint(0, len(palette), size=img_size)
    if np.random.rand() > 0.5:
        arr = np.bitwise_xor(arr, np.random.randint(0, len(palette), size=self.img_size))
    img = np.zeros((*img_size, 3), dtype=np.uint8)
    for i, color in enumerate(palette):
        img[arr == i] = color
    if np.random.rand() > 0.5:
        img = np.clip(img + np.random.randint(0, 40, img.shape), 0, 255)
    ax.imshow(img, origin="lower")
    ax.axis("off")


def tensor_field(self, ax, palette: Palette) -> None:
    """Simple vector field using sine/cosine relations."""

    x = np.linspace(-2, 2, np.random.randint(5, 50))
    y = np.linspace(-2, 2, np.random.randint(5, 50))
    X, Y = np.meshgrid(x, y)
    U = np.sin(X) * np.cos(Y)
    V = -np.cos(X) * np.sin(Y)
    ax.quiver(X, Y, U, V, color=random.choice(palette))
    ax.axis("off")


@staticmethod
def lissajous_harmonics_from_music(
    ax,
    palette: Palette,
    binario: str,
    music_folder: str,
    randomize_start: bool = True,
    randomize_phases: bool = True,
) -> bool:
    """
    Generates a Lissajous harmonic image using the detected base frequency of the fundamental note
    from an audio file whose name matches the binary. If no audio is found, generates a generic Lissajous curve.
    """

    audio_file = None
    for fname in os.listdir(music_folder):
        if binario in fname and fname.lower().endswith((".mp3", ".wav", ".ogg", ".flac")):
            audio_file = os.path.join(music_folder, fname)
            break
    if audio_file is None:
        print(f"[INFO] No audio file found for {binario}. A generic Lissajous curve will be generated.")
        lissajous(ax, palette, randomize_start=randomize_start)
        return True

    # Process audio and generate harmonic curve
    try:
        y_audio, sr = librosa.load(audio_file, sr=None, mono=True, duration=10.0)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y_audio, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        freq_base = np.nanmedian(f0)
        if np.isnan(freq_base):
            freq_base = librosa.note_to_hz("C2")
    except Exception as e:
        print(f"Error analyzing {audio_file}: {e}")
        freq_base = librosa.note_to_hz("C2")

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
