from abc import abstractmethod
from matplotlib.patheffects import AbstractPathEffect

from .pe_colors import HLSModifier

class ColorModifyStroke(AbstractPathEffect):
    @abstractmethod
    def apply_to_color(self, c):
        pass

    def __or__(self, other):
        return MultiColorStroke(self, other)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        # change the stroke color
        rgb = self.apply_to_color(gc0.get_rgb())
        gc0.set_foreground(rgb)

        # chage the fill color
        if rgbFace is not None:
            rgbFace = self.apply_to_color(rgbFace)
        renderer.draw_path(
            gc0, tpath, affine, rgbFace)


class MultiColorStroke(ColorModifyStroke):
    def __init__(self, *sl):
        self._pe_list = sl

    def apply_to_color(self, c):
        for pe in self._pe_list:
            c = pe.apply_to_color(c)

        return c

class HLSModifyStroke(ColorModifyStroke):
    """A line based PathEffect which re-draws a stroke."""

    def __init__(self, h="100%", l="100%", s="100%", alpha="100%",
                 dh=0, dl=0, ds=0, dalpha=0):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self._modifier = HLSModifier(h, l, s, alpha, dh, dl, ds, dalpha)

    def apply_to_color(self, c):
        return self._modifier.apply_to_color(c)

