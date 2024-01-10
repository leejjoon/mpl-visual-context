"""
Defines classes for path effects that modifies color.
"""

from abc import abstractmethod
import numpy as np
import matplotlib.colors as mcolors

from .hls_helper import HLSModify_axb, _convert_scale_or_const
from . import color_matrix as CM

from .patheffects_base import ChainablePathEffect


class ColorModifyStroke(ChainablePathEffect):
    """
    A base class for path effects that modifies color.

    Subclasses should override the ``apply_to_color_path`` method that returns a new color.
    """

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
    """
    PathEffect which modifies the color in HLS space. Given
    a tuple of (a, b), the new color is defiend as h' = a * h + b, and so on.
    Both stroke and fill color are changed.
    """
    def __init__(
        self, h_ab=(1, 0), l_ab=(1, 0), s_ab=(1, 0), alpha_ab=(1, 0), clip_mode="clip"
    ):
        super().__init__()
        self._modifier = HLSModify_axb(h_ab, l_ab, s_ab, alpha_ab, clip_mode=clip_mode)

    def apply_to_color(self, c):
        return self._modifier.apply_to_color(c)

    def __repr__(self):
        return repr(self._modifier)


class HLSModify(HLSaxb):
    """
    PathEffect which modifies the color in HLS space.
    Both stroke and fill color are changed.
    """

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
    """
    PathEffect which modifies the color in RGB space, using a predefined
    color matrix. Supported matrix are 'grayscale', 'sepia', 'nightvision',
    'warm' and 'cool.
    Both stroke and fill color are changed.
    """
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
    """PathEffect to set the fill color"""
    def __init__(self, fillcolor):
        self._fillcolor = None if fillcolor is None else mcolors.to_rgba(fillcolor)

    def _convert(self, renderer, gc, tpath, affine, rgbFace):

        return renderer, gc, tpath, affine, self._fillcolor


class StrokeColor(ChainablePathEffect):
    """PathEffect to set the stoke color"""
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
    """PathEffect to set the stoke color by the fill color"""
    def __init__(self):
        super().__init__()

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)
        gc0.set_foreground(rgbFace)

        return renderer, gc0, tpath, affine, rgbFace


class FillColorFromStrokeColor(ChainablePathEffect):
    """PathEffect to set the fill color by the stroke color"""
    def __init__(self):
        super().__init__()

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        # GC does not have get_foreground or instead it has get_rgb, which
        # return rgba. We simply remove a.
        rgbFace_new = gc.get_rgb()[:3]

        return renderer, gc, tpath, affine, rgbFace_new


class BlendAlpha(ChainablePathEffect):
    """Remove the alpha channel by blending the original color (w/ alpha) with
    the given backgrond color.
    """
    def __init__(self, bg_color):
        self._bg_color = bg_color

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        gc1 = renderer.new_gc()
        gc1.copy_properties(gc)

        bg_rgb = np.array(mcolors.to_rgb(self._bg_color))

        rgba_new = gc.get_rgb()
        rgb_new = np.array(rgba_new[:3])
        alpha = rgba_new[3]
        # gc.get_alpha()
        gc1.set_foreground(rgb_new*alpha + bg_rgb*(1-alpha))
        gc1.set_alpha(1)

        if rgbFace is not None:
            alpha = rgbFace[-1]
            rgbFace = np.asarray(rgbFace)
            rgbFace2 = np.ones_like(rgbFace)
            rgbFace2[:3] = rgbFace[:3]*alpha + bg_rgb[:3]*(1-alpha)
        else:
            rgbFace2 = rgbFace

        return renderer, gc1, tpath, affine, rgbFace2


class ColorFromFunc(ChainablePathEffect):
    """PathEffect to set the stoke color from a function. The function should
    take stroke-color and fill color and return new stroke-color and
    fill-color."""
    def __init__(self, func):
        super().__init__()
        self._func = func

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        # change the stroke color
        stroke_color, fill_color = self._func(gc0.get_rgb()[:3], rgbFace)
        gc0.set_foreground(stroke_color)

        return renderer, gc0, tpath, affine, fill_color
