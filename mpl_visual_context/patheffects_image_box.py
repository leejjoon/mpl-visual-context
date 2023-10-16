import numpy as np
from scipy.interpolate import interp1d

import matplotlib.transforms as mtransforms
from matplotlib.patheffects import AbstractPathEffect
from matplotlib.transforms import BboxTransformTo, Bbox, TransformedPath
from .image_box import ImageBox, ColorBoxLazy
from .image_box import get_gradient_array_from_str


class FillImage(AbstractPathEffect):
    """
    Fill the path with the given image. It actually draws the image with its
    clip_path set to the path itself.
    """
    def __init__(self, im, ax=None, remove_from_axes=False, alpha=None,
                 **kwargs):
        """

        Keyword Arguments:
        clip_box
        """
        if im.axes is None and ax is None:
            raise ValueError("im.axes should not be None")

        ax = ax if ax is not None else im.axes

        if remove_from_axes:
            im.remove()

        im.axes = ax

        if "clip_box" in kwargs:
            clipbox = kwargs.pop("clip_box")
            im.set_clip_box(clipbox)

        if kwargs:
            raise ValueError(
                "Unknown keyword argument {}".format(", ".join(kwargs.keys()))
            )

        self.im = im
        self._alpha = alpha

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        self.im.set_clip_path(tpath, transform=affine)
        alpha_old = self.im.get_alpha()
        if alpha_old is not None:
            self.im.set_alpha(alpha_old * (1 if self._alpha is None else self._alpha))
        else:
            self.im.set_alpha(self._alpha)

        self.im.draw(renderer)
        self.im.set_alpha(alpha_old)
        # FIXME we may better recover the clip_path?


class GradientBase(AbstractPathEffect):
    def __init__(self, extent=None, coords=None):

        self.extent = [0, 0, 1, 1] if extent is None else extent
        self.coords = coords

        # self._image_bbox = ColorBoxLazy(
        #     alphas, bbox=bbox, coords=coords, axes=axes, **im_kw
        # )

    def get_image_box(self):
        pass

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        # self._image_bbox.set_color(rgbFace)
        # image_box = self.get_image_box()
        image_bbox = self.get_image_box()
        coords = self.coords
        if coords is None:

            def get_extent(renderer):
                bbox_out = tpath.get_extents()
                tr = BboxTransformTo(bbox_out)
                bbox = tr.transform_bbox(Bbox.from_extents(self.extent))
                return bbox

            image_bbox.set_coords(affine)
            image_bbox.set_bbox(get_extent)

        rect = gc.get_clip_rectangle()
        image_bbox.set_clip_box(rect)
        pp = TransformedPath(tpath, affine)
        image_bbox.set_clip_path(pp)
        image_bbox.draw(renderer)


class Gradient(GradientBase):
    def __init__(self, data, alpha=None, extent=None, bbox=None, coords=None, axes=None, **im_kw):

        super().__init__(extent=extent, coords=coords)

        self._image_bbox = ImageBox(
            data, alpha=alpha, bbox=bbox, coords=coords, axes=axes, **im_kw
        )

    def get_image_box(self):
        return self._image_bbox

    # def draw_path(self, renderer, gc, tpath, affine, rgbFace):
    #     # self._image_bbox.set_color(rgbFace)
    #     # image_box = self.get_image_box()
    #     super().draw_path(renderer, gc, tpath, affine, rgbFace)


class AlphaGradient(GradientBase):
    """Fill the path with image of the fill color of the path, with
    varying transparency.

    """
    def __init__(self, alphas, extent=None, bbox=None, coords=None, axes=None, **im_kw):

        # self.extent = [0, 0, 1, 1] if extent is None else extent
        # self.coords = coords
        super().__init__(extent=extent, coords=coords)

        self._image_bbox = ColorBoxLazy(
            alphas, bbox=bbox, coords=coords, axes=axes, **im_kw
        )

    def get_image_box(self):
        return self._image_bbox

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        self._image_bbox.set_color(rgbFace)

        super().draw_path(renderer, gc, tpath, affine, rgbFace)
        # coords = self.coords
        # if coords is None:

        #     def get_extent(renderer):
        #         bbox_out = tpath.get_extents()
        #         tr = BboxTransformTo(bbox_out)
        #         bbox = tr.transform_bbox(Bbox.from_extents(self.extent))
        #         return bbox

        #     self._image_bbox.set_coords(affine)
        #     self._image_bbox.set_bbox(get_extent)

        # rect = gc.get_clip_rectangle()
        # self._image_bbox.set_clip_box(rect)
        # pp = TransformedPath(tpath, affine)
        # self._image_bbox.set_clip_path(pp)
        # self._image_bbox.draw(renderer)
