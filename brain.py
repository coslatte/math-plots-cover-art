from pathlib import Path
from typing import Callable, Tuple
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import numpy as np
import random

from utils import Constants, ImageProperties, Palette, Resolution, State


class Brain:
    def __init__(self):
        self._output_path = Constants.DEFAULT_PATH
        self._img_count = Constants.DEFAULT_IMG_COUNT
        self._img_size = ImageProperties.Resolution.NORMAL
        self._color_palette = Constants.DEFAULT_BASE_PALETTE
        # self.dpi =

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
    def img_size(self, size: Tuple[int, int]) -> None:
        """Set the image size (resolution)."""

        self._img_size = size

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

    #############
    # FUNCTIONS #
    #############

    def generate_image(self, func: Callable[[Axes, Palette], None], palette: Palette) -> Tuple[Figure, Axes]:
        """Create a figure/axes, set background, invoke the plotting function, and return fig/ax."""

        fig, ax = plt.subplots(figsize=(self.img_size[0] / 100, self.img_size[1] / 100), dpi=100)

        ax.set_facecolor(np.array(random.choice(palette)) / 255)

        func(ax, palette)

        return fig, ax

    def save_image(
        self,
        name: str,
        func: Callable[[plt.Axes, Palette], None],
        output_dir: Path,
        palette: Palette,
        index: int = 1,
        format: str = "png",
    ) -> None:
        if format not in ("png", "jpeg", "svg"):
            raise ValueError("Image format not allowed")

        fig, ax = self.generate_image(name=name, func=func, palette=palette)

        # Build file path as: <output_dir>/<name>/<name>_<index>.ext
        dir_path = output_dir / name
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / f"{name}_{index}.{format}"

        fig.savefig(
            file_path,
            dpi=100,
            bbox_inches="tight",
            pad_inches=0,
            transparent=False,
            format=format,
        )

        plt.close(fig)
        print(f"Imagen guardada: {file_path}")

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
    def __init__(self, name: str, func: Callable, palette: Palette, output_dir: Path):
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
            Brain.save_image(name=self.name, func=self.func, output_dir=self.output_dir, palette=self.palette, index=1)

            print(f"Generated one {self.name} image in {self.output_dir}")
            return State.SUCCESS
        except Exception as e:
            print(f"Error genearting '{self.name}' image in {self.output_dir}: {e.with_traceback}")
            return State.FAILURE
