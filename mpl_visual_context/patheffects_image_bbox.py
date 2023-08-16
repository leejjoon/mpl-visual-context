import numpy as np
import matplotlib.transforms as mtransforms
from matplotlib.patheffects import AbstractPathEffect
from matplotlib.transforms import BboxTransformTo, Bbox, TransformedPath
from .image_box_effect import ColorBboxAlpha

from scipy.interpolate import interp1d


class BboxAlphaPathEffect(AbstractPathEffect):
    "BboxAlpha with color from rgbFace"
    def __init__(self, alpha,
                 extent=None, bbox=None, coords="data", axes=None,
                 **im_kw):
        self._image_bbox = ColorBboxAlpha(None, alpha,
                                          extent=extent,
                                          bbox=bbox, coords=coords,
                                          axes=axes,
                                          **im_kw)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        rect = gc.get_clip_rectangle()
        self._image_bbox.set_clip_box(rect)
        pp = mtransforms.TransformedPath(tpath, affine)
        self._image_bbox.set_clip_path(pp)
        self._image_bbox.set_color(rgbFace)
        self._image_bbox.draw(renderer)


class _GradBase():
    RESHAPE_TARGET = None

    def __init__(self, x_or_v, v=None):
        if v is None:
            self.v = x_or_v
            self.x = np.linspace(0, 1, len(self.v))
        else:
            self.x = x_or_v
            self.v = v

    def get_2d(self):
        x = np.linspace(0, 1, 256)
        alphas = interp1d(self.x, self.v)(x)

        return alphas.reshape(self.RESHAPE_TARGET)


class GradH(_GradBase):
    RESHAPE_TARGET = (1, -1)


class GradV(_GradBase):
    RESHAPE_TARGET = (-1, 1)


def _gradient_from_string(s):
    if ">" in s:
        alphas = [float(v) for v in s.split(">")]
        return GradH(alphas)
    elif "^" in s:
        alphas = [float(v) for v in s.split("^")]
        return GradV(alphas)
    else:
        raise ValueError()


class AlphaGradient(AbstractPathEffect):

    def __init__(self, alphas, extent=None, bbox=None,
                 coords="data", axes=None,
                 **im_kw):

        self.extent = [0, 0, 1, 1] if extent is None else extent

        if isinstance(alphas, str):
            alphas = _gradient_from_string(alphas)

        if hasattr(alphas, "get_2d"):
            alphas = alphas.get_2d()

        if len(alphas.shape) != 2:
            raise ValueError()

        self._image_bbox = ColorBboxAlpha(None, alphas,
                                          bbox=bbox, coords=coords,
                                          axes=axes,
                                          **im_kw)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        def get_extent(renderer):
            bbox_out = tpath.get_extents()
            tr = BboxTransformTo(bbox_out)
            bbox = tr.transform_bbox(Bbox.from_extents(self.extent))
            return bbox

        self._image_bbox.set_coords(affine)
        self._image_bbox.set_bbox(get_extent)

        rect = gc.get_clip_rectangle()
        self._image_bbox.set_clip_box(rect)
        pp = TransformedPath(tpath, affine)
        self._image_bbox.set_clip_path(pp)
        self._image_bbox.set_color(rgbFace)
        self._image_bbox.draw(renderer)
