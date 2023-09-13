import numpy as np
from matplotlib.patheffects import AbstractPathEffect, Normal
from matplotlib import cbook
from matplotlib.transforms import Affine2D, TransformedBbox, Bbox, TransformedPath

# from .patheffects import StrokeOnly, GCModify

# from abc import abstractmethod

# class ChainableImageEffect:

#     # @abstractmethod
#     def process_image(self, dpi, scale_factor,
#                        x, y, img):
#         return dpi, scale_factor, x, y, img

# from matplotlib.backends._backend_agg import RendererAgg as _RendererAgg
from matplotlib.backends.backend_agg import RendererAgg

# class RendererAgg(_RendererAgg):
#     def __init__(self, width, height, dpi):
#         super().__init__(width, height, dpi)
#         self._raster_depth = 0
#         self._rasterizing = False


class ImageEffect(AbstractPathEffect):
    def __init__(self, image_effect):
        self._image_effect = image_effect
        self._path_effect = None

    def __ror__(self, other: AbstractPathEffect):
        e = ImageEffect(self._image_effect)
        e._path_effect = other
        return e

    def get_image(self, renderer, gc, tpath, affine, rgbFace):
        # If the original backend is an agg backedn, a new agg backend with
        # same dpi will be created. Otherwise, the new agg backednmay have
        # different dpi than the original one. Thus we need to take care of the
        # change in the dpi.

        agg_dpi = renderer.dpi  # For the pdf backend, this is the dpi set by
        # the user not the intrinsic 72.

        mixed_backend = hasattr(renderer, "figure")  # mixed backend. only
                                                     # tested for pdf.

        if mixed_backend:
            ss = renderer.figure.get_size_inches()
            # figdpi = renderer._figdpi
            width = ss[0] * agg_dpi
            height = ss[1] * agg_dpi
            scale_factor = agg_dpi / renderer._figdpi
        else:
            scale_factor = 1
            width = renderer.width * scale_factor
            height = renderer.height * scale_factor

        agg_renderer = RendererAgg(int(width), int(height), agg_dpi)

        if mixed_backend:
            new_affine = affine + Affine2D().scale(scale_factor)

            # clip_rect and clip_path need to be updated to refelect dpi
            # change. We may temporarily change the
            # figure's dpi_scale_trans, but this is not univeral solution.

            gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
            gc0.copy_properties(gc)

            # We first change clip_rect.
            cliprect = gc.get_clip_rectangle()
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


        if self._path_effect is not None:
            self._path_effect.draw_path(agg_renderer, gc0, tpath, new_affine, rgbFace)
        else:
            agg_renderer.draw_path(gc0, tpath, new_affine, rgbFace)

        orig_img = np.asarray(agg_renderer.buffer_rgba())

        slice_y, slice_x = cbook._get_nonzero_slices(orig_img[..., 3])
        cropped_img = orig_img[slice_y, slice_x] / 255.0

        # The cropped_img is in agg_dpi. The x & y need to be scaled with
        # inverse of the scale_factor for translation.
        return (
            agg_dpi,
            scale_factor,
            slice_x.start,
            (height - slice_y.stop),
            cropped_img[::-1],
        )

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


# class StartImageEffect(ImageEffectStart):
#     def __init__(self):
#         super().__init__(self, [])
