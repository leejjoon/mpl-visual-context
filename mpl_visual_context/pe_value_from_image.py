import colorsys
import numpy as np
from matplotlib.transforms import Bbox, BboxTransform
from matplotlib.patheffects import AbstractPathEffect

from matplotlib.image import AxesImage
from .mpl_fix import image_get_window_extent


def get_image_value_at_xy(im, x, y, renderer=None):
    """
    Return the image value at the position or *None* if the position is
    outside the image.

    See Also
    --------
    matplotlib.artist.Artist.get_cursor_data
    """
    disp_extent = im.get_window_extent(renderer)
    # if im.origin == 'upper':
    #     ymin, ymax = ymax, ymin
    arr = im.get_array()
    # disp_extent = Bbox([[xmin, ymin], [xmax, ymax]])
    array_extent = Bbox([[0, 0], [arr.shape[1], arr.shape[0]]])
    trans = BboxTransform(boxin=disp_extent, boxout=array_extent)
    point = trans.transform([x, y])
    if any(np.isnan(point)):
        return None
    j, i = point.astype(int)
    # Clip the coordinates at array bounds
    if not (0 <= i < arr.shape[0]) or not (0 <= j < arr.shape[1]):
        return None
    else:
        return arr[i, j]


def get_image_value_at_bbox(im, bbox, renderer=None):
    """
    Return the image value at the center of the overwrappin bbox (intersection
    of image's extent and the given bbox) or *None* if the bbox is outside
    the image

    See Also
    --------
    matplotlib.artist.Artist.get_cursor_data
    """
    if isinstance(im, AxesImage):
        disp_extent = image_get_window_extent(im, renderer)
    else:
        disp_extent = im.get_window_extent(renderer)

    # print(disp_extent)
    bb = Bbox.intersection(disp_extent, bbox)
    if bb is None:
        return None

    x, y = 0.5 * (bb.x0 + bb.x1), 0.5 * (bb.y0 + bb.y1)

    # if im.origin == 'upper':
    #     ymin, ymax = ymax, ymin
    arr = im.get_array()
    # disp_extent = Bbox([[xmin, ymin], [xmax, ymax]])
    array_extent = Bbox([[0, 0], [arr.shape[1], arr.shape[0]]])
    trans = BboxTransform(boxin=disp_extent, boxout=array_extent)
    point = trans.transform([x, y])
    # print("point", point, x)
    if any(np.isnan(point)):
        return None
    j, i = point.astype(int)
    # Clip the coordinates at array bounds
    if not (0 <= i < arr.shape[0]) or not (0 <= j < arr.shape[1]):
        return None
    else:
        return arr[i, j]


class ValueFromImage(AbstractPathEffect):
    def __init__(self, im, drop_shadow=True):
        self.im = im
        self.drop_shadow = drop_shadow

    def _get_image_value(self, renderer, gc, tpath, affine, rgbFace):
        bb = tpath.get_extents()
        bb1 = bb.transformed(affine)

        v = get_image_value_at_bbox(self.im, bb1, renderer=renderer)
        return v

    def _get_color_for_value(self, v, foreground, rgbFace):
        if v is not None:
            r, g, b = self.im.to_rgba(v)[:3]
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            rgbFace = [1, 1, 1] if l < 0.5 else [0, 0, 0]
        else:
            rgbFace = [1.0, 0, 0]

        return foreground, rgbFace

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        alpha = self.im.get_alpha()
        alpha = 1.0 if alpha is None else alpha

        v = self._get_image_value(renderer, gc, tpath, affine, rgbFace)
        foreground0, rgbFace0 = self._get_color_for_value(v, gc.get_rgb(), rgbFace)

        if self.drop_shadow:
            rgb = self.im.to_rgba(v)
            gc0.set_foreground(rgb)
            gc0.set_alpha(0.3 * alpha)
            gc0.set_linewidth(5)
            renderer.draw_path(gc0, tpath, affine, rgbFace0)

            gc0.set_alpha(0.7 * alpha)
            gc0.set_linewidth(2.5)
            renderer.draw_path(gc0, tpath, affine, rgbFace0)

        renderer.draw_path(gc, tpath, affine, rgbFace0)
