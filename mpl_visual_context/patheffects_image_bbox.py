import matplotlib.transforms as mtransforms
from matplotlib.patheffects import AbstractPathEffect
from .image_box_effect import ColorBboxAlpha


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


