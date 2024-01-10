import numpy as np
import scipy.ndimage as NI

from matplotlib.patheffects import AbstractPathEffect, Normal
from matplotlib import cbook
from matplotlib.transforms import Affine2D, TransformedBbox, Bbox, TransformedPath
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.artist import Artist

from mpl_visual_context.patheffects_base import AbstractPathEffect

from matplotlib.transforms import Affine2D
from .patheffects_transform import PostAffine


class ImageEffectBase():
    def __init__(self):

        self.agg_renderer = None
        self.renderer_prop = {}

        # dealing with dpi change in the mixed backend is VERY tricky and often
        # have no easy straightforward solution. It is possible that some
        # path_effects are not compatible with dpi change in the
        # image_effect/clipboard. A workaround could be to place an dpi_scale
        # transform (PostAffine instance, that scales with dpi) in the middle
        # of the patheffect chain and have incompatible patheffects comes
        # before the dpi_scale. This is only tested with clipboard.
        self.dpi_scale = PostAffine()
        # self.is_post_affine_setup = False

    def clear(self):
        self.agg_renderer = None
        self.renderer_prop = {}

    def init_renderer(self, renderer):
        if self.agg_renderer is not None:
            if self.renderer_prop["orig_renderer"] is not renderer:
                raise RuntimeError("inconsistent renderer")
            else:
                return

        # If the original backend is an agg backend, a new agg backend with
        # same dpi will be created. Otherwise, the new agg backednmay have
        # different dpi than the original one. Thus we need to take care of the
        # change in the dpi.

        agg_dpi = renderer.dpi  # For the pdf backend, this is the dpi set by
        # the user not the intrinsic 72.

        is_mixed_backend = hasattr(renderer, "figure")  # mixed backend. only
                                                        # tested for pdf.

        if is_mixed_backend:
            ss = renderer.figure.get_size_inches()
            # figdpi = renderer._figdpi
            width = ss[0] * agg_dpi
            height = ss[1] * agg_dpi
            scale_factor = agg_dpi / renderer._figdpi
        else:
            scale_factor = 1
            width = renderer.width #* scale_factor
            height = renderer.height #* scale_factor

        self.agg_renderer = RendererAgg(int(width), int(height), agg_dpi)
        self.renderer_prop.update(
            orig_renderer=renderer,
            is_mixed_backend=is_mixed_backend,
            scale_factor=scale_factor,
            agg_dpi=agg_dpi,
            height=height)

    def update_gc_n_affine(self, gc, affine, use_dpi_scale=False):
        self.dpi_scale.affine.clear()
        if self.renderer_prop["is_mixed_backend"]:
            scale_factor = self.renderer_prop["scale_factor"]
            if use_dpi_scale:
                new_affine = affine
                # new_affine = affine + Affine2D().scale(scale_factor)
                self.dpi_scale.affine.scale(scale_factor)
            else:
                new_affine = affine + Affine2D().scale(scale_factor)

            # clip_rect and clip_path need to be updated to refelect dpi
            # change. We may temporarily change the
            # figure's dpi_scale_trans, but this is not univeral solution.

            gc0 = self.agg_renderer.new_gc()  # Don't modify gc, but a copy!
            gc0.copy_properties(gc)

            # We first change clip_rect.
            cliprect = gc.get_clip_rectangle()
            if cliprect is not None:
                left, bottom, right, top = cliprect.extents

                cliprect0 = Bbox.from_extents(left, bottom, right, top)
                tr = Affine2D().scale(scale_factor)
                gc0.set_clip_rectangle(TransformedBbox(cliprect0, tr))

            # now, clip_path
            _tpath, _affine = gc.get_clip_path()
            if _affine is None:
                _affine = Affine2D().scale(scale_factor)
            else:
                _affine = _affine.frozen().scale(scale_factor)

            if _tpath is not None:
                gc0.set_clip_path(None)

        else:
            new_affine = affine
            gc0 = gc

        return gc0, new_affine

    def draw_with_path_effect(self, path_effect, gc0, tpath, new_affine, rgbFace):

        if path_effect is not None:
            path_effect.draw_path(self.agg_renderer, gc0, tpath, new_affine, rgbFace)
        else:
            self.agg_renderer.draw_path(gc0, tpath, new_affine, rgbFace)

    def get_rendered_image(self):
        orig_img = np.asarray(self.agg_renderer.buffer_rgba())

        slice_y, slice_x = cbook._get_nonzero_slices(orig_img[..., 3])
        cropped_img = orig_img[slice_y, slice_x] / 255.0

        # The cropped_img is in agg_dpi. The x & y need to be scaled with
        # inverse of the scale_factor for translation.
        return (
            self.renderer_prop["agg_dpi"],
            self.renderer_prop["scale_factor"],
            slice_x.start,
            (self.renderer_prop["height"] - slice_y.stop),
            cropped_img[::-1],
        )


class ImageEffect(AbstractPathEffect, ImageEffectBase):
    def __init__(self, image_effect):
        super().__init__()

        self._image_effect = image_effect
        self._path_effect = None

    def __ror__(self, other: AbstractPathEffect):
        e = ImageEffect(self._image_effect)
        e._path_effect = other
        return e

    def get_image(self, renderer, gc, tpath, affine, rgbFace):
        self.init_renderer(renderer)

        gc0, new_affine = self.update_gc_n_affine(gc, affine)

        self.draw_with_path_effect(self._path_effect, gc0, tpath, new_affine, rgbFace)

        return self.get_rendered_image()

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        dpi, scale_factor, x, y, img = self.get_image(
            renderer, gc, tpath, affine, rgbFace
        )

        dpi, scale_factor, x, y, img = self._image_effect.process_image(
            dpi, scale_factor, x, y, img
        )

        if img.size:
            if img.dtype.kind == 'f':
                img = np.asarray(img * 255.0, np.uint8)
            renderer.draw_image(gc, x / scale_factor, y / scale_factor, img)

        self.clear()


class ImageClipboard(ImageEffectBase):
    def __init__(self):
        super().__init__()

    def copy(self, use_dpi_scale=False ):
        return CopyToClipboard(self, use_dpi_scale=use_dpi_scale)

    def paste(self, image_effect, clear=True):
        return PasteFromClipboard(self, image_effect, clear=clear)


class CopyToClipboard(AbstractPathEffect):
    def __init__(self, clipboard, path_effect=None, stop_drawing=True,
                 use_dpi_scale=None):
        """
        clipboard : Clipboard
        """
        self.clipboard = clipboard
        self._path_effect = path_effect
        self.stop_drawing = stop_drawing

        # use_dpi_scale option should be turned on if you are placing the
        # dpi_scale transform in the middiel of the patheffects pipeline..

        self._use_dpi_scale = use_dpi_scale

    def __ror__(self, other: AbstractPathEffect):
        self._path_effect = other
        return self

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        clipboard = self.clipboard

        clipboard.init_renderer(renderer)

        if self._path_effect is None:
            gc0, new_affine = clipboard.update_gc_n_affine(gc, affine,
                                                           use_dpi_scale=self._use_dpi_scale)
        else:
            gc0, new_affine = clipboard.update_gc_n_affine(gc, affine,
                                                           use_dpi_scale=self._use_dpi_scale)
            # gc0, new_affine = gc, affine

        clipboard.draw_with_path_effect(self._path_effect, gc0, tpath, new_affine, rgbFace)

        if not self.stop_drawing:
            renderer.draw_path(gc, tpath, affine, rgbFace)

        return


class PasteFromClipboard(AbstractPathEffect):
    def __init__(self, clipboard, image_effect, clear=True):
        """
        clipboard : Clipboard
        """
        self.clipboard = clipboard
        self._image_effect = image_effect
        self.clear = clear

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        dpi, scale_factor, x, y, img = self.clipboard.get_rendered_image()

        if self._image_effect is not None:
            dpi, scale_factor, x, y, img = self._image_effect.process_image(
                dpi, scale_factor, x, y, img
            )

        if img.size:
            if img.dtype.kind == 'f':
                # img[..., -1] *= 0.5
                img = np.asarray(img * 255.0, np.uint8)
            renderer.draw_image(gc, x / scale_factor, y / scale_factor, img)

        if self.clear:
            self.clipboard.clear()


class ClipboardPasteArtist(Artist):
    def __init__(self, clipboard, image_effect=None,
                 clear=True,
                 **kw):
        super().__init__(**kw)
        self._clipboard = clipboard
        self._image_effect = image_effect
        self._clear = clear

    def adjust_image(self, renderer, orig_img):
        return orig_img

    def get_rendered_image(self, renderer):
        clipboard = self._clipboard
        orig_img = np.asarray(clipboard.agg_renderer.buffer_rgba())

        orig_img = self.adjust_image(renderer, orig_img)

        slice_y, slice_x = cbook._get_nonzero_slices(orig_img[..., 3])
        cropped_img = orig_img[slice_y, slice_x] / 255.0

        # The cropped_img is in agg_dpi. The x & y need to be scaled with
        # inverse of the scale_factor for translation.
        return (
            clipboard.renderer_prop["agg_dpi"],
            clipboard.renderer_prop["scale_factor"],
            slice_x.start,
            (clipboard.renderer_prop["height"] - slice_y.stop),
            cropped_img[::-1],
        )

    def draw(self, renderer):

        dpi, scale_factor, x, y, img = self.get_rendered_image(renderer)

        if self._image_effect is not None:
            dpi, scale_factor, x, y, img = self._image_effect.process_image(
                dpi, scale_factor, x, y, img
            )

        if img.size:
            if img.dtype.kind == 'f':
                img = np.asarray(img * 255.0, np.uint8)

            gc = renderer.new_gc()
            self._set_gc_clip(gc)
            renderer.draw_image(gc, x / scale_factor, y / scale_factor, img)

        if self._clear:
            self._clipboard.clear()


class ReflectionArtist(ClipboardPasteArtist):
    """This is to make a simple vertical reflection effect. It takes two
    clipboard. The first clipboard should contain the image of the mirrored
    artists. The second clipboard (clipboard_alpha) is used to adjust the alpha
    channel.

    - We take the alpha channel of the clipboard_alpha and use it as an
    object mask, and then do the distance transform.
    - We use gaussian funtion of this distance and use it as the alpha channel, so that
    the reflected image gradually become transparent away from the original object.
    """
    def __init__(self, clipboard,
                 clipboard_alpha,
                 clear_alpha=False,
                 alpha_dist_sigma=40,
                 alpha_default=0.3,
                 image_effect=None,
                 **kw):
        super().__init__(clipboard, image_effect, **kw)

        self._clipboard_alpha = clipboard_alpha
        self._clear_alpha = clear_alpha
        self._alpha_dist_sigma = alpha_dist_sigma
        self._alpha_default = alpha_default

    def adjust_image(self, renderer, orig_img):
        if self._clipboard_alpha is not None:
            alpha_img = np.asarray(self._clipboard_alpha.agg_renderer.buffer_rgba())
            alpha = alpha_img[..., -1]/255.
            dist = NI.distance_transform_edt(alpha==0)
            scale = self._clipboard.renderer_prop["scale_factor"]

            sigma = renderer.points_to_pixels(self._alpha_dist_sigma) * scale
            ee = np.exp(-(dist/sigma)**2)*orig_img[..., 3]/255.*self._alpha_default
            orig_img[..., 3] = (255*ee).astype("uint8")
        else:
            slice_y, slice_x = cbook._get_nonzero_slices(orig_img[..., 3])
            subim = orig_img[slice_y, slice_x, 3] / 255
            scale = self._clipboard.renderer_prop["scale_factor"]

            ny = subim.shape[0]
            dist = np.arange(ny)
            sigma = renderer.points_to_pixels(self._alpha_dist_sigma) * scale
            ee = np.exp(-(dist[:, np.newaxis]/sigma)**2)*subim*self._alpha_default
            orig_img[..., 3][slice_y, slice_x] = (255*ee).astype("uint8")

        return orig_img

    def draw(self, renderer):

        super().draw(renderer)

        if self._clipboard_alpha is not None and self._clear_alpha:
            self._clipboard_alpha.clear()

