import warnings
from itertools import cycle, chain
import numpy as np
try:
    import bezier
except ImportError:
    warnings.warn("bezier module not fount. Using bezier-lite.")
    from . import bezier_lite as bezier

from matplotlib.path import Path as MPath


def mpl2bezier(mpl_path, transform=None):
    # if transform is not None:
    #     mpl_path = transform.transform_path(mpl_path)

    # ci = iter(mpl_path.codes)
    # vi = iter(mpl_path.vertices)

    beziers = []
    bezier_current = []
    # nodes = []
    last_node = None

    # for c in ci:
    for vv, c in mpl_path.iter_segments(transform=transform,
                                        simplify=False, snap=False,
                                        curves=True):
        # vv = vv_.reshape((-1, 2))
        if c == MPath.MOVETO:
            if len(bezier_current):
                beziers.append((bezier_current, False)) # set close_poly = False
                bezier_current = []
            # nodes = [next(vi)]
            last_node = vv
            continue
        elif c == MPath.LINETO:
            degree = 1
            # verts = nodes + [next(vi)]
            verts_ = np.concatenate([last_node, vv])
        elif c == MPath.CURVE3:
            degree = 2
            verts_ = np.concatenate([last_node, vv])
            # verts = nodes + [next(vi), next(vi)]
            # next(ci)
        elif c == MPath.CURVE4:
            degree = 3
            verts_ = np.concatenate([last_node, vv])
            # verts = nodes + [next(vi), next(vi), next(vi)]
            # next(ci)
            # next(ci)
        elif c == MPath.CLOSEPOLY:
            # verts = nodes + [bezier_current[0].nodes[:, 0]]
            verts_ = np.concatenate([last_node, bezier_current[0].nodes[:, 0]])
            # skip if last node is already equal to the first node.
            verts = verts_.reshape((-1, 2))
            if np.any(verts[0] - verts[-1]):
                p = bezier.Curve(np.array(verts).T, degree=1)
                bezier_current.append(p)
            beziers.append((bezier_current, True)) # set close_poly = True
            bezier_current = []
            # nodes = []
            last_node = None
            # next(vi)
            continue
        elif c == MPath.STOP:
            beziers.append((bezier_current, False)) # set close_poly = False
            bezier_current = []
            last_node = None
            # nodes = []
            # next(vi)
            continue
        else:
            raise ValueError()

        p = bezier.Curve(np.array(verts_.reshape((-1, 2))).T, degree=degree)
        bezier_current.append(p)
        last_node = p.nodes[:, -1]
        # nodes = [p.nodes[:, -1]]

    if bezier_current:
        beziers.append((bezier_current, False)) # set close_poly = False

    return beziers
    # if beziers[-1]:
    # else:
    #     return beziers[:-1]

def bezier2mpl(curve, no_start_node=True):
    if curve.degree == 3:
        codes = [MPath.CURVE4] * 3
        verts = curve.nodes
    elif curve.degree == 2:
        codes = [MPath.CURVE3] * 2
        verts = curve.nodes
    elif curve.degree == 1:
        codes = [MPath.LINETO]
        verts = curve.nodes
    else:
        raise ValueError()

    if no_start_node:
        return verts[:, 1:], codes
    else:
        return verts, [MPath.MOVETO] + codes

def beziers2mpl(bezier_list, close=True):
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
    if close:
        codes.append([MPath.CLOSEPOLY])
    else:
        codes.append([MPath.STOP])

    p = MPath(np.hstack(vertices).T, codes=np.hstack(codes))

    return p


def get_inverted_path(p,
                      close_poly=True):
    # M, C3, L = Path.MOVETO, Path.CURVE3, Path.LINETO

    bezier_list = list((b, k) for b, k in p.iter_bezier() if k > 1)

    vertices = [bezier_list[-1][0].control_points[-1]]
    codes = [MPath.MOVETO]

    for seg, k in reversed(bezier_list):
        if k == 1: continue
        vertices.extend(seg.control_points[-2::-1])
        codes.extend([{2: MPath.LINETO,
                       3: MPath.CURVE3,
                       4: MPath.CURVE4}[k]] * seg.degree)

    if close_poly:
        vertices.append(bezier_list[0][0].control_points[0])
        codes.append(MPath.CLOSEPOLY)

    return MPath(vertices, codes=codes)
