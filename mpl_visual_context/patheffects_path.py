from matplotlib.path import Path
import matplotlib.transforms as mtransforms
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


class ClipPathFromPatch(ChainablePathEffect):

    def __init__(self, patch):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self.patch = patch

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        if self.patch is not None:
            gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
            gc0.copy_properties(gc)
            pp = mtransforms.TransformedPath(self.patch.get_path(),
                                             self.patch.get_transform())
            gc0.set_clip_path(pp)
        else:
            gc0 = gc

        return renderer, gc0, tpath, affine, rgbFace


class ClipPathSelf(ChainablePathEffect):

    def __init__(self):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
        gc0.copy_properties(gc)
        pp = mtransforms.TransformedPath(tpath, affine)
        gc0.set_clip_path(pp)

        return renderer, gc0, tpath, affine, rgbFace
