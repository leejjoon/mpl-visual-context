import numpy as np
from matplotlib.patheffects import AbstractPathEffect
import matplotlib.transforms as mtransforms
from matplotlib import colormaps


class Glow(AbstractPathEffect):
    """
    Patheffect with glow effect. Adopted from mplcybepunk.
    Each existing line is redrawn several times with increasing
    width and low alpha to create the glow effect.
    """
    def __init__(
        self,
        n_glow_lines: int = 10,
        diff_linewidth: float = 1.05,
        alpha_line: float = 0.3,
        offset=(0, 0),
    ):
        self.n_glow_lines = n_glow_lines
        self.diff_linewidth = diff_linewidth
        self.alpha_line = alpha_line
        self.xoffset = offset[0]
        self.yoffset = offset[1]

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        alpha0 = gc.get_alpha()

        aa = np.arange(1, self.n_glow_lines + 1)
        linewidths = gc0.get_linewidth() + aa * self.diff_linewidth

        gc0.set_alpha(alpha0 * self.alpha_line / self.n_glow_lines)

        oo = np.linspace(0, 1, self.n_glow_lines)

        for lw, o in zip(linewidths, oo):
            gc0.set_linewidth(lw)
            offset = mtransforms.Affine2D().translate(
                *map(renderer.points_to_pixels, [o * self.xoffset, o * self.yoffset])
            )

            renderer.draw_path(gc0, tpath, affine + offset, None)


class CmapGlow(AbstractPathEffect):
    """Patheffect similar to Glow, but with different colors basedon the given
    colormap.

    """
    def __init__(
        self,
        cmap,
        nlevel=10,
        diff_linewidth=5,
        alpha_line: float = 0.3,
        xoffset=0,
        yoffset=0,
    ):
        self.cmap = colormaps.get_cmap(cmap)
        self.nlevel = nlevel
        self.diff_linewidth = diff_linewidth
        self.alpha_line = alpha_line
        self.xoffset = xoffset
        self.yoffset = yoffset

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        alpha0 = gc.get_alpha()

        aa = np.linspace(1, 0, self.nlevel)
        linewidths = gc0.get_linewidth() + aa * self.diff_linewidth

        if self.alpha_line is not None:
            gc0.set_alpha(alpha0 * self.alpha_line / self.nlevel)

        oo = np.linspace(1, 0, self.nlevel)

        for lw, o in zip(linewidths, oo):
            gc0.set_linewidth(lw)
            gc0.set_foreground(self.cmap(o))
            offset = mtransforms.Affine2D().translate(
                *map(renderer.points_to_pixels, [o * self.xoffset, o * self.yoffset])
            )

            renderer.draw_path(gc0, tpath, affine + offset, None)
