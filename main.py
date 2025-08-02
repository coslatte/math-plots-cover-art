import os
import matplotlib.pyplot as plt
import numpy as np
import librosa
import colorsys
import datetime
import random
from PIL import Image, ImageEnhance, ImageFilter
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.interpolate import make_interp_spline

OUTPUT_DIR = "output"
# Tamaños de imagen disponibles
IMG_SIZES = {"normal": (1400, 1400), "hd": (5000, 5000)}
IMG_SIZE = IMG_SIZES["hd"]  # tamaño por defecto
IMG_COUNT = 15

# Paletas de colores modernas, oscuras y con mucha variedad
BASE_PALETTES = [
    [
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
    ],
    [
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
    ],
    [
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
    ],
    [
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
    ],
]


def random_palette():
    """
    Genera una paleta de colores fríos (azul, cian, violeta, azul-verde) con saturación media y luminosidad media-alta.
    Ocasionalmente (10%) agrega un color cálido (rojo, magenta).
    """
    palette = []
    n_colors = random.randint(8, 16)
    for _ in range(n_colors):
        if random.random() < 0.9:
            # 90%: tonos fríos (azul 200°–260°, cian 160°–200°, violeta 260°–300°)
            h_ranges = [(0.44, 0.56), (0.56, 0.72), (0.72, 0.83)]  # HSL: 160–300°
            h_range = random.choice(h_ranges)
            h = random.uniform(*h_range)
        else:
            # 10%: rojo/magenta (0°–30° y 330°–360°)
            if random.random() < 0.5:
                h = random.uniform(0.0, 0.08)
            else:
                h = random.uniform(0.92, 1.0)
        s = random.uniform(0.45, 0.7)  # saturación media
        l = random.uniform(0.48, 0.72)  # luminosidad media-alta
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        rgb = (int(r * 255), int(g * 255), int(b * 255))
        palette.append(rgb)
    random.shuffle(palette)
    return palette


def generate_julia_set(ax, palette):
    # Fractal de conjunto de Julia clásico
    x = np.linspace(-1.5, 1.5, IMG_SIZE[0])
    y = np.linspace(-1.5, 1.5, IMG_SIZE[1])
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    c = np.random.uniform(-0.8, 0.8) + 1j * np.random.uniform(-0.8, 0.8)
    img = np.zeros(Z.shape, dtype=int)
    max_iter = 256
    for i in range(max_iter):
        mask = np.abs(Z) < 2.0
        img[mask] = i
        Z[mask] = Z[mask] ** 2 + c
    idx = (img % len(palette)).astype(int)
    rgb = np.zeros((*img.shape, 3), dtype=np.uint8)
    for i, color in enumerate(palette):
        rgb[idx == i] = color
    ax.imshow(rgb, origin="lower")
    ax.axis("off")


def generate_hilbert_curve(ax, palette):
    # Curva de Hilbert (orden 6)
    def hilbert_curve(n):
        def hilbert(x0, y0, xi, xj, yi, yj, n):
            if n <= 0:
                x = x0 + (xi + yi) / 2
                y = y0 + (xj + yj) / 2
                return [(x, y)]
            else:
                return (
                    hilbert(x0, y0, yi / 2, yj / 2, xi / 2, xj / 2, n - 1)
                    + hilbert(
                        x0 + xi / 2, y0 + xj / 2, xi / 2, xj / 2, yi / 2, yj / 2, n - 1
                    )
                    + hilbert(
                        x0 + xi / 2 + yi / 2,
                        y0 + xj / 2 + yj / 2,
                        xi / 2,
                        xj / 2,
                        yi / 2,
                        yj / 2,
                        n - 1,
                    )
                    + hilbert(
                        x0 + xi / 2 + yi,
                        y0 + xj / 2 + yj,
                        -yi / 2,
                        -yj / 2,
                        -xi / 2,
                        -xj / 2,
                        n - 1,
                    )
                )

        return hilbert(0, 0, 1, 0, 0, 1, n)

    points = hilbert_curve(6)
    points = np.array(points)
    color = np.array(random.choice(palette)) / 255
    ax.plot(points[:, 0], points[:, 1], color=color, linewidth=2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def generate_lissajous(ax, palette, randomize_start=True):
    # Curvas de Lissajous
    if randomize_start:
        # --- Mejora de simetría: desfase aleatorio en t ---
        t_offset = np.random.uniform(0, 2 * np.pi)
        t = np.linspace(0, 2 * np.pi, 20000) + t_offset  # Alta resolución + desfase
        delta = np.random.uniform(0, np.pi)
    else:
        t = np.linspace(0, 2 * np.pi, 20000)
        delta = 0
    a = np.random.randint(1, 8)
    b = np.random.randint(1, 8)
    x = np.sin(a * t + delta)
    y = np.sin(b * t)
    color = np.array(random.choice(palette)) / 255
    ax.plot(x, y, color=color, linewidth=3, alpha=0.9)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.axis("off")


def generate_voronoi_art(ax, palette):
    # Arte de diagramas de Voronoi
    n_points = np.random.randint(10, 35)
    points = np.random.rand(n_points, 2) * 2 - 1
    vor = Voronoi(points)
    voronoi_plot_2d(
        vor, ax=ax, show_points=False, show_vertices=False, line_colors="none"
    )
    for i, region in enumerate(vor.regions):
        if not region or -1 in region:
            continue
        polygon = [vor.vertices[v] for v in region]
        color = np.array(palette[i % len(palette)]) / 255
        ax.fill(*zip(*polygon), color=color, alpha=np.random.uniform(0.7, 1.0))
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.axis("off")


def generate_bezier_art(ax, palette):
    # Arte con curvas de Bézier
    n_curves = np.random.randint(8, 20)
    for i in range(n_curves):
        points = np.random.rand(np.random.randint(3, 7), 2)
        points = points[np.argsort(points[:, 0])]
        x = points[:, 0]
        y = points[:, 1]
        xnew = np.linspace(x.min(), x.max(), 300)
        if len(x) >= 4:
            spl = make_interp_spline(x, y, k=3)
            ynew = spl(xnew)
        elif len(x) >= 2:
            spl = make_interp_spline(x, y, k=len(x) - 1)
            ynew = spl(xnew)
        else:
            continue
        color = np.array(palette[i % len(palette)]) / 255
        ax.plot(
            xnew,
            ynew,
            color=color,
            linewidth=np.random.uniform(2, 7),
            alpha=np.random.uniform(0.5, 1.0),
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def generate_fractal(ax, palette):
    # Variar parámetros para mayor diversidad
    freq1 = np.random.uniform(0.5, 3.5)
    freq2 = np.random.uniform(0.5, 3.5)
    phase = np.random.uniform(0, 2 * np.pi)
    x = np.linspace(-2, 2, IMG_SIZE[0])
    y = np.linspace(-2, 2, IMG_SIZE[1])
    X, Y = np.meshgrid(x, y)
    Z = np.sin(freq1 * (X**2 + Y**2) + phase)
    Z += np.cos(freq2 * (X * Y) + phase)
    Z = (Z - Z.min()) / (Z.max() - Z.min())
    idx = (Z * (len(palette) - 1)).astype(int)
    img = np.zeros((*Z.shape, 3), dtype=np.uint8)
    for i, color in enumerate(palette):
        img[idx == i] = color
    ax.imshow(img, origin="lower")
    ax.axis("off")


def generate_attractor(ax, palette):
    # Atractor de Clifford
    # Atractor de Clifford con más variabilidad
    a, b, c, d = [np.random.uniform(-2.5, 2.5) for _ in range(4)]
    x, y = np.random.uniform(-1, 1), np.random.uniform(-1, 1)
    points = []
    n_points = np.random.randint(150000, 250000)
    for _ in range(n_points):
        x_new = np.sin(a * y) + c * np.cos(a * x)
        y_new = np.sin(b * x) + d * np.cos(b * y)
        x, y = x_new, y_new
        points.append([x, y])
    points = np.array(points)
    palette_norm = [tuple(np.array(col) / 255) for col in palette]
    ax.scatter(
        points[:, 0],
        points[:, 1],
        s=np.random.uniform(0.05, 0.2),
        c=[palette_norm[i % len(palette_norm)] for i in range(len(points))],
        marker=",",
        alpha=np.random.uniform(0.3, 0.7),
    )
    ax.axis("off")


def generate_binary_pattern(ax, palette):
    # Patrón binario tipo matriz
    # Patrón binario tipo matriz con más variabilidad
    arr = np.random.randint(0, len(palette), size=IMG_SIZE)
    # Añadir ruido y distorsión
    if np.random.rand() > 0.5:
        arr = np.bitwise_xor(arr, np.random.randint(0, len(palette), size=IMG_SIZE))
    img = np.zeros((*IMG_SIZE, 3), dtype=np.uint8)
    for i, color in enumerate(palette):
        img[arr == i] = color
    if np.random.rand() > 0.5:
        img = np.roll(img, np.random.randint(1, 100), axis=np.random.choice([0, 1]))
    ax.imshow(img, origin="lower")
    ax.axis("off")


def generate_tensor_field(ax, palette):
    # Visualización de campo tensorial (direcciones) con más variabilidad
    x = np.linspace(-2, 2, np.random.randint(5, 50))
    y = np.linspace(-2, 2, np.random.randint(5, 50))
    X, Y = np.meshgrid(x, y)
    freq = np.random.uniform(0.5, 5)
    U = np.sin(freq * X * Y) + np.cos(freq * Y)
    V = np.cos(freq * X * Y) - np.sin(freq * X)
    palette_norm = [tuple(np.array(col) / 255) for col in palette]
    color = random.choice(palette_norm)
    ax.streamplot(
        X,
        Y,
        U,
        V,
        color=color,
        linewidth=np.random.uniform(1, 3),
        density=np.random.uniform(1.5, 2.5),
    )
    ax.axis("off")


def generate_math_art(ax, palette):
    # Elegir aleatoriamente el tipo de figura matemática a dibujar
    options = [
        generate_fractal,
        generate_attractor,
        generate_binary_pattern,
        generate_tensor_field,
        generate_voronoi_art,
        generate_bezier_art,
        generate_julia_set,
        generate_hilbert_curve,
        generate_lissajous,
    ]
    func = np.random.choice(options)
    try:
        func(ax, palette)
    except Exception as e:
        print(f"Falló la generación: {e.with_traceback()}")


def postprocess_image(img: Image.Image, apply_filters: bool = True) -> Image.Image:
    """
    Postprocesa la imagen solo con saturación moderada y desenfoque. Sin distorsión ni efectos extra.
    """
    # Saturación más baja
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(np.random.uniform(1.08, 1.18))

    # Pequeño desenfoque
    if np.random.rand() > 0.5:
        img = img.filter(ImageFilter.GaussianBlur(radius=np.random.uniform(0.5, 1.5)))
    return img


def generate_lissajous_harmonics_from_music(
    ax, palette, binario, music_folder, randomize_start=True, randomize_phases=True
):
    """
    Genera una imagen de Lissajous armónicos usando la frecuencia base detectada de la nota fundamental
    de un archivo de audio cuyo nombre coincide con el binario. Si no hay audio, genera una curva de Lissajous genérica.
    Optimizada para suavidad, velocidad y un toque artístico.
    """
    import os
    import numpy as np
    import random
    from scipy.interpolate import make_interp_spline

    # Buscar archivo de audio
    audio_file = None
    for fname in os.listdir(music_folder):
        if binario in fname and fname.lower().endswith(
            (".mp3", ".wav", ".ogg", ".flac")
        ):
            audio_file = os.path.join(music_folder, fname)
            break
    if audio_file is None:
        print(
            f"[INFO] No se encontró archivo de audio para {binario}. Se generará una curva de Lissajous genérica."
        )
        generate_lissajous(ax, palette, randomize_start=randomize_start)
        return True

    # Procesar audio y generar curva armónica
    try:
        y_audio, sr = librosa.load(audio_file, sr=None, mono=True, duration=10.0)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y_audio, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        freq_base = np.nanmedian(f0)
        if np.isnan(freq_base):
            freq_base = librosa.note_to_hz("C2")
    except Exception as e:
        print(f"Error analizando {audio_file}: {e}")
        freq_base = librosa.note_to_hz("C2")

    N = int(binario, 2)
    if N == 0:
        N = 3  # mínimo

    # --- OPTIMIZACIÓN ---
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

    # Normalización
    x /= np.max(np.abs(x))
    y /= np.max(np.abs(y))

    # Spline cúbico para suavidad
    t_smooth = np.linspace(t.min(), t.max(), N_SPLINE, dtype=np.float32)
    spl_x = make_interp_spline(t, x, k=3)
    spl_y = make_interp_spline(t, y, k=3)
    x_smooth = spl_x(t_smooth)
    y_smooth = spl_y(t_smooth)

    # Normalización post-spline
    x_smooth /= np.max(np.abs(x_smooth))
    y_smooth /= np.max(np.abs(y_smooth))

    # Toque artístico: ruido sutil
    noise_strength = 0.002
    x_smooth += np.random.normal(0, noise_strength, size=x_smooth.shape)
    y_smooth += np.random.normal(0, noise_strength, size=y_smooth.shape)

    # Color y estilo artístico
    color = np.clip(
        np.array(random.choice(palette)) / 255 + np.random.uniform(-0.05, 0.05, 3), 0, 1
    )
    linewidth = np.random.uniform(1.8, 2.6)
    alpha = np.random.uniform(0.82, 0.95)

    ax.plot(x_smooth, y_smooth, color=color, linewidth=linewidth, alpha=alpha)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.axis("off")
    return True


def save_images():
    # Lista de binarios en el orden dado
    BINARIOS = [
        "01001",
        "01100",
        "01111",
        "10000",
        "10100",
        "10101",
        "10111",
        "11001",
        "11100",
        "11101",
        "11110",
        "11111",
    ]
    # Crear subcarpeta única por corrida
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(OUTPUT_DIR, f"arte_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)

    options = [
        ("fractal", generate_fractal),
        ("attractor", generate_attractor),
        ("binary_pattern", generate_binary_pattern),
        ("tensor_field", generate_tensor_field),
        ("lissajous_musical", None),  # Se manejará aparte
        ("voronoi", generate_voronoi_art),
        ("bezier", generate_bezier_art),
        # ("julia_set", generate_julia_set),
        ("hilbert_curve", generate_hilbert_curve),
        ("lissajous", generate_lissajous),
    ]

    def generar_imagen(name, func, i, palette, BINARIOS, run_dir):

        type_dir = os.path.join(run_dir, name)
        os.makedirs(type_dir, exist_ok=True)
        fig, ax = plt.subplots(figsize=(IMG_SIZE[0] / 100, IMG_SIZE[1] / 100), dpi=100)
        ax.set_facecolor(np.array(random.choice(palette)) / 255)
        if name == "lissajous_musical":
            idx = i % len(BINARIOS)
            binario = BINARIOS[idx]
            music_folder = r"D:\Coding\Projects\hobbie\random\python-project\music"
            from main import generate_lissajous_harmonics_from_music

            success = generate_lissajous_harmonics_from_music(
                ax,
                palette,
                binario,
                music_folder,
                randomize_start=True,
                randomize_phases=True,
            )
            if not success:
                plt.close(fig)
                return
        else:
            func(ax, palette)
        final_path = os.path.join(type_dir, f"album_cover_{name}_{i + 1}.png")
        fig.savefig(
            final_path,
            dpi=100,
            bbox_inches="tight",
            pad_inches=0,
            transparent=False,
        )
        plt.close(fig)
        print(f"Imagen guardada: {final_path}")

    tasks = []
    for name, func in options:
        palette = random_palette()
        for i in range(IMG_COUNT):
            tasks.append((name, func, i, palette, BINARIOS, run_dir))

    # Ejecución secuencial para depuración
    for args in tasks:
        try:
            generar_imagen(*args)
        except Exception as e:
            print(f"Error generando imagen {args[0]}_{args[2]+1}: {e}")


if __name__ == "__main__":
    save_images()
