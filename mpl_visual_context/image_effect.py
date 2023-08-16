import numpy as np
from matplotlib.patheffects import AbstractPathEffect, Normal
from matplotlib import cbook
# from .patheffects import StrokeOnly, GCModify
import scipy.ndimage as NI

from abc import abstractmethod

class ChainableImageEffect:

    # @abstractmethod
    def process_image(self, dpi, scale_factor,
                       x, y, img):
        return dpi, scale_factor, x, y, img


class ImageEffectStart(AbstractPathEffect):
    def __init__(self, start, ie_list):
        self.start = start
        self._ie_list = ie_list

    @abstractmethod
    def get_image(self, renderer, gc, tpath, affine, rgbFace):
        ...

    def __or__(self, other):
        if isinstance(other, ChainableImageEffect):
            return ChainedImageEffect(self, other)
        else:
            raise ValueError()

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        agg_dpi, scale_factor, x, y, img = \
            self.get_image(renderer, gc, tpath, affine, rgbFace)

        if img.size:
            ox, oy = 0, 0
            # gc = renderer.new_gc()
            if img.dtype.kind == 'f':
                img = np.asarray(img * 255., np.uint8)
            renderer.draw_image(gc, x/scale_factor, y/scale_factor, img)



class ChainedImageEffect(ImageEffectStart):
    def __init__(self, ie1: ImageEffectStart, ie2: ChainableImageEffect):
        # self.start = ie1.start
        # self._ie_list = ie1._ie_list + [ie2]
        super().__init__(ie1.start, ie1._ie_list + [ie2])

        # if isinstance(ie1, ChainedImageEffect):
        # else:
        #     self._ie_list = [ie1, ie2]

    def get_image(self, renderer, gc, tpath, affine, rgbFace):
        dpi, scale_factor, x, y, img = \
            self.start.get_image(renderer, gc, tpath, affine, rgbFace)

        for ie in self._ie_list:
            dpi, scale_factor, x, y, img = \
                ie.process_image(dpi, scale_factor, x, y, img)

        return dpi, scale_factor, x, y, img


class StartImageEffect(ImageEffectStart):
    def __init__(self):
        super().__init__(self, [])

    def get_image(self, renderer, gc, tpath, affine, rgbFace):
        from matplotlib.backends._backend_agg import RendererAgg
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

        agg_renderer.draw_path(gc, tpath, affine + Affine2D().scale(scale_factor), rgbFace)

        orig_img = np.asarray(memoryview(agg_renderer))
        slice_y, slice_x = cbook._get_nonzero_slices(orig_img[..., 3])
        cropped_img = orig_img[slice_y, slice_x] / 255.

        # The cropped_img is in agg_dpi. The x & y need to be scaled with
        # inverse of the scale_factor for translation.
        return (agg_dpi, scale_factor,
                slice_x.start, (height - slice_y.stop),
                cropped_img[::-1])



class Offset(ChainableImageEffect):
    def __init__(self, ox, oy):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.ox = ox
        self.oy = oy

    def process_image(self, dpi, scale_factor, x, y, img):
        return dpi, scale_factor, x + scale_factor*self.ox, y + scale_factor*self.oy, img

import matplotlib.colors as mcolors

class Fill(ChainableImageEffect):
    def __init__(self, c):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.c = c

    def process_image(self, dpi, scale_factor, x, y, img):
        img = img.copy()
        img[:, :, :3] = mcolors.to_rgb(self.c)
        return dpi, scale_factor, x, y, img


class Pad(ChainableImageEffect):
    def __init__(self, pad, pady=None, *, rgb_fill=1., alpha_fill=0.):
        "ox, oy in points (72 dpi)"
        super().__init__()
        # self.sigma = sigma
        self.padx = pad
        self.pady = pad if pady is None else pady
        self.rgb_fill = rgb_fill
        self.alpha_fill = alpha_fill

    def get_pad(self):
        return self.padx, self.pady

    def process_image(self, dpi, scale_factor, x, y, img):

        padx_, pady_ = self.get_pad()
        pads = int(padx_*scale_factor), int(pady_*scale_factor)

        img_rgb = np.pad(img[:, :, :3], [pads, pads, (0, 0)],
                         "constant",
                         constant_values=self.rgb_fill)
        img_alpha = np.pad(img[:, :, 3], [pads, pads],
                           "constant",
                           constant_values=self.alpha_fill)
        tgt_image = np.concatenate([img_rgb, img_alpha[:, :, np.newaxis]],
                                   axis=-1)

        return dpi, scale_factor, x-pads[0], y-pads[1], tgt_image


class Dilation(ChainableImageEffect):
    def __init__(self, size):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.size = size

    def process_image(self, dpi, scale_factor, x, y, img):
        size = int(self.size * scale_factor)
        img = NI.grey_dilation(img, size=[size, size, 1])

        return dpi, scale_factor, x, y, img

class Erosion(ChainableImageEffect):
    def __init__(self, size):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.size = size

    def process_image(self, dpi, scale_factor, x, y, img):
        size = int(self.size * scale_factor)
        img = NI.grey_erosion(img, size=[size, size, 1])

        return dpi, scale_factor, x, y, img


from matplotlib.colors import LightSource as _LightSource

class LightSource(ChainableImageEffect):
    def __init__(self, erosion_size=3, gaussian_size=3, fraction=1):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.light_source = _LightSource()
        self.erosion_size = erosion_size
        self.gaussian_size = gaussian_size
        self.fraction = fraction

    def process_image(self, dpi, scale_factor, x, y, img):

        elev = img[:, :, -1]
        # msk = elev > 0.5
        # img[~msk,:-1] = 0

        size = int(self.erosion_size * scale_factor)
        elev = NI.grey_erosion(elev, size=[size, size])

        size = int(self.gaussian_size * scale_factor)
        elev = NI.gaussian_filter(elev, [size, size])

        # FIXME for some colors,eg, red, blue, overlay and soft does not
        # introduce shades. To prevent this, we simply clip the rgb values
        # between 0.2 and 0.8
        rgb = np.clip(img[:, :, :-1], 0.2, 0.8)
        rgb2 = self.light_source.shade_rgb(rgb, elev,
                                           fraction=self.fraction,
                                           blend_mode="overlay")
        out = np.concatenate([rgb2, img[:,:,3:]], -1)
        return dpi, scale_factor, x, y, out

# vv = _LightSource().hillshade(elev)

# kk = _LightSource().shade_rgb(rgb, elev, blend_mode="hsv")

class Gaussian(ChainableImageEffect):
    def __init__(self, sigma):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.sigma = sigma

    # def get_pad(self):
    #     return self.sigma*3

    def process_image(self, dpi, scale_factor, x, y, img):
        # pad = int(self.get_pad()*scale_factor)
        # img_rgb = np.pad(img[:, :, :3], [(pad, pad), (pad, pad), (0, 0)],
        #                  "constant",
        #                  constant_values=1.)
        # img_alpha = np.pad(img[:, :, 3], [(pad, pad), (pad, pad)],
        #                    "constant",
        #                    constant_values=0.)
        # img = np.concatenate([img_rgb, img_alpha[:, :, np.newaxis]], axis=-1)
        s = self.sigma * scale_factor
        tgt_image = NI.gaussian_filter(img, [s, s, 0])

        return dpi, scale_factor, x, y, tgt_image

class AlphaAxb(ChainableImageEffect):
    def __init__(self, alpha_ab):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.alpha_ab = alpha_ab

    def get_pad(self):
        return 0

    def process_image(self, dpi, scale_factor, x, y, img):
        img2 = img.copy()
        a, b = self.alpha_ab
        img2[:,:,3] = a * img2[:, :, 3] + b

        return dpi, scale_factor, x, y, img2

