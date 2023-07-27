from abc import abstractmethod
import numpy as np
from matplotlib.patheffects import AbstractPathEffect
import matplotlib.colors as mcolors
from matplotlib.path import Path

from .hls_helper import HLSModifier
from . import color_matrix as CM


class ChainablePathEffect(AbstractPathEffect):

    def __or__(self, other):
        return ChainedStroke(self, other)

    @abstractmethod
    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        return renderer, gc, tpath, affine, rgbFace

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        renderer, gc, tpath, affine, rgbFace = self._convert(
            renderer, gc, tpath, affine, rgbFace
        )
        renderer.draw_path(gc, tpath, affine, rgbFace)

class ChainedStroke(ChainablePathEffect):
    def __init__(self, pe1: ChainablePathEffect, pe2: ChainablePathEffect):
        if isinstance(pe1, ChainedStroke):
            self._pe_list = pe1._pe_list + [pe2]
        else:
            self._pe_list = [pe1, pe2]

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        for pe in self._pe_list:
            renderer, gc, tpath, affine, rgbFace = pe._convert(
                renderer, gc, tpath, affine, rgbFace
            )
        return renderer, gc, tpath, affine, rgbFace

    def __repr__(self):
        s = " | ".join([repr(pe) for pe in self._pe_list])
        return "ChainedStroke({})".format(s)


class PartialStroke(ChainablePathEffect):
    def __init__(self, start, stop):
        super().__init__()
        self._start = start
        self._stop = stop

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices
        n = len(codes)
        start, stop = self._start, self._stop
        start = start if isinstance(start, int) else int(start*n)
        stop = stop if isinstance(stop, int) else int(stop*n)

        # FIXME It does not support splines yet.
        vertices = vertices[start:stop]
        codes = codes[start:stop]
        codes[0] = tpath.MOVETO

        new_tpath = Path._fast_from_codes_and_verts(vertices, codes)

        return renderer, gc, new_tpath, affine, rgbFace


class OpenStroke(ChainablePathEffect):

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices

        codes = [c if c != tpath.CLOSEPOLY else tpath.STOP
                 for c in codes]

        new_tpath = Path._fast_from_codes_and_verts(vertices, codes)

        return renderer, gc, new_tpath, affine, rgbFace


class StrokeOnly(ChainablePathEffect):

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

        return renderer, gc, tpath, affine, None


class FillOnly(ChainablePathEffect):

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)
        gc0.set_linewidth(0)

        return renderer, gc0, tpath, affine, rgbFace


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
