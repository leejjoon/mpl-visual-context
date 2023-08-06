from matplotlib.path import Path
from .patheffects_base import ChainablePathEffect


class Partial(ChainablePathEffect):
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


class Open(ChainablePathEffect):

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

