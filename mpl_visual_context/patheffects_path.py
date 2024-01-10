"""
Defines classes for path effects that modifies the path and/or fill behavior.
"""
import numpy as np
from matplotlib.path import Path
import matplotlib.transforms as mtransforms
from matplotlib.transforms import Bbox
from matplotlib.transforms import Affine2D, IdentityTransform
import matplotlib.colors as mcolors
from .patheffects_base import ChainablePathEffect, AbstractPathEffect
from .image_box import TR
from .bezier_helper import get_inverted_path


class StrokeOnly(ChainablePathEffect):
    """
    PathEffect with only stroke. This is done by setting the fill color
    to None.
    """
    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

        return renderer, gc, tpath, affine, None


class FillOnly(ChainablePathEffect):
    """
    PathEffect with only fill. This is done by setting the linewidth to 0.
    """
    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)
        gc0.set_linewidth(0)

        return renderer, gc0, tpath, affine, rgbFace


class Partial(ChainablePathEffect):
    """
    PathEffect with that preserve only a part of the path. It only support
    lines (no bezier splines).
    """
    def __init__(self, start, stop):
        """
        start, stop : index (if int) or fraction (if float)
       """
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
        codes = codes[start:stop].copy()
        codes[0] = tpath.MOVETO

        new_tpath = Path._fast_from_codes_and_verts(vertices, codes)

        return renderer, gc, new_tpath, affine, rgbFace


class Open(ChainablePathEffect):
    """
    PathEffect with no closed with. This is done by replacin CLOSEPOLY
    code to STOP.
    """

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        codes, vertices = tpath.codes, tpath.vertices

        codes = [c if c != tpath.CLOSEPOLY else tpath.STOP for c in codes]

        new_tpath = Path._fast_from_codes_and_verts(vertices, codes)

        return renderer, gc, new_tpath, affine, rgbFace


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
    """
    PathEffect that transform the given lines to smooth bezier path.
    If the path is not line (not closed), the path is not changed.
    """
    def __init__(self, skip_incompatible=False):
        """
        skip_incompatible : do not draw the path if incompatible. Default if False (the path is drawn as is)
        """
        super().__init__()
        self._skip_incompatible = skip_incompatible

    @staticmethod
    def _make_smooth_path(vertices, start_code=Path.MOVETO):
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


class SmoothFillBetween(Smooth):
    """
    PathEffect that transform a patch created by fill_between to a
    smooth nezier path. It assumes that the patch is consist of two lines
    (one for upper/left boundary another for lower/right boundary), which
    are smoothed separately then combined.
    """
    def __init__(self, skip_incompatible=False, skip_first_n=0):
        """
        skip_incompatible : do not draw the path if incompatible. Default if False (the path is drawn as is)
        skip_first_n : ignore fist n points in the path (for each upper and lower bounday).
        """
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


def _get_rounded(v0, v1, v2, dl):
    x0, y0 = v0
    x1, y1 = v1
    x2, y2 = v2

    dx10 = x0 - x1
    dy10 = y0 - y1
    dx12 = x2 - x1
    dy12 = y2 - y1
    l10 = np.hypot(dx10, dy10)
    l12 = np.hypot(dx12, dy12)

    if l10 == 0 or l12 == 0: # some paths have repeating points. We just skip those.
        return None

    if l10 < 2*dl:
        dl10 = l10*0.5
    else:
        dl10 = dl

    if l12 < 2*dl:
        dl12 = l12*0.5
    else:
        dl12 = dl

    x10 = x1 + dx10 * dl10 / l10
    y10 = y1 + dy10 * dl10 / l10

    x12 = x1 + dx12 * dl12 / l12
    y12 = y1 + dy12 * dl12 / l12

    return [[x10, y10], [x1, y1], [x12, y12]]


class RoundCorner(ChainablePathEffect):
    def __init__(self, round_size=20, i_selector=None):
        super().__init__()
        self.round_size = round_size
        if i_selector is None:
            self.i_selector = lambda i: True
        else:
            self.i_selector = i_selector

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        tp = affine.transform_path(tpath)
        codes, vertices = tp.codes, tp.vertices
        if codes is None:
            codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices)-1)

        select_i = self.i_selector

        dl = renderer.points_to_pixels(self.round_size)

        # FIXME this only works if the path is not broken (CLOSEPOLY|STOP only
        # at the end). We should refactor the code so that the path is split,
        # rounded, and merged.
        c0, v0 = codes[0], vertices[0]
        v_start = [v0[0], v0[1]] # we may replace its values later
        cc, vv = [c0], [v_start]
        for i in range(1, len(codes)-1):
            c0, c1, c2 = codes[i-1:i+2]
            v0, v1, v2 = vertices[i-1:i+2]
            if not (c0 in [Path.MOVETO, Path.LINETO] and
                    c1 == Path.LINETO and
                    c2 in [Path.LINETO, Path.CLOSEPOLY, Path.STOP]):
                cc.append(c1)
                vv.append(v1)

                if c1 == Path.MOVETO: # to support broken path
                    v_start = [v1[0], v1[1]]
                continue

            if select_i(i) and (ww := _get_rounded(v0, v1, v2, dl)):

                vv.extend(ww)
                cc.extend([Path.LINETO, Path.CURVE3, Path.CURVE3])
                # curveto : x0, x1, x2
            else:
                cc.append(c1)
                vv.append(v1)

        n = len(codes)
        c0, c1 = codes[-2:]
        v0, v1 = vertices[-2:]
        if (c1 == Path.CLOSEPOLY and select_i(n-11)):
            ww = _get_rounded(v0, v1, vertices[1], dl)
            vv.extend(ww)
            cc.extend([Path.LINETO, Path.CURVE3, Path.CURVE3])
            v_start[:] = ww[2]

        cc.append(c1)
        vv.append(v1)

        new_tpath = affine.inverted().transform_path(Path(vertices=vv, codes=cc))
        return renderer, gc, new_tpath, affine, rgbFace


class ClipPathFromPatch(ChainablePathEffect):
    """
    PathEffect that clips the path using a provided patch.
    """
    def __init__(self, patch):
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
    """
    PathEffect that sets the clip_path to the path itself. This is useful when
    the path is modified down in the pipeline.
    """
    def __init__(self):
        super().__init__()

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
        gc0.copy_properties(gc)
        pp = mtransforms.TransformedPath(tpath, affine)
        gc0.set_clip_path(pp)

        return renderer, gc0, tpath, affine, rgbFace


class ClipRect(ChainablePathEffect):
    """
    PathEffect that modifies the clip_rect using the given coordinate
    (and transform). In most case, the default clip_rect is the bbox of
    the axes.
    """
    def __init__(self, ax, left=None, bottom=None, right=None, top=None,
                 coords="data"):
        """
        ax : axes instance that will be used to get the data coordinate and etc.
        left, bottom, right, top: values in the given coordinate. Not changed if None.
        coord : coordinate system. Coule be 'data', 'axes fraction', etc. Check the annotate function in Matplotlib.
        """
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


class TextAlongArc(ChainablePathEffect):
    def __init__(
            self, R, smooth_line=False, n_split=2
    ):
        """
        smooth_line : try to 
        """
        self._smooth_line = smooth_line
        self.R = R
        self.n_split = n_split

    @staticmethod
    def _transform_vertices(v, R, affine):
        xmin, ymin = np.min(v, axis=0)
        xmax, ymax = np.max(v, axis=0)
        xc = 0.5*(xmin + xmax)
        yc = 0.5*(ymin + ymax)
        w, h = xmax - xmin, ymax - ymin

        v1 = v - [xc, yc]
        dx, dy = v1.T

        # Since the path will be modified before affine, we scale the R with
        # the length of h in the transformed space.
        xc0, yc0 = affine.transform_point([xc, yc])
        xc1, yc1 = affine.transform_point([xc+w, yc])
        xc2, yc2 = affine.transform_point([xc, yc+h])
        w_, h_ = np.hypot([xc1-xc0, xc2-xc0], [yc1-yc0, yc2-yc0])

        if R is None:
            # We assume that the tpath + affine is modified such that R is a
            # distance to zero point from xc, yc.
            R0 = np.hypot(xc0, yc0)
            # R0, R1 = np.hypot([xc0, xc1], [yc0, yc1])
            # aspect = (w_ / w / h_ * h)
            # aspect = 2
            # print(aspect)
            R = R0 / h_ * h
        else:
            R = R / h_ * h

        theta = dx / R
        xn = xc + (R+dy)*np.sin(theta)
        yn = yc + (R+dy)*np.cos(theta) - R

        v = np.array([xn, yn]).T

        return v

    @classmethod
    def make_curved(cls, tpath, R, affine, smooth_line=False, n_split=2):
        # We will split a single staraigh line in to multiple line segments.
        # Later, we will convert this to a smoothe line.
        ns = n_split * 3  # Since a line segment will be converted to a
                               # cubic bezier, we make enough room for it.
        if smooth_line:
            indices_to_smooth = []  # list of indices where a line is converted
                                    # to curve.
            last_node = None
            v, c = [], []
            for v1, c1 in tpath.iter_segments(simplify=False):
                if c1 == Path.LINETO:
                    vx = np.linspace(last_node[0], v1[0], ns+1)[1:]
                    vy = np.linspace(last_node[1], v1[1], ns+1)[1:]
                    v_ = np.array([vx, vy]).T
                    v.append(v_)
                    indices_to_smooth.append(len(c))
                    # Note that the codes is populated assuming that the
                    # straight line will be converted to smooth cubic bezier
                    # curve.
                    c.extend([Path.CURVE4]*ns)
                else:
                    v_ = v1.reshape((-1, 2))
                    v.append(v_)
                    c.extend([c1] * len(v_))

                last_node = v1[-2:]

            v = np.vstack(v)
            codes = np.array(c)

            v = cls._transform_vertices(v, R, affine)

            for i in indices_to_smooth:
                v1 = v[i-1:i+ns:3]
                v2, _ = Smooth._make_smooth_path(v1)
                v[i-1:i+ns] = v2

            path = Path(v, codes=codes)

        else:
            v = cls._transform_vertices(tpath.vertices, R, affine)
            path = Path(v, codes=tpath.codes)

        return path

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

        if self.R is None or (self.R and np.isfinite(self.R)):
            tpath = self.make_curved(tpath, self.R, affine,
                                     smooth_line=self._smooth_line,
                                     n_split=self.n_split)

        return renderer, gc, tpath, affine, rgbFace


class ClosedPathSelector(ChainablePathEffect):
    def __init__(self, selector):
        self._selector = selector

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        idx = np.where(tpath.codes == Path.CLOSEPOLY)
        code_splits = np.split(tpath.codes, idx[0]+1)
        vert_splits = np.split(tpath.vertices, idx[0]+1)

        tp = Path(vertices=vert_splits[self._selector],
                  codes=code_splits[self._selector])

        return renderer, gc, tp, affine, rgbFace
