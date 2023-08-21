import numpy as np
from matplotlib.patheffects import AbstractPathEffect, Normal
from matplotlib import cbook
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
        agg_dpi = renderer.dpi  # For the pdf backend, this is the dpi set by
                                # the user not the intrinsic 72.

        if hasattr(renderer, "figure"):  # mixed backend. only tested for pdf.
            ss = renderer.figure.get_size_inches()
            width = ss[0] * agg_dpi
            height = ss[1] * agg_dpi
            scale_factor = agg_dpi / renderer._figdpi
        else:
            width = renderer.width
            height = renderer.height
            scale_factor = 1
        # agg_info = self._get_agg_info(renderer)

        agg_renderer = RendererAgg(int(width), int(height),
                                   agg_dpi)

        # agg_renderer.draw_path(gc, tpath, affine, rgbFace)
        # gc.set_linewidth(1)
        from matplotlib.transforms import Affine2D

        new_affine = affine + Affine2D().scale(scale_factor)

        if self._path_effect is not None:
            self._path_effect.draw_path(agg_renderer,
                                        gc, tpath, new_affine, rgbFace)
        else:
            agg_renderer.draw_path(gc, tpath, new_affine, rgbFace)

        orig_img = np.asarray(agg_renderer.buffer_rgba())
        slice_y, slice_x = cbook._get_nonzero_slices(orig_img[..., 3])
        cropped_img = orig_img[slice_y, slice_x] / 255.

        # The cropped_img is in agg_dpi. The x & y need to be scaled with
        # inverse of the scale_factor for translation.
        return (agg_dpi, scale_factor,
                slice_x.start, (height - slice_y.stop),
                cropped_img[::-1])

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        dpi, scale_factor, x, y, img = \
            self.get_image(renderer, gc, tpath, affine, rgbFace)

        dpi, scale_factor, x, y, img = \
            self._image_effect.process_image(dpi, scale_factor, x, y, img)

        if img.size:
            if img.dtype.kind == 'f':
                img = np.asarray(img * 255., np.uint8)
            renderer.draw_image(gc, x/scale_factor, y/scale_factor, img)

# class StartImageEffect(ImageEffectStart):
#     def __init__(self):
#         super().__init__(self, [])

