from abc import ABC, abstractmethod

import numpy as np
from scipy.optimize import fminbound

import matplotlib.transforms as mtransforms
from matplotlib.text import Annotation
from matplotlib.path import Path
from .bezier_lite import Curve
from .patheffects_base import ChainablePathEffect
from .transform_helper import TR
from .bezier_helper import mpl2bezier, beziers2mpl


class BezierFindYatX():
    # https://pomax.github.io/bezierinfo/#yforx

    # linear
    ab_coeff = np.array([[ -1, 1],
                         [  1, 0]], dtype=float)

    # quadratic
    abc_coeff = np.array([[ 1, -2, 1],
                          [-2,  2, 0],
                          [ 1,  0, 0]], dtype=float)

    # for cubic
    abcd_coeff = np.array([[-1,  3, -3, 1],
                           [ 3, -6,  3, 0],
                           [-3,  3,  0, 0],
                           [ 1,  0,  0, 0]], dtype=float)

    coeff_dict = {2: ab_coeff,
                  3: abc_coeff,
                  4: abcd_coeff}

    @classmethod
    def find(cls, node, x):
        """
        node : should be node values for a single coordinates. (4, ) for cubic.
        """
        coeff = cls.coeff_dict[node.shape[-1]]
        t_coeffs = np.dot(coeff, node)
        t_coeffs[-1] -= x

        t_roots = np.roots(t_coeffs)
        t_roots = t_roots[(t_roots.imag == 0)
                          & (0 < t_roots.real)
                          & (t_roots.real < 1)].real

        return t_roots

finder = BezierFindYatX()


def _maybe_test():  # convert this to test

    # We will find Y given X.

    # # for quadratic
    # ab_coeff = np.array([[2, -4, 2],
    #                       [2, -2, 0]], dtype=float)

    # for cubic bezier
    abcd_coeff = np.array([[-1,  3, -3, 1],
                           [ 3, -6,  3, 0],
                           [-3,  3,  0, 0],
                           [ 1,  0,  0, 0]], dtype=float)


    # px = bezier_extreme.get_extreme_points(curve.nodes[0])
    # py = bezier_extreme.get_extreme_points(curve.nodes[1])

    if False:
        x0 = -0.1
        nodes = curve.nodes
        t_coeffs = np.dot(abcd_coeff, nodes[0])
        t_coeffs[3] -= x0

        t_roots = np.roots(t_coeffs)
        t_roots = t_roots[(t_roots.imag == 0)
                          & (0 < t_roots.real)
                          & (t_roots.real < 1)].real

        t = t_roots[0]
        # xy = np.dot(abcd_coeff, [t**3, t**2, t, 1])
        xy = [curve.evaluate(t).reshape((-1,)) for t in t_roots]
        assert np.all([x for x, y in xy])

    nodes = np.asfortranarray([
        [0.0, -1.0, 1.0, -0.75 ],
        [2.0,  0.0, 1.0,  1.625],
    ])
    curve = bezier.Curve(nodes, degree=3)

    finder = BezierFindYatX()
    t_roots = finder.find(nodes[0], x=-0.1)
    xy = [curve.evaluate(t).reshape((-1,)) for t in t_roots]
    assert np.all([x for x, y in xy])


    nodes = np.asfortranarray([
        [0.0, -1.0, 1.0],
        [2.0,  0.0, 1.0],
    ])
    curve = bezier.Curve(nodes, degree=2)
    t_roots = finder.find(nodes[0], 0.4)
    xy = [curve.evaluate(t).reshape((-1,)) for t in t_roots]
    assert np.all([x for x, y in xy])

    nodes = np.asfortranarray([
        [0.0, -1.0],
        [2.0,  0.0],
    ])
    curve = bezier.Curve(nodes, degree=1)
    t_roots = finder.find(nodes[0], -0.5)
    xy = [curve.evaluate(t).reshape((-1,)) for t in t_roots]
    assert np.all([x for x, y in xy])


class Locator(ChainablePathEffect):
    def __init__(self, axes, xy,
                 pad=3, coords="data",
                 locate_only=False,
                 split_path=True):
        """
        axis : "x" for x-axis, "y" for y-axis.
        locate_only : do not find clipping points.
        """
        super().__init__()
        self._axes = axes

        x, y = xy
        if x is None and y is None:
            raise ValueError()
        elif y is None:
            self._mode = "findYatX"
            self._x = x
            self._x_or_y = 0
        elif x is None:
            self._mode = "findXatY"
            self._x = y
            self._x_or_y = 1
        else:
            self._mode = "nearXY"
            self._x = x
            self._y = y

        self._coords = coords

        self._pad = pad
        if split_path and locate_only:
            import warnings
            warnings.warn("spltt_path requires locate_only=False. Overriding locate_only to False.")
            locate_only = False
        self._locate_only = locate_only
        self._split_path = split_path

    def get_width(self, renderer):
        pad = renderer.points_to_pixels(self._pad)
        return 2 * pad

    def update_points_list(self, renderer, points_list):
        pass

    def locate_point(self, renderer, tp0):
        if self._mode.startswith("find"):
            return self.locate_point_at_x(renderer, tp0)

        else:
            return self.locate_point_near_xy(renderer, tp0)

    def locate_point_near_xy(self, renderer, tp0):
        tr = TR.get_xy_transform(renderer, self._coords, axes=self._axes)
        xy = tr.transform_point([self._x, self._y])

        bsl = mpl2bezier(tp0)
        dist_thresh = 1

        bsl_split_points = [] # index i and and parameter t for bezeir curve.
        for bs, closed in bsl: # for multiple paths, we iterate over each.
            starting_points = np.array([b.nodes[:, 0] for b in bs])
            # print("#", starting_points)

            dist = np.hypot(starting_points[:, 0] - xy[0],
                            starting_points[:, 1] - xy[1])
            i = np.argmin(dist)
            if dist[i] < dist_thresh:
                # print(i, dist[i])
                bsl_split_points.append((i, 0.))

        return bsl_split_points

    def locate_point_at_x(self, renderer, tp0):
        """
        tp0 : given the path in screen coordinate.
        we try to locate its intersecting point with x=x.
        """

        # locate the split points

        # x_or_y : 0 for x axis, 1 for y axis
        x, x_or_y = self._x, self._x_or_y

        tr = TR.get_xy_transform(renderer, self._coords, axes=self._axes)
        # assert tr.is_separable

        tp = tr.inverted().transform_path(tp0)

        bsl = mpl2bezier(tp)

        bsl_split_points = [] # index i and and parameter t for bezeir curve.
        for bs, closed in bsl: # for multiple paths, we iterate over each.
            # we assume x should be monotonically increasing. Just check if
            # x[-1] > x[0] and invert if necessary.
            # FIXME This part of the code is not tested.
            if bs[0].nodes[x_or_y][0] > bs[0].nodes[x_or_y][-1]:
                print("invert")
                bs = [Curve(b.nodes[:, ::-1], b.degree) for b in bs]

            xx = [b.nodes[x_or_y][-1] for b in bs]
            i = np.searchsorted(xx, x)
            if 0 < i < len(bs):
                t_ = finder.find(bs[i].nodes[x_or_y], x)  # we only
                                                                # return 1st t
                bsl_split_points.append((i, t_[0]))
            else:
                bsl_split_points.append((None, None))

        return bsl_split_points

    @staticmethod
    def split_path(bsl0, bsl_split_points, width, locate_only=True):
        """
        bsl0 : in the screen coordinate
        """

        bsl1 = []
        points_list = [] # coordinates of clipped path. Simply, left, center
                         # and right points are stored.

        for (bs, closed), (i, t) in zip(bsl0, bsl_split_points):
            if t is None:
                bsl1.append((bs, closed))
                continue

            # FIXME if closed is True, we need to check if the split point is
            # at the edge and try to wrap the path around.
            x0, y0 = bs[i].evaluate(t).reshape((-1, ))
            points = np.array([[np.nan, np.nan],
                               [x0, y0],
                               [np.nan, np.nan]])
            points_list.append(points)

            if locate_only:
                bsl1.append((bs, closed))
                continue

            def f(i):
                x, y = bs[i].nodes[:, 0]
                r = np.hypot(x-x0, y-y0) - width
                return r

            # get the reasonable left/right boundary. We do this not to stuck
            # on the local minimum.
            i_left = i
            while i_left >= 0 and f(i_left) < 0:
                i_left -= (i - i_left) + 1
            i_left = max(i_left, 0)

            N = len(bs)
            i_right = i + 1
            while i_right < N  and f(i_right) < 0:
                i_right += (i_right - i)
            i_right = min(i_right, N)

            # print(i, i_left, i_right)
            def f_abs(xt):
                i, t = divmod(xt, 1)
                x, y = bs[int(i)].evaluate(t).reshape((-1,))
                # print(x, y)
                r = np.abs(np.hypot(x-x0, y-y0) - width)
                return r

            xt_left = fminbound(f_abs, i_left, i+t)
            # print("#", i, t, xt_left, f_abs(xt_left))
            if f_abs(xt_left) > 1:
                xt_left = 0
            xt_right = fminbound(f_abs, i+t, i_right)
            if f_abs(xt_right) > 1:
                xt_right = N

            if xt_left > 0:
                i_, t = divmod(xt_left, 1)
                i = int(i_)
                bs_left = bs[:i] + [bs[i].specialize(0, t)]
                x, y = bs[i].evaluate(t).reshape((-1,))
                points[0] = [x, y]
            else:
                bs_left = []
            # if t:
            #     bs_left.append(bs[i].specialize(0, t))

            if xt_right < N:
                i_, t = divmod(xt_right, 1)
                i = int(i_)
                bs_right=  [bs[i].specialize(t, 1)] + bs[i+1:]
                x, y = bs[i].evaluate(t).reshape((-1,))
                points[2] = [x, y]
            else:
                bs_right = []

            bsl1.extend([(bs_left, False), (bs_right, False)])

        return bsl1, points_list

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):

        # locate the split points

        # We find the splitting point in the self._coords coordinate.
        # So, we transform the path to the input coord.
        tp0 = affine.transform_path(tpath)

        bsl_split_points = self.locate_point(renderer, tp0)

        # find the clip points in the pixel coordinate.
        bsl0 = mpl2bezier(tp0)

        # print(i, x0, y0)
        width = self.get_width(renderer) * 0.5

        # we now try to split the path with the given width. As a result this
        # will get new path and the splitting points; a list of 3x2 array for
        # the coordinate of the center and two edges. This can be used to
        # measure the angle and the curvature.
        bsl1, points_list = self.split_path(bsl0, bsl_split_points, width,
                                            locate_only=self._locate_only)

        # do something with the points_list
        self.update_points_list(renderer, points_list)

        # the original path is split only if _split_path is True. The split
        # path in the screen coordinate for now. We can easily revert it back
        # to the origin coordinate. Not sure if that is worth it.
        if self._split_path:
            tppl = [beziers2mpl(bs, closed) for bs, closed in bsl1 if bs]
            # we skip the last stop segment.
            if tppl:
                tpath = Path(vertices=np.vstack([tpp.vertices[:-1] for tpp in tppl]),
                             codes=np.concatenate([tpp.codes[:-1] for tpp in tppl]))
                affine = mtransforms.IdentityTransform()

        # print(points_list)
        return renderer, gc, tpath, affine, rgbFace


class LocatorForIXYARBase(ABC, Locator):
    def __init__(self, axes, xy, pad=3, coords="data",
                 do_rotate=True, do_curve=False, **kwargs):
        super().__init__(axes, xy, pad=pad, coords=coords, **kwargs)
        self._do_rotate = do_rotate
        self._do_curve = do_curve

    @abstractmethod
    def set_ixyar(self, i, xy, angle, R, renderer):
        ...

    def update_points_list(self, renderer, points_list):
        if not points_list:
            # no intersecting points are found.
            # make it invisible
            self.set_ixyar(-1, [0, 0], 0, 0, renderer)
            return

        for i, points in enumerate(points_list):

            inverted = False
            if self._do_rotate:
                if np.all(np.isfinite(points[0])):
                    left = points[0]
                else:
                    left = points[1]
                if np.all(np.isfinite(points[2])):
                    right = points[2]
                else:
                    right = points[1]
                dx = right[0] - left[0]
                dy = right[1] - left[1]
                if dx < 0:
                    inverted = True
                    dx = -dx
                    dy = -dy
                angle = np.rad2deg(np.arctan2(dy, dx))
            else:
                angle = None

            R = np.nan
            if self._do_curve:
                # we get the radius of curvature
                x, y, z = points[:, 0] + points[:, 1]*1j # 0+1j, 1+0j, 0-1j
                w = z-x
                w /= y-x
                if w.imag:
                    c = (x-y)*(w-abs(w)**2)/2j/w.imag-x
                    R_ = np.abs(c+x)
                    if np.abs(R_) < 1.e3:
                        R = -np.sign(w.imag)*R_
                        if inverted:
                            R = -R

            self.set_ixyar(i, points[1], angle, R, renderer)


class LocatorForIXYAR(LocatorForIXYARBase):
    def __init__(self, cb_ixyar, axes, xy, pad=3, coords="data",
                 do_rotate=False, do_curve=False, **kwargs):
        super().__init__(axes, xy, pad=pad, coords=coords,
                         do_rotate=do_rotate, do_curve=do_curve,
                         **kwargs)
        self._cb_ixyar = cb_ixyar

    def set_ixyar(self, i, xy, angle, R, renderer):
        self._cb_ixyar(i, xy, angle, R, renderer)


class LocatorForAnn(LocatorForIXYARBase):
    def __init__(self, ann, axes, xy, pad=3, coords="data",
                 do_rotate=True, do_curve=False,
                 invisible_if_no_intersection=True,
                 **kwargs):
        super().__init__(axes, xy, pad=pad, coords=coords,
                         do_rotate=do_rotate, do_curve=do_curve,
                         **kwargs)
        self.ann = ann
        self.invisible_if_no_intersection = invisible_if_no_intersection

        self._pe_list = []

    def get_width(self, renderer):
        angle = self.ann.get_rotation()
        self.ann.set_rotation(0)
        pad2 = super().get_width(renderer)
        width = self.ann.get_window_extent(renderer).width + pad2
        self.ann.set_rotation(angle)
        return width

    def set_ixyar(self, i, xy, angle, R, renderer=None):
        if i < 0:
            if self.invisible_if_no_intersection:
                self.ann.set_visible(False)
            return

        self.ann.set_visible(True)

        if isinstance(self.ann, Annotation):
            tr = self.ann._get_xy_transform(renderer, self.ann.xycoords)
            xy = tr.inverted().transform_point(xy)

            self.ann.xy = xy
        else:
            xy = self.ann.get_transform().inverted().transform_point(xy)

            self.ann.set_position(xy)

        if angle is not None:
            self.ann.set_rotation(angle)
        else:
            self.ann.set_rotation(0)

        for pe in self._pe_list:
            pe.R = R

    def new_curved_patheffect(self, smooth_line=False, n_split=4):
        from mpl_visual_context.patheffects_path import TextAlongArc
        pe = TextAlongArc(0,
                          smooth_line=smooth_line,
                          n_split=n_split)
        self._pe_list.append(pe)
        return pe
