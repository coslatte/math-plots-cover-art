from pathlib import Path
import re
from typing import Callable

import random

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .utils import Constants, ImageProperties, Palette, Resolution, State


class Brain:
    def __init__(self) -> None:
        self._output_path: Path = Constants.DEFAULT_PATH
        self._img_count: int = Constants.DEFAULT_IMG_COUNT
        self._img_size: Resolution = ImageProperties.Resolution.NORMAL.value
        self._dpi: int = 100
        self._color_palette: Palette = list(Constants.DEFAULT_BASE_PALETTE)
        self._prefer_gpu: bool = True

    ##############
    # PROPERTIES #
    ##############

    @property
    def output_path(self) -> Path:
        """Get the current output path for saving images."""

        return self._output_path

    @output_path.setter
    def output_path(self, path: Path) -> None:
        """Set the output path for saving images."""

        self._output_path = path

    @property
    def img_size(self) -> Resolution:
        """Get the current image size (resolution)."""

        return self._img_size

    @img_size.setter
    def img_size(self, size: Resolution) -> None:
        """Set the image size (resolution)."""

        self._img_size = size

    @property
    def dpi(self) -> int:
        """Get the current figure DPI."""

        return self._dpi

    @dpi.setter
    def dpi(self, value: int) -> None:
        """Set the figure DPI used for rendering and export."""

        self._dpi = value

    @property
    def img_count(self) -> int:
        """Get the current image count."""

        return self._img_count

    @img_count.setter
    def img_count(self, count: int) -> None:
        """Set the current image count."""

        self._img_count = count

    @property
    def color_palette(self) -> Palette:
        """Get the current color palette."""

        return self._color_palette

    @color_palette.setter
    def color_palette(self, palette: Palette) -> None:
        """Set the current color palette."""

        self._color_palette = palette

    @property
    def prefer_gpu(self) -> bool:
        """Return whether optional hardware acceleration should be used."""

        return self._prefer_gpu

    @prefer_gpu.setter
    def prefer_gpu(self, value: bool) -> None:
        """Enable or disable optional hardware acceleration."""

        self._prefer_gpu = value

    #############
    # FUNCTIONS #
    #############

    def _safe_name(self, name: str) -> str:
        """Return a filesystem-safe name for folders and files."""

        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")
        return safe_name or "image"

    def generate_image(self, func: Callable[..., None], palette: Palette | None = None) -> tuple[Figure, Axes]:
        """Create a figure/axes, set background, invoke the plotting function, and return fig/ax."""

        active_palette = palette or self.color_palette
        fig, ax = plt.subplots(figsize=(self.img_size[0] / self.dpi, self.img_size[1] / self.dpi), dpi=self.dpi)
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        fig.patch.set_facecolor("black")

        face_color = tuple(channel / 255 for channel in random.choice(active_palette))
        ax.set_facecolor(face_color)
        fig.patch.set_facecolor(face_color)
        ax.set_position([0, 0, 1, 1])
        ax.set_axis_off()

        func(ax, active_palette, img_size=self.img_size, prefer_gpu=self.prefer_gpu)

        return fig, ax

    def save_image(
        self,
        name: str,
        func: Callable[..., None],
        output_dir: Path,
        palette: Palette | None = None,
        index: int = 1,
        image_format: str = "png",
    ) -> Path:
        if image_format not in ("png", "jpeg", "svg"):
            raise ValueError("Image format not allowed")

        fig, _ax = self.generate_image(func=func, palette=palette)
        safe_name = self._safe_name(name)

        # Build file path as: <output_dir>/<name>/<name>_<index>.ext
        dir_path = output_dir / safe_name
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{safe_name}_{index}.{image_format}"

        try:
            fig.savefig(
                file_path,
                dpi=self.dpi,
                pad_inches=0,
                transparent=False,
                format=image_format,
            )
            print(f"Saved image: {file_path}")
            return file_path
        finally:
            plt.close(fig)

    # def save_images(self, output_dir: Path | None = None, count: int | None = None) -> None:
    #     """Generate and save a batch of images for each available option."""

    #     out_dir = output_dir or self.output_path
    #     n = count or self.img_count

    #     # Create subfolder per run
    #     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #     run_dir = out_dir / f"art_{timestamp}"
    #     run_dir.mkdir(parents=True, exist_ok=True)

    #     for name, func in OPTIONS.items():
    #         for i in range(1, n + 1):
    #             palette = random_palette()
    #             try:
    #                 save_image(name=name, func=func, output_dir=run_dir, palette=palette, index=i)
    #             except Exception as e:
    #                 print(f"Error generando imagen {name}_{i}: {e}")


class GraphicableEntity:
    def __init__(self, name: str, func: Callable[..., None], palette: Palette, output_dir: Path) -> None:
        self.name = name
        self.func = func
        self.palette = palette
        self.output_dir = output_dir

    def render(self) -> State:
        """Renders and save the graphicable entity.

        Returns:
            State: the way if the State was successful or not.
        """

        try:
            brain = Brain()
            brain.save_image(name=self.name, func=self.func, output_dir=self.output_dir, palette=self.palette, index=1)

            print(f"Generated one {self.name} image in {self.output_dir}")
            return State.SUCCESS
        except (OSError, ValueError, RuntimeError, TypeError, ImportError) as error:
            print(f"Error generating '{self.name}' image in {self.output_dir}: {error}")
            return State.FAILURE
