from abc import abstractmethod
import numpy as np
from matplotlib.patheffects import AbstractPathEffect
import matplotlib.colors as mcolors

from .hls_helper import HLSModifier
from . import color_matrix as CM

class ColorModifyStroke(AbstractPathEffect):
    @abstractmethod
    def apply_to_color(self, c):
        pass

    def __ror__(self, other):
        return ChainedColorStroke(self, other)

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


class ChainedColorStroke(ColorModifyStroke):
    def __init__(self, cms1: ColorModifyStroke, cms2: ColorModifyStroke):
        if isinstance(cms1, ChainedColorStroke):
            self._cms_list = cms1._cms_list + [cms2]
        else:
            self._cms_list = [cms1, cms2]

    def apply_to_color(self, c):
        for _cms in self._cms_list:
            c = _cms.apply_to_color(c)

        return c

    def __repr__(self):
        s = " | ".join([repr(cms) for cms in self._cms_list])
        return "ChainedColorStroke({})".format(s)


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

    def __repr__(self):
        h, l, s = self._modifier.hls
        a = self._modifier.alpha
        dh, dl, ds = self._modifier.d_hls
        da = self._modifier.d_alpha

        return f"HLSModifyStrke(h={h}, l={l}, s={s}, a={a}, dh={dh}, dl={dl}, ds={ds}, da={da})"


class ColorMatrixStroke(ColorModifyStroke):
    _color_matrix = CM._get_matrix()

    def __init__(self, kind):
        self._kind = kind
        self._m = self._color_matrix[kind]

    def apply_to_color(self, c):
        c_rgba = mcolors.to_rgba(c)

        c_rgb = c_rgba[:3]
        alpha = c_rgba[3]

        c_rgb_new = np.clip(self._m @ c_rgb, 0, 1)

        return np.append(c_rgb_new, alpha)

    def __repr__(self):
        return f"ColorMatrix({self._kind})"
