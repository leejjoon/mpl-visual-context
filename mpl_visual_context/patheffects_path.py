import numpy as np
from matplotlib.path import Path
import matplotlib.transforms as mtransforms
from matplotlib.transforms import Bbox
from .patheffects_base import ChainablePathEffect
from .image_box import TR


class Partial(ChainablePathEffect):
    def __init__(self, start, stop):
        super().__init__()
        self._start = start
        self._stop = stop

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices
        n = len(codes)
        start, stop = self._start, self._stop
        start = start if isinstance(start, int) else int(start * n)
        stop = stop if isinstance(stop, int) else int(stop * n)

        # FIXME It does not support splines yet.
        vertices = vertices[start:stop]
        codes = codes[start:stop]
        codes[0] = tpath.MOVETO

        new_tpath = Path._fast_from_codes_and_verts(vertices, codes)

        return renderer, gc, new_tpath, affine, rgbFace


class Open(ChainablePathEffect):
    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices

        codes = [c if c != tpath.CLOSEPOLY else tpath.STOP for c in codes]

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
            pp = mtransforms.TransformedPath(
                self.patch.get_path(), self.patch.get_transform()
            )
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


class ClipRect(ChainablePathEffect):
    def __init__(self, ax, left=None, bottom=None, right=None, top=None,
                 coords="data"):
        super().__init__()
        self.ax = ax
        self.left= left
        self.bottom = bottom
        self.right = right
        self.top = top

        self.coords = coords

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
        gc0.copy_properties(gc)

        cliprect = gc0.get_clip_rectangle()

        left, bottom, right, top = cliprect.extents

        tr = TR.get_xy_transform(renderer, self.coords, axes=self.ax)

        left = left if self.left is None else tr.transform_point([self.left, 0])[0]
        right = right if self.right is None else tr.transform_point([self.right, 0])[0]

        bottom = bottom if self.bottom is None else tr.transform_point([0, self.bottom])[1]
        top = top if self.top is None else tr.transform_point([0, self.top])[1]

        cliprect0 = Bbox.from_extents(left, bottom, right, top)
        gc0.set_clip_rectangle(cliprect0)

        return renderer, gc0, tpath, affine, rgbFace


# original code from
# https://www.particleincell.com/wp-content/uploads/2012/06/bezier-spline.js

def _computeControlPoints(K):
    nn = len(K)
    n = nn - 1

    p1 = np.zeros(n)
    p2 = np.zeros(n)

    a = np.zeros(n)
    b = np.zeros(n)
    c = np.zeros(n)
    r = np.zeros(n)

    a[0] = 0
    b[0] = 2
    c[0] = 1
    r[0] = K[0] + 2*K[1]

    for i in range(1, n-1):
        a[i]=1
        b[i]=4
        c[i]=1
        r[i] = 4 * K[i] + 2 * K[i+1]

    a[n-1] = 2
    b[n-1] = 7
    c[n-1] = 0
    r[n-1] = 8*K[n-1] + K[n]

    # /*solves Ax=b with the Thomas algorithm (from Wikipedia)*/
    for i in range(1, n):
        m = a[i] / b[i-1]
        b[i] = b[i] - m * c[i-1]
        r[i] = r[i] - m * r[i-1]

    p1[n-1] = r[n-1]/b[n-1]

    for i in range(n-2, -1, -1):
        p1[i] = (r[i] - c[i] * p1[i+1]) / b[i]

    # /*we have p1, now compute p2*/
    for i in range(0, n-1):
        p2[i] = 2*K[i+1] - p1[i+1]

    p2[n-1] = 0.5*(K[n] + p1[n-1])

    return p1, p2


class Smooth(ChainablePathEffect):
    def __init__(self, skip_incompatible=False):
        super().__init__()
        self._skip_incompatible = skip_incompatible

    def _make_smooth_path(self, vertices, start_code=Path.MOVETO):
        n = len(vertices)

        x = vertices[:, 0]
        y = vertices[:, 1]
        xp1, xp2 = _computeControlPoints(x)
        yp1, yp2 = _computeControlPoints(y)

        xy = np.empty(shape=(n*3-2, 2), dtype=float)

        xy[::3] = vertices

        xy[1::3, 0] = xp1
        xy[2::3, 0] = xp2

        xy[1::3, 1] = yp1
        xy[2::3, 1] = yp2

        codes = np.empty(len(xy), dtype="uint8")
        codes.fill(Path.CURVE4)
        codes[0] = start_code

        return xy, codes

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices

        if codes is not None and (codes[0] != Path.MOVETO or
                                  np.any(codes[1:] != Path.LINETO)):
            if self._skip_incompatible:
                renderer = None

            return renderer, gc, tpath, affine, rgbFace

        xy, codes = self._make_smooth_path(vertices)
        new_tpath = Path(vertices=xy, codes=codes)

        return renderer, gc, new_tpath, affine, rgbFace


class SmoothClosed(Smooth):
    """
    This is for a closed path such as returned by fill_between
    """
    def __init__(self, skip_incompatible=False, skip_first_n=1):
        super().__init__(skip_incompatible=skip_incompatible)

        # somehow, the 1st point seems to be repeated and smoothing seems not
        # right unless the points is skipped.
        self._skip_first_n = skip_first_n

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices

        if codes is not None and (codes[0] != Path.MOVETO or
                                  np.any(codes[1:-1] != Path.LINETO) or
                                  codes[-1] != Path.CLOSEPOLY):
            if self._skip_incompatible:
                renderer = None

            return renderer, gc, tpath, affine, rgbFace

        n = len(vertices) // 2
        u = self._skip_first_n

        v1, c1 = self._make_smooth_path(vertices[u:n],
                                        start_code=Path.MOVETO)
        v2, c2 = self._make_smooth_path(vertices[n+u:2*n],
                                        start_code=Path.LINETO)

        vv = np.vstack([v1, v2, v1[:1]])
        cc = np.hstack([c1, c2, [Path.CLOSEPOLY]])

        new_tpath = Path(vertices=vv, codes=cc)

        return renderer, gc, new_tpath, affine, rgbFace
