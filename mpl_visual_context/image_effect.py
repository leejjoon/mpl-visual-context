from abc import ABC, abstractmethod
from collections.abc import Sequence

import numpy as np
import scipy.ndimage as NI

import matplotlib.colors as mcolors


class ImageEffectBase(ABC):
    @abstractmethod
    def process_image(self, dpi, scale_factor, x, y, img):
        ...


class ChainableImageEffect(ImageEffectBase):
    def __or__(self, other):
        return ChainedImageEffect(self, other)


class ChainedImageEffect(ChainableImageEffect):
    def __init__(self, ie1: ChainableImageEffect, ie2: ChainableImageEffect):
        if isinstance(ie1, ChainedImageEffect):
            self._ie_list = ie1._ie_list + [ie2]
        else:
            self._ie_list = [ie1, ie2]

    def process_image(self, dpi, scale_factor, x, y, img):
        for ie in self._ie_list:
            dpi, scale_factor, x, y, img = ie.process_image(
                dpi, scale_factor, x, y, img
            )

        return dpi, scale_factor, x, y, img


class Offset(ChainableImageEffect):
    """translate the image by the given offset"""
    def __init__(self, ox, oy):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.ox = ox
        self.oy = oy

    def process_image(self, dpi, scale_factor, x, y, img):
        return (
            dpi,
            scale_factor,
            x + scale_factor * self.ox,
            y + scale_factor * self.oy,
            img,
        )


class Fill(ChainableImageEffect):
    """fill the rgb chanell with given color. alpha channel is not affected"""
    def __init__(self, c):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.c = c

    def process_image(self, dpi, scale_factor, x, y, img):
        img = img.copy()
        img[:, :, :3] = mcolors.to_rgb(self.c)
        return dpi, scale_factor, x, y, img


class AlphaAxb(ChainableImageEffect):
    """Modify the alpha channel by element-wise operation of 'a * c + b' where
    a, b is given and c is a alpha value from the image."""
    def __init__(self, alpha_ab):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.alpha_ab = alpha_ab

    def get_pad(self):
        return 0

    def process_image(self, dpi, scale_factor, x, y, img):
        img2 = img.copy()
        a, b = self.alpha_ab
        img2[:, :, 3] = np.clip(a * img2[:, :, 3] + b, 0, 1)

        return dpi, scale_factor, x, y, img2


class Pad(ChainableImageEffect):
    """pad the image by given numberof pixels."""
    def __init__(self, pad, pady=None, *, rgb_fill=1.0, alpha_fill=0.0):
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

        scale_factor1 = dpi / 72. * scale_factor

        padx_, pady_ = self.get_pad()
        pads = int(padx_ * scale_factor1), int(pady_ * scale_factor1)

        img_rgb = np.pad(
            img[:, :, :3],
            [pads, pads, (0, 0)],
            "constant",
            constant_values=self.rgb_fill,
        )
        img_alpha = np.pad(
            img[:, :, 3], [pads, pads], "constant", constant_values=self.alpha_fill
        )
        tgt_image = np.concatenate([img_rgb, img_alpha[:, :, np.newaxis]], axis=-1)

        return dpi, scale_factor, x - pads[0], y - pads[1], tgt_image


class ImageConvBase(ChainableImageEffect):
    def __init__(self, size, channel_slice=slice(3, None)):
        "ox, oy in points (72 dpi)"
        super().__init__()
        self.size = size
        self.channel_slice = channel_slice

    def _get_scaled_size(self, size, scale_factor):
        if isinstance(size, Sequence):
            size0 = int(size[0] * scale_factor)
            size1 = int(size[1] * scale_factor)
            size = (size0, size1, size[2])
        else:
            size = int(size * scale_factor)
            size = (size, size, 0)

        return size

    def _process_image(self, img, size):
        return NI.grey_dilation(img, size)

    def process_image(self, dpi, scale_factor, x, y, img):

        scale_factor1 = dpi / 72. * scale_factor
        size = self._get_scaled_size(self.size, scale_factor1)
        cs = self.channel_slice
        img[..., cs] = self._process_image(img[..., cs], size=size)

        return dpi, scale_factor, x, y, img


class Dilation(ImageConvBase):
    """grey dilation of the image """
    def _process_image(self, img, size):
        return NI.grey_dilation(img, size)


class Erosion(ImageConvBase):
    """grey erosion of the image """
    def _process_image(self, img, size):
        return NI.grey_erosion(img, size)


class Gaussian(ImageConvBase):
    """gaussian smoothed image """

    def _get_scaled_size(self, size, scale_factor):
        if isinstance(size, Sequence):
            size0 = size[0] * scale_factor
            size1 = size[1] * scale_factor
            size = (size0, size1, size[2])
        else:
            size = size * scale_factor
            size = (size, size, 0)

        return size

    def _process_image(self, img, size):
        return NI.gaussian_filter(img, size)

GaussianBlur = Gaussian

class LightSourceBase(ChainableImageEffect):
    def __init__(
        self, fraction=1, vert_exag=1, blend_mode="overlay", azdeg=315, altdeg=45
    ):
        super().__init__()
        self.light_source = mcolors.LightSource(azdeg=azdeg, altdeg=altdeg)
        self.fraction = fraction
        self.blend_mode = blend_mode
        self.vert_exag = vert_exag

    @abstractmethod
    def get_elev(self, dpi, scale_factor, x, y, img):
        ...

    def process_image(self, dpi, scale_factor, x, y, img):

        elev = self.get_elev(dpi, scale_factor, x, y, img)

        # FIXME for some colors,eg, red, blue, overlay and soft does not
        # introduce shades. To prevent this, we simply clip the rgb values
        # between 0.2 and 0.8
        rgb = np.clip(img[:, :, :-1], 0.2, 0.8)
        rgb2 = self.light_source.shade_rgb(
            rgb,
            elev,
            fraction=self.fraction,
            vert_exag=self.vert_exag,
            blend_mode=self.blend_mode,
        )
        out = np.concatenate([rgb2, img[:, :, 3:]], -1)
        return dpi, scale_factor, x, y, out


class LightSource(LightSourceBase):
    """apply lightsource effect to the image using its alpha channel (gaussian
    smoothed) as elevation"""
    def __init__(
        self,
        erosion_size=3,
        gaussian_size=3,
        fraction=1,
        vert_exag=1,
        blend_mode="overlay",
        azdeg=315,
        altdeg=45,
    ):
        super().__init__(
            fraction=fraction,
            vert_exag=vert_exag,
            blend_mode=blend_mode,
            azdeg=azdeg,
            altdeg=altdeg,
        )

        self.erosion_size = erosion_size
        self.gaussian_size = gaussian_size

    def get_elev(self, dpi, scale_factor, x, y, img):
        scale_factor = dpi / 72. * scale_factor
        elev = img[:, :, -1]

        size = int(self.erosion_size * scale_factor)
        elev = NI.grey_erosion(elev, size=[size, size])

        size = int(self.gaussian_size * scale_factor)
        elev = NI.gaussian_filter(elev, [size, size])

        return elev


class LightSourceSharp(LightSourceBase):
    """apply lightsource effect to the image. The elevation is calculated by
    the distance transform of the alpha channel."""
    def __init__(
        self,
        dist_max=None,
        dist_min=0,
        fraction=1,
        blend_mode="overlay",
        vert_exag=1,
        azdeg=315,
        altdeg=45,
    ):
        super().__init__(
            fraction=fraction,
            vert_exag=vert_exag,
            blend_mode=blend_mode,
            azdeg=azdeg,
            altdeg=altdeg,
        )

        self.dist_max = dist_max
        self.dist_min = dist_min

    def get_elev(self, dpi, scale_factor, x, y, img):
        scale_factor = dpi / 72. * scale_factor
        elev = img[:, :, -1]

        elev = NI.distance_transform_edt(elev)
        if self.dist_max is not None:
            size = int(self.dist_max * scale_factor)
        else:
            size = np.inf
        elev = np.clip(elev, int(self.dist_min * scale_factor), size)

        return elev


