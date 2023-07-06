from matplotlib import transforms
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

from matplotlib.patheffects import AbstractPathEffect

from matplotlib.transforms import (
    Affine2D, Bbox, BboxBase, BboxTransformTo, Transform)
from matplotlib.artist import Artist
from matplotlib.image import Bbox, BboxImage, AxesImage
from matplotlib.transforms import TransformedBbox

from .mpl_fix import CollectionFix

class TR:
    def __init__(self):
        pass
        # self.axes = ax

    @staticmethod
    def get_xy_transform(renderer, s, axes=None):
        """
        adopted from get_xy_transform of Text.Annotate.
        """

        if isinstance(s, tuple):
            s1, s2 = s
            from matplotlib.transforms import blended_transform_factory
            tr1 = TR.get_xy_transform(renderer, s1, axes=axes)
            tr2 = TR.get_xy_transform(renderer, s2, axes=axes)
            tr = blended_transform_factory(tr1, tr2)
            return tr
        elif callable(s):
            tr = s(renderer)
            if isinstance(tr, BboxBase):
                return BboxTransformTo(tr)
            elif isinstance(tr, Transform):
                return tr
            else:
                raise RuntimeError("Unknown return type")
        elif isinstance(s, Artist):
            bbox = s.get_window_extent(renderer)
            if not np.any(np.isfinite(bbox.get_points())):
                bbox = CollectionFix.get_window_extent(s)
            return BboxTransformTo(bbox)
        elif isinstance(s, BboxBase):
            return BboxTransformTo(s)
        elif isinstance(s, Transform):
            return s
        elif not isinstance(s, str):
            raise RuntimeError(f"Unknown coordinate type: {s!r}")

        if axes is None:
            raise ValueError("axes argument is requred.")

        figure = axes.figure

        if s == 'data':
            return axes.transData
        # elif s == 'polar':
        #     from matplotlib.projections import PolarAxes
        #     tr = PolarAxes.PolarTransform()
        #     trans = tr + self.axes.transData
        #     return trans

        s_ = s.split()
        if len(s_) != 2:
            raise ValueError(f"{s!r} is not a recognized coordinate")

        bbox0, xy0 = None, None

        bbox_name, unit = s_
        # if unit is offset-like
        if bbox_name == "figure":
            bbox0 = figure.figbbox
        elif bbox_name == "subfigure":
            bbox0 = figure.bbox
        elif bbox_name == "axes":
            bbox0 = axes.bbox
        # elif bbox_name == "bbox":
        #     if bbox is None:
        #         raise RuntimeError("bbox is specified as a coordinate but "
        #                            "never set")
        #     bbox0 = self._get_bbox(renderer, bbox)

        if bbox0 is not None:
            xy0 = bbox0.p0
        elif bbox_name == "offset":
            raise ValueError("offset is not supported")
            # xy0 = self._get_ref_xy(renderer)

        if xy0 is not None:
            # reference x, y in display coordinate
            ref_x, ref_y = xy0
            if unit == "points":
                # dots per points
                dpp = figure.dpi / 72
                tr = Affine2D().scale(dpp)
            elif unit == "pixels":
                tr = Affine2D()
            elif unit == "fontsize":
                raise ValueError("fontsize is not supported")
                # fontsize = self.get_size()
                # dpp = fontsize * igure.dpi / 72
                # tr = Affine2D().scale(dpp)
            elif unit == "fraction":
                w, h = bbox0.size
                tr = Affine2D().scale(w, h)
            else:
                raise ValueError(f"{unit!r} is not a recognized unit")

            return tr.translate(ref_x, ref_y)

        else:
            raise ValueError(f"{s!r} is not a recognized coordinate")


class ImageClipEffect(AbstractPathEffect):
    def __init__(self, im, ax=None, remove_from_axes=False, draw_path=True):
        if im.axes is None and ax is None:
            raise ValueError("im.axes should not be None")

        ax = ax if ax is not None else im.axes

        if remove_from_axes:
            im.remove()

        im.axes = ax

        self.im = im

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""

        self.im.set_clip_path(tpath, transform=affine)
        self.im.draw(renderer)

        if self.draw_path:
            renderer.draw_path(
                gc, tpath, affine, None)


def get_data_from_dir(dir, bbox=None, alpha=None):
    if bbox is None:
        bbox = Bbox.from_extents([0, 0, 1, 1])

    if isinstance(dir, str):
        if dir in ["up", "right"]:
            c0 = 0
            c1 = bbox.height
        else:
            c0 = bbox.height
            c1 = 0

        if dir in ["up", "down"]:
            data = np.linspace(c0, c1, 256).reshape((256, 1))
        else:
            data = np.linspace(c0, c1, 256).reshape((1, 256))
    else:
        data = dir

    if isinstance(alpha, str):
        if alpha in ["up", "down", "left", "right"]:
            if alpha in ["up", "right"]:
                a0, a1 = 0, 1
            else:
                a0, a1 = 1, 0

            if alpha in ["up", "down"]:
                alpha = np.linspace(a0, a1, 256).reshape((256, 1))
            else:
                alpha = np.linspace(a0, a1, 256).reshape((1, 256))

    if isinstance(alpha, np.ndarray):
        new_shape = np.broadcast_shapes(alpha.shape, data.shape)
        data = np.broadcast_to(data, new_shape)
        alpha = np.broadcast_to(alpha, new_shape)

    return data, alpha


class TransformedBboxImage(BboxImage):

    def __init__(self, data, extent=None, coords="data", axes=None,
                 alpha=None,
                 **im_kw):
        self.coords = coords
        if extent is None:
            extent = [0, 0, 1, 1]
        self.bbox_orig = Bbox.from_extents(extent)


        BboxImage.__init__(self, Bbox([[0, 0], [0, 0]]), origin="lower",
                           interpolation="none",
                           transform=mtransforms.IdentityTransform(),
                           **im_kw)

        data, alpha = self._convert_data(data, alpha=alpha)
        self.set_data(data)
        self.set_alpha(alpha)
        self.axes = axes

    def _convert_data(self, data, alpha=None):
        return data, alpha

    def draw(self, renderer):
        tr = TR.get_xy_transform(renderer, self.coords, axes=self.axes)
        trbox = TransformedBbox(self.bbox_orig, tr)
        self.bbox = trbox

        if self.axes is None and isinstance(self.coords, Artist):
            axes = self.coords.axes
        else:
            axes = self.axes

        # if axes is not None:
        #     self.set_clip_box(axes.bbox)

        # self.im.set_clip_path(tpath, transform=affine)
        BboxImage.draw(self, renderer)

class GradientBboxImage(TransformedBboxImage):
    def _convert_data(self, data, alpha=None):
        data, alpha = get_data_from_dir(data, alpha=alpha)
        return data, alpha

def get_bbox_image(data, extent=None, coords="data",
                   c0=0, c1=1., axes=None, **im_kw):
    if data == "horizontal":
        data = np.linspace(c0, c1, 256).reshape((1, 256))
    elif data == "vertical":
        data = np.linspace(c0, c1, 256).reshape((256, 1))

    if extent is None:
        extent = [0, 0, 1, 1]
    bbox = Bbox.from_extents(extent)

    tr = TR.get_xy_transform(None, coords, axes=axes)

    im = BboxImage(bbox, origin="lower",
                   interpolation="none",
                   transform=tr,
                   **im_kw)
    # bbox of self.im will be updated within 'draw_path'

    im.set_data(data)


class BboxImageEffect(AbstractPathEffect):
    def __init__(self, data, extent=None, coords="data",
                 c0=0, c1=1., axes=None, **im_kw):
        if data == "horizontal":
            data = np.linspace(c0, c1, 256).reshape((1, 256))
        elif data == "vertical":
            data = np.linspace(c0, c1, 256).reshape((256, 1))
        self.data = data

        self.bbox_image = TransformedBboxImage(data,
                                               extent=extent,
                                               coords=coords, **im_kw)
        # self.coords = coords

        # if extent is None:
        #     extent = [0, 0, 1, 1]
        # self.bbox = Bbox.from_extents(extent)
        # self.coords = coords
        # self.axes = axes
        # self.im = BboxImage(Bbox([[0, 0], [0, 0]]), origin="lower",
        #                     interpolation="none",
        #                     transform=mtransforms.IdentityTransform(),
        #                     **im_kw)
        # # bbox of self.im will be updated within 'draw_path'

        # self.im.set_data(self.data)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""

        self.bbox_image.set_clip_path(tpath, transform=affine)
        self.bbox_image.draw(renderer)
        # # bbox = self.coords.get_window_extent(renderer)
        # # print(bbox)
        # tr = TR.get_xy_transform(renderer, self.coords, axes=self.axes)
        # # print(tr)
        # trbox = TransformedBbox(self.bbox, tr)
        # self.im.bbox = trbox
        # # print(trbox)
        # # im = im

        # if self.axes is None and isinstance(self.coords, Artist):
        #     axes = self.coords.axes
        # else:
        #     axes = self.axes

        # if axes is not None:
        #     self.im.set_clip_box(axes.bbox)

        # self.im.set_clip_path(tpath, transform=affine)
        # self.im.draw(renderer)

        renderer.draw_path(
            gc, tpath, affine, None)


class GradientEffect(TransformedBboxImage):
    """It uses AxesImage and the extent are given in transData, so the image
    respects the transformation. And the scale of the image depend on its
    extent.

    For example, 'up' will have c0 = 0 and c1 = height.

    Note that the extent of the image is determined when the instance is
    created.
    """
    def __init__(self, dir, artist, norm=None, vmin=None, vmax=None,
                 alpha=None,
                 **im_kw):
        """

        dir : ["up", "down", "left", "right]
             direction of gradient
        """
        self._artist = artist

        ax = artist.axes
        # AFAIK, the get_datalim is only available for collections.
        bbox = artist.get_datalim(ax.transData)

        data, alpha = get_data_from_dir(dir, bbox, alpha=alpha)

        x1, y1, x2, y2 = bbox.extents
        im = self.image = AxesImage(ax,
                                    extent=[x1, x2, y1, y2],
                                    transform=ax.transData,
                                    origin="lower",
                                    norm=norm, **im_kw)

        im.set_data(data)
        im.set_alpha(alpha)
        if im.get_clip_path() is None:
            # image does not already have clipping set, clip to axes patch
            im.set_clip_path(ax.patch)
        im._scale_norm(norm, vmin, vmax)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""

        # # We reset the extent just in case (it may not necessary most of the
        # # time). But somehow this does not seem to work, so disabled.
        # ax = self._artist.axes

        # bbox = self._artist.get_datalim(ax.transData)
        # x1, y1, x2, y2 = bbox.extents
        # self.image.set_extent([x1, x2, y1, y2])
        # print(bbox.extents)

        self.image.set_clip_path(tpath, transform=affine)
        self.image.draw(renderer)

        renderer.draw_path(
            gc, tpath, affine, None)


# class GradientEffect(BboxImageEffect):
#     def __init__(self, data, extent=None, coords="data",
#                  c0=0, c1=1., axes=None, **im_kw):
#         if data == "horizontal":
#             data = np.linspace(c0, c1, 256).reshape((1, 256))
#         elif data == "vertical":
#             data = np.linspace(c0, c1, 256).reshape((256, 1))
#         self.data = data

#         self.bbox_image = TransformedBboxImage(data,
#                                                extent=extent,
#                                                coords=coords, **im_kw)

#     def draw_path(self, renderer, gc, tpath, affine, rgbFace):
#         """Draw the path with updated gc."""

#         self.bbox_image.set_clip_path(tpath, transform=affine)
#         self.bbox_image.draw(renderer)

#         renderer.draw_path(
#             gc, tpath, affine, None)
