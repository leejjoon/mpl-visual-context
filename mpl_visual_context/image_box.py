"""
ImageBox
"""
from abc import ABC, abstractmethod

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.colors as mcolors

from matplotlib.transforms import (
    Bbox,
    IdentityTransform,
)
from matplotlib.image import Bbox, BboxImage
from matplotlib.transforms import TransformedBbox, BboxTransformFrom

from .transform_helper import TR

__all__ = ["ImageBox", "ColorBox", "ColorBoxLazy"]

GRADIENT_DIRECTIONS = ["up", "down", "left", "right"]


class _GradBase:
    def __init__(self, x_or_v, v=None, xmin=0.0, xmax=1.0):
        self.xmin = xmin
        self.xmax = xmax

        if v is None:
            self.v = x_or_v
            self.x = np.linspace(0, 1, len(self.v))
        else:
            self.x = x_or_v
            self.v = v

    # def get_2d(self, shape=None):
    #     x = np.linspace(self.xmin, self.xmax, self.size)
    #     grad = interp1d(self.x, self.v)(x)

    #     return grad.reshape(self.RESHAPE_TARGET)


class GradH(_GradBase):
    def get_2d(self, shape=None):
        if shape is None:
            size = 256
        else:
            size = shape[1]
        x = np.linspace(self.xmin, self.xmax, size)
        grad = interp1d(self.x, self.v)(x)

        return grad.reshape((1, size))


class GradV(_GradBase):
    def get_2d(self, shape=None):
        if shape is None:
            size = 256
        else:
            size = shape[0]
        x = np.linspace(self.xmin, self.xmax, size)
        grad = interp1d(self.x, self.v)(x)

        return grad.reshape((size, 1))


def _gradient_from_string(s, xmin=0.0, xmax=1.0):
    if ">" in s:
        vv = [float(v) for v in s.split(">")]
        return GradH(vv, xmin=xmin, xmax=xmax)
    elif "^" in s:
        vv = [float(v) for v in s.split("^")]
        return GradV(vv, xmin=xmin, xmax=xmax)
    else:
        raise ValueError(f"Unknown gradient string: {s}")


def get_gradient_array_from_str(s: str, shape=None, zmin: float = 0, zmax: float = 1):
    if s in ["up", "down", "left", "right"]:
        dir = s
        # shape = (128, 256)
        if dir in ["up", "right"]:
            a0, a1 = zmin, zmax
        else:
            a0, a1 = zmax, zmin

        if dir in ["up", "down"]:
            shape = (256, 1) if (shape is None or shape[0] == 1) else shape[:2]
            g = GradV([a0, a1])
            # l = shape[0]
            # shape_intermediate = (l, 1)
        else:
            shape = (1, 256) if (shape is None or shape[1] == 1) else shape[:2]
            g = GradH([a0, a1])
            # l = shape0[1]
            # shape_intermediate = (1, 1)

        d = g.get_2d(shape)
    else:
        d = _gradient_from_string(s).get_2d(shape=shape)
        if shape is None:
            shape = d.shape

    d = np.broadcast_to(d, shape)

    return d


def test_dir():
    d = get_gradient_array_from_str("up")
    assert np.all(d == np.linspace(0, 1, 256).reshape((256, 1)))

    d = get_gradient_array_from_str("down")
    assert np.all(d == np.linspace(1, 0, 256).reshape((256, 1)))

    d = get_gradient_array_from_str("right")
    assert np.all(d == np.linspace(0, 1, 256).reshape((1, 256)))

    d = get_gradient_array_from_str("left")
    assert np.all(d == np.linspace(1, 0, 256).reshape((1, 256)))


def test_ss():
    d = get_gradient_array_from_str("0 > 1")
    assert np.all(d == np.linspace(0, 1, 256).reshape((1, 256)))

    d = get_gradient_array_from_str("right", shape=(1, 128))
    assert np.all(d == np.linspace(0, 1, 128).reshape((1, 128)))

    d = get_gradient_array_from_str("right", shape=(128, 128))
    assert np.all(d == np.linspace(0, 1, 128).reshape((1, 128)))

    d = get_gradient_array_from_str("0 ^ 1")
    assert np.all(d == np.linspace(0, 1, 256).reshape((256, 1)))


def get_data_from_str(data, alpha=None, shape=None):

    if isinstance(data, str):
        data = get_gradient_array_from_str(data, shape=shape)  # zmin=0, zmax=1,
    elif isinstance(data, np.ndarray):
        if shape is not None:
            assert shape == np.broadcast_shapes(data.shape, shape)
        else:
            shape = data.shape
    else:
        raise ValueError(f"data should an instance of ndarray or a string")

    if isinstance(alpha, str):
        alpha = get_gradient_array_from_str(alpha, shape=shape)

    if isinstance(alpha, np.ndarray):
        if len(data.shape) == 3:
            new_shape = np.broadcast_shapes(alpha.shape, data.shape[:2])
            data = np.broadcast_to(data, new_shape + data.shape[2:])
            alpha = np.broadcast_to(alpha, new_shape)
        else:
            new_shape = np.broadcast_shapes(alpha.shape, data.shape)
            data = np.broadcast_to(data, new_shape)
            alpha = np.broadcast_to(alpha, new_shape)

    return data, alpha


def test_da():
    d, a = get_data_from_str("right", alpha=None, shape=None)
    assert np.all(d == np.linspace(0, 1, 256).reshape((1, 256)))
    assert a is None

    d, a = get_data_from_str("right", alpha="up", shape=None)
    assert np.all(d == np.linspace(0, 1, 256).reshape((1, 256)))
    assert np.all(a == np.linspace(0, 1, 256).reshape((256, 1)))

    # z = np.zeros((10, 10, 3))
    # z[:, :, 0] = np.arange(100).reshape((10, 10))/100.
    # d, a = get_data_from_str(z, alpha="right", shape=None)
    # assert np.all(d == np.linspace(0, 1, 256).reshape((1, 256)))
    # assert a is None


class TransformedBboxBase(BboxImage):
    """BboxImage which support flexible coordinate system similar to the annotation. This should be a base class, and the image  data (and alpha) should be set by the subclass.."""

    def _get_bbox_orig(self, extent, bbox):
        """
        Returns a bbox from the extent if extent is not None, otherwise
        returns a bbox itself. If both are None, return s unit bbox.
        """

        if bbox is not None:
            if extent is not None:
                raise ValueError("extent should be None if bbox is given")
            bbox_orig = bbox
        else:
            if extent is None:
                extent = [0, 0, 1, 1]
            bbox_orig = Bbox.from_extents(extent)

        return bbox_orig

    def __init__(self, extent=None, bbox=None, coords="data", axes=None,
                 blend_color=None, **im_kw):
        self.coords = coords
        self.bbox_orig = self._get_bbox_orig(extent, bbox)
        BboxImage.__init__(
            self,
            Bbox([[0, 0], [0, 0]]),
            origin="lower",
            interpolation="none",
            transform=IdentityTransform(),
            **im_kw,
        )
        self.axes = axes
        self._blend_color = blend_color

    def set_extent(self, extent, bbox=None):
        self.bbox_orig = self._get_bbox_orig(extent, bbox)

    def set_bbox(self, bbox):
        "bbox or a callable which take a renderer as an arguemnt"
        self.bbox_orig = bbox

    def set_coords(self, coords):
        self.coords = coords

    def init_data_n_alpha(self, data, alpha=None):
        data, alpha = self._convert_data(data, alpha=alpha)
        self.set_data(data)
        self.set_alpha(alpha)

    def _convert_data(self, data, alpha=None):
        return data, alpha

    def draw(self, renderer):
        tr = TR.get_xy_transform(renderer, self.coords, axes=self.axes)
        if callable(self.bbox_orig):
            bbox_orig = self.bbox_orig(renderer)
        else:
            bbox_orig = self.bbox_orig
        trbox = TransformedBbox(bbox_orig, tr)
        self.bbox = trbox

        super().draw(renderer)

    def pick_color_from_image(self, renderer, xy):
        """
        xy in display coordinate. shape of (N, input_dim)

        return the color value at point x, y.
        """

        tr = TR.get_xy_transform(renderer, self.coords, axes=self.axes)
        if callable(self.bbox_orig):
            bbox_orig = self.bbox_orig(renderer)
        else:
            bbox_orig = self.bbox_orig
        trbox = TransformedBbox(bbox_orig, tr)

        # xy = ax.transAxes.transform([[0, 0], [0.5, 0.5], [1, 1]])
        xy2 = BboxTransformFrom(trbox).transform(xy)

        # we cache the image if not cached.
        if self._imcache is None:
            A = self._A
            self._imcache = self.to_rgba(A, bytes=True, norm=(A.ndim == 2))
            if not(len(A.shape) == 3 and A.shape[-1] == 4):
                # FIXME to_rgba returns alpha of 1?
                alpha = self.get_alpha()
                self._imcache[..., -1] = 255 * (1 if alpha is None else alpha)

        ny, nx = self._imcache.shape[:2]

        ij = (xy2 * [nx, ny]).astype("i")

        # we simply clip the indices between 0 and n-1. Thus the coordinates
        # outside the box will have a color of nearby pixel, not NA.
        ij2 = np.clip(ij, [0, 0], [nx-1, ny-1])

        colors = self._imcache[ij2[:, 1], ij2[:, 0]]
        return colors

    def _make_image(self, A, in_bbox, out_bbox, clip_bbox, magnification=1, unsampled=False, round_to_pixel_border=True):
        im = super()._make_image(A, in_bbox, out_bbox,
                                 clip_bbox, magnification, unsampled, round_to_pixel_border)

        if self._blend_color:
            blend_color = np.array(mcolors.to_rgb(self._blend_color)) * 255
            d = im[0]
            alpha = d[..., 3:] / 255
            d2  = np.zeros_like(d)
            d2[..., 3] = 255
            d2[..., :3] = (d[..., :3] * alpha) + blend_color*(1-alpha)
            return d2, *im[1:]

        else:
            return im


class ImageBox(TransformedBboxBase):
    def __init__(
            self,
            data,
            alpha=None,
            shape=None,
            extent=None,
            bbox=None,
            coords="data",
            axes=None,
            **im_kw,
    ):
        """
        data: 2d-ndarray, directional string (up, down, right, left), interp-string ('0. > 0.5 > 0.)
        """

        self._respect_alpha = False

        # we do not support data of mpl color specification for possible
        # comflict with array.
        super().__init__(extent=extent, bbox=bbox, coords=coords, axes=axes, **im_kw)
        self.init_data_n_alpha(data, alpha=alpha, shape=shape)

    def init_data_n_alpha(self, data, alpha=None, shape=None):
        data, alpha = self._convert_data(data, alpha=alpha, shape=shape)
        if len(data.shape) == 3 and data.shape[-1] == 3:
            # FIXME MxNx3 image is set, alpha as array is not
            # respected. This is a workaround.
            if alpha is None:
                alpha = np.ones(data.shape[:-1], dtype=data.dtype)
            data = np.concatenate([data, alpha[:, :, np.newaxis]], axis=-1)
            self.set_data(data)
        else:
            self.set_data(data)
            self.set_alpha(alpha)

    def _convert_data(self, data, alpha=None, shape=None):
        data, alpha = get_data_from_str(data, alpha=alpha, shape=shape)

        return data, alpha

    def _check_unsampled_image(self):
        return True

    def _make_image(
        self,
        A,
        in_bbox,
        out_bbox,
        clip_bbox,
        magnification=1.0,
        unsampled=False,
        round_to_pixel_border=True,
    ):
        if not unsampled:
            im = super()._make_image(
                A,
                in_bbox,
                out_bbox,
                clip_bbox,
                magnification=magnification,
                unsampled=unsampled,
                round_to_pixel_border=round_to_pixel_border,
            )
            return im

        else:
            # FIXME for unsampled, alpha may not be
            # respected. This is a workaround.
            self._respect_alpha = True
            r = super()._make_image(
                A,
                in_bbox,
                out_bbox,
                clip_bbox,
                magnification=magnification,
                unsampled=unsampled,
                round_to_pixel_border=round_to_pixel_border,
            )
            self._respect_alpha = False
            return r

    def to_rgba(self, x, alpha=None, bytes=False, norm=True):
        # FIXME for unsampled, MxN image is set, alpha is not
        # respected. This is a workaround.

        if self._respect_alpha and alpha is None:
            alpha = self.get_alpha()

        return super().to_rgba(x, alpha=alpha, bytes=bytes, norm=norm)


class ColorBoxBase(ABC, TransformedBboxBase):
    """image of single color with alpha gradient"""

    def __init__(
        self,
        alpha,
        shape=None,
        extent=None,
        bbox=None,
        coords="data",
        axes=None,
        **im_kw,
    ):
        super().__init__(extent=extent, bbox=bbox, coords=coords, axes=axes, **im_kw)
        # The shape of image is determined by the shape of alpha
        self._alpha_array = get_gradient_array_from_str(alpha, shape=shape)
        self._A = np.zeros(self._alpha_array.shape + (4,), dtype=float)

    def _check_unsampled_image(self):
        return True

    def update_A(self):
        "the array need to be explicitly updated if color or alpha is changed after initialiation"
        color = self.get_color()
        self._update_A_rgb(color)
        alpha = self.get_alpha()
        self._update_A_alpha(alpha)

    @abstractmethod
    def get_color(self):
        ...

    def _update_A_rgb(self, color):
        rgb = mcolors.to_rgb(color)
        self._A[..., :3] = rgb

    def _update_A_alpha(self, alpha):
        self._A[..., -1] = (alpha if alpha else 1) * self._alpha_array


class ColorBox(ColorBoxBase):
    def __init__(
        self, color, alpha, extent=None, bbox=None, coords="data", axes=None, **im_kw
    ):
        super().__init__(
            alpha, extent=extent, bbox=bbox, coords=coords, axes=axes, **im_kw
        )

        self.set_color(color)
        # _A is internal array that is used by to show the image. For this to
        # work, _check_unsampled_image method should return True.
        self.update_A()

    def set_color(self, color):
        self._color = color

    def get_color(self):
        return self._color


class ColorBoxLazy(ColorBoxBase):
    def __init__(
        self, alpha, extent=None, bbox=None, coords="data", axes=None, **im_kw
    ):
        super().__init__(
            alpha, extent=extent, bbox=bbox, coords=coords, axes=axes, **im_kw
        )
        self._color = None

    def set_color(self, color):
        self._color = color

    def get_color(self):
        return self._color

    def get_alpha(self):
        rgba = mcolors.to_rgba(self.get_color())
        return rgba[-1]

    def draw(self, renderer):
        if self.get_color() is None:
            raise RuntimeError("color must be set before draw")
        self.update_A()
        super().draw(renderer)
