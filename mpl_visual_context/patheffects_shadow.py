import numpy as np

from itertools import cycle, chain
from matplotlib.transforms import Affine2D, IdentityTransform
from matplotlib.path import Path
from matplotlib.text import TextPath
from matplotlib.patches import PathPatch
from .bezier_helper import bezier, mpl2bezier, bezier2mpl
from .patheffects_base import ChainablePathEffect

# see https://pomax.github.io/bezierinfo/#extremities
class BezierExtreme():

    # for quadratic
    ab_coeff = np.array([[2, -4, 2],
                          [2, -2, 0]], dtype=float)

    # for cubic bezier
    abc_coeff = np.array([[-3, 9, -9, 3],
                          [6, -12, 6, 0],
                          [-3, 3, 0, 0]], dtype=float)

    @staticmethod
    def _get_extreme_points2(a, b):
        if a == 0:
            candidates = []
        else:
            candidates = [b/a]

        return [p for p in candidates if 0 < p < 1]

    @classmethod
    def get_extreme_points2(cls, nodes):
        ab = np.dot(cls.ab_coeff, nodes)
        return cls._get_extreme_points2(*ab)

    @staticmethod
    def _get_extreme_points_cubic(a, b, c):
        b2_4ac = b*b - 4*a*c
        if b2_4ac == 0.:
            candidates = [-0.5 * b / a]
        elif b2_4ac > 0:
            candidates = [-0.5 * (b - b2_4ac**.5) / a,  -0.5 * (b + b2_4ac**.5) / a]
        else:
            return []

        return [p for p in candidates if 0 < p < 1]

    @classmethod
    def get_extreme_points_cubic(cls, nodes):
        abc = np.dot(cls.abc_coeff, nodes)
        return cls._get_extreme_points_cubic(*abc)

    @classmethod
    def get_extreme_points(cls, nodes):
        if len(nodes) == 4:
            return cls.get_extreme_points_cubic(nodes)
        elif len(nodes) == 3:
            return cls.get_extreme_points2(nodes)
        else:
            raise ValueError()

bezier_extreme = BezierExtreme()

if False:

    nodes = np.asfortranarray([
        [0.0, -1.0, 1.0, -0.75 ],
        [2.0,  0.0, 1.0,  1.625],
    ])
    curve = bezier.Curve(nodes, degree=3)

    px = bezier_extreme.get_extreme_points(curve.nodes[0])
    py = bezier_extreme.get_extreme_points(curve.nodes[1])

    curve.plot(128)
    ax = plt.gca()
    for p in [px, py]:
        xy = np.array([curve.evaluate(p1)[:, 0] for p1 in p])
        for xy1 in xy:
            x, y = xy1
            ax.plot([x], [y], "o")


if False:

    nodes = np.asfortranarray([
        [0.0, -1.0, 1.0],
        [2.0,  0.0, 1.0],
    ])
    curve = bezier.Curve(nodes, degree=2)

    px = bezier_extreme.get_extreme_points(nodes[0])
    py = bezier_extreme.get_extreme_points(nodes[1])

    curve.plot(128)
    ax = plt.gca()
    for p in [px, py]:
        xy = np.array([curve.evaluate(p1)[:, 0] for p1 in p])
        for xy1 in xy:
            x, y = xy1
            ax.plot([x], [y], "o")


def convert_piecewise_monotonic(bp):
    """ given a list of bezier paths, returns a list of list of paths, each
    item is monotonically increase/decrease in y-direction"""
    bpp = []
    for b in bp:
        by = b.nodes[1]
        if b.degree == 1:
            bpp.append(b)
        elif b.degree in [2, 3]:
            extremes = bezier_extreme.get_extreme_points(by)
            # print(by, extremes)
            if extremes:
                bpp.extend([b.specialize(e1, e2) for (e1, e2)
                            in zip([0] + extremes, extremes + [1])])
            else:
                bpp.append(b)

    yy = np.array([bpp[0].nodes[1][0]] + [b.nodes[1][-1] for b in bpp])
    ss = np.sign(yy[1:] - yy[:-1])
    ds = ss[1:] - ss[:-1]
    splits = np.split(bpp, np.nonzero(ds)[0]+1)

    return splits


def create_shadow_bezier_lists(splits, ox, oy):
    """
    splits : list of list of bezier paths.
    """
    shadows = []
    oxy = np.array([ox, oy])[:, np.newaxis]
    from_nodes = bezier.Curve.from_nodes
    for s in splits:
        # we make all the shadows are drawn in the same direction, so that they
        # can be unioned without holes.
        if s[0].nodes[1, 0] < s[-1].nodes[1, -1]:
            s_offset = [bezier.Curve.from_nodes(si.nodes[:, ::-1] + oxy)
                          for si in s[::-1]]
        else:
            s_offset = [bezier.Curve.from_nodes(si.nodes + oxy)
                          for si in s]
            s = [bezier.Curve.from_nodes(si.nodes[:, ::-1])
                 for si in s[::-1]]

        conn1 = from_nodes(np.hstack((s[-1].nodes[:, -1:],
                                      s_offset[0].nodes[:, :1])))
        conn2 = from_nodes(np.hstack((s_offset[-1].nodes[:, -1:],
                                      s[0].nodes[:, :1])))
        combined = list(s) + [conn1] + s_offset + [conn2]

        shadows.append(combined)

    return shadows

# bezier_list = shadows[2]

def beziers2mpl(bezier_list):
    """convert a list of bezier curves (supposed to be connected and closed)
    to MPL path.
    """
    vertices, codes = [], []
    for p, no_start_node in zip(bezier_list,
                                chain([False], cycle([True]))):
        _v, _c = bezier2mpl(p, no_start_node=no_start_node)
        vertices.append(_v)
        codes.append(_c)
    vertices.append(vertices[0][:, :1])
    codes.append([Path.CLOSEPOLY])
    p = Path(np.hstack(vertices).T, codes=np.hstack(codes))

    return p


class ShadowPath(ChainablePathEffect):
    def __init__(self, angle, distance,
                 post_affine=True):
        """
        angle : clockwise from the right in degree.
        post_affine : If True, thr shadow path is obtained after affine is applied. The distance is in dpi
        """
        self.angle =angle
        self.distance = distance
        self.post_affine = post_affine

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        if self.post_affine:
            tp0 = tpath.transformed(affine)
            tr0 = IdentityTransform()
            dpi_cor = renderer.points_to_pixels(1)
        else:
            tp0 = tpath
            tr0 = affine
            dpi_cor = 1

        tr = Affine2D().rotate_deg(self.angle)
        tri = tr.inverted()

        tp = tr.transform_path(tp0)
        bp_list = mpl2bezier(tp)

        ox, oy = self.distance*dpi_cor, 0

        mps = []
        for bp, closed in bp_list:
            splits = convert_piecewise_monotonic(bp)

            shadows = create_shadow_bezier_lists(splits, ox, oy)

            for shadow in shadows:
                p = beziers2mpl(shadow)
                mps.append(p)

        vertices = np.vstack([p.vertices for p in mps])
        codes = np.concatenate([p.codes for p in mps])
        path0 = Path(vertices, codes=codes)
        path = tri.transform_path(path0)

        return renderer, gc, path, tr0, rgbFace


if False:
    tp0 = TextPath((0, 0), "Matplotlib", size=30)
    tr = Affine2D().rotate_deg(30)
    tri = tr.inverted()
    tp = tr.transform_path(tp0)
    bp_list = mpl2bezier(tp)
    ox, oy = 2, 0

    mps = []
    for bp in bp_list:
        # bp = bp_list[1]
        splits = convert_piecewise_monotonic(bp)

        shadows = create_shadow_bezier_lists(splits, ox, oy)

        for shadow in shadows:
            p0 = beziers2mpl(shadow)
            p = tri.transform_path(p0)
            mps.append(p)

    if True:
        red = np.array([233, 77, 85, 255]) / 255

        I = np.zeros((200, 1, 4)) + red
        I[:, 0, 3] = np.linspace(0, 1, len(I))
        im = ax.imshow(I, extent=[-2, 160, -10, 80], aspect="auto")
        vertices = np.vstack([p.vertices for p in mps])
        codes = np.concatenate([p.codes for p in mps])
        path = Path(vertices, codes=codes)
        im.set_clip_path(path, transform=ax.transData)
        mp = PathPatch(path, fc="0.5", ec="0.5")
        # ax.add_patch(mp)
        # mp = PathPatch(p, fc="0.5", ec="0.5")
        # ax.add_patch(mp)

        ax.add_patch(PathPatch(tp0, fc="w", linewidth=0))
        ax.set_xlim(-2, 160)
        ax.set_ylim(-10, 80)

