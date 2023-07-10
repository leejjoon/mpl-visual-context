import numpy as np
from matplotlib.patheffects import AbstractPathEffect

class GlowStroke(AbstractPathEffect):
    def __init__(self,
                 n_glow_lines: int = 10,
                 diff_linewidth: float = 1.05,
                 alpha_line: float = 0.3):
        self.n_glow_lines = n_glow_lines
        self.diff_linewidth = diff_linewidth
        self.alpha_line = alpha_line

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        alpha0 = gc.get_alpha()

        aa = np.arange(1, self.n_glow_lines+1)
        linewidths = gc0.get_linewidth() + aa*self.diff_linewidth

        gc0.set_alpha(alpha0 * self.alpha_line / self.n_glow_lines)

        renderer.draw_path(
            gc, tpath, affine, rgbFace)

        for lw in linewidths:
            gc0.set_linewidth(lw)
            renderer.draw_path(
                gc0, tpath, affine, rgbFace)

