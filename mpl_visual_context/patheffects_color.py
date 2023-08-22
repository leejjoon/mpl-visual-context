from abc import abstractmethod
import numpy as np
import matplotlib.colors as mcolors

from .hls_helper import HLSModify_axb, _convert_scale_or_const
from . import color_matrix as CM

from .patheffects_base import ChainablePathEffect


class ColorModifyStroke(ChainablePathEffect):
    @abstractmethod
    def apply_to_color(self, c):
        pass

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        # change the stroke color
        rgb = self.apply_to_color(gc0.get_rgb())
        gc0.set_foreground(rgb)

        # chage the fill color
        if rgbFace is not None:
            rgbFace = self.apply_to_color(rgbFace)

        return renderer, gc0, tpath, affine, rgbFace


class HLSaxb(ColorModifyStroke):
    def __init__(
        self, h_ab=(1, 0), l_ab=(1, 0), s_ab=(1, 0), alpha_ab=(1, 0), clip_mode="clip"
    ):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self._modifier = HLSModify_axb(h_ab, l_ab, s_ab, alpha_ab, clip_mode=clip_mode)

    def apply_to_color(self, c):
        return self._modifier.apply_to_color(c)

    def __repr__(self):
        return repr(self._modifier)


class HLSModify(HLSaxb):
    """A line based PathEffect which re-draws a stroke."""

    def __init__(
        self,
        h="100%",
        l="100%",
        s="100%",
        alpha="100%",
        dh=0,
        dl=0,
        ds=0,
        dalpha=0,
        clip_mode="clip",
    ):
        hls_ab = [_convert_scale_or_const(v) for v in [h, l, s, alpha]]
        h, l, s, alpha = [
            (a, b + dd) for (a, b), dd in zip(hls_ab, [dh, dl, ds, dalpha])
        ]

        super().__init__(h_ab=h, l_ab=l, s_ab=s, alpha_ab=alpha, clip_mode=clip_mode)


class ColorMatrix(ColorModifyStroke):
    color_matrix = CM._get_matrix()

    def __init__(self, kind):
        self._kind = kind
        self._m = self.color_matrix[kind]

    def apply_to_color(self, c):
        c_rgba = mcolors.to_rgba(c)

        c_rgb = c_rgba[:3]
        alpha = c_rgba[3]

        c_rgb_new = np.clip(self._m @ c_rgb, 0, 1)

        return np.append(c_rgb_new, alpha)

    def __repr__(self):
        return f"ColorMatrix({self._kind})"


class FillColor(ChainablePathEffect):
    def __init__(self, fillcolor):
        self._fillcolor = mcolors.to_rgba(fillcolor) if fillcolor else None

    def _convert(self, renderer, gc, tpath, affine, rgbFace):

        return renderer, gc, tpath, affine, self._fillcolor


class StrokeColor(ChainablePathEffect):
    def __init__(self, c):
        super().__init__()
        self._stroke_color = c

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)
        fg = mcolors.to_rgba(self._stroke_color)
        gc0.set_foreground(fg)

        return renderer, gc0, tpath, affine, rgbFace


class StrokeColorFromFillColor(ChainablePathEffect):
    def __init__(self):
        super().__init__()

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)
        gc0.set_foreground(rgbFace)

        return renderer, gc0, tpath, affine, rgbFace


class FillColorFromStrokeColor(ChainablePathEffect):
    def __init__(self):
        super().__init__()

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        # GC does not have get_foreground or instead it has get_rgb, which
        # return rgba. We simply remove a.
        rgbFace_new = gc.get_rgb()[:3]

        return renderer, gc, tpath, affine, rgbFace_new
