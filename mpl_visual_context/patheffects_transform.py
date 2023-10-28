import matplotlib.transforms as mtransforms

from .patheffects_base import ChainablePathEffect
from .transform_helper import TR


class Offset(ChainablePathEffect):
    """
    PathEffect that offsets the path.
    """
    def __init__(self, ox, oy):
        super().__init__()
        self._ox = ox
        self._oy = oy

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        offset = mtransforms.Affine2D().translate(
            *map(renderer.points_to_pixels, [self._ox, self._oy])
        )

        return renderer, gc, tpath, affine + offset, rgbFace


class Affine(ChainablePathEffect):
    """PathEffect to apply affine trasnform the path. Note that this is applied
    before the affine of the path (this was intended to transform the text
    path)

    """
    def __init__(self, affine=None):
        super().__init__()
        if affine is None:
            affine = mtransforms.Affine2D()
        self.affine = affine

    def skew_deg(self, xShear, yShear):
        self.affine.skew_deg(xShear, yShear)
        return self

    def rotate_deg(self, degrees):
        self.affine.rotate_deg(degrees)
        return self

    def scale(self, sx, sy=None):
        self.affine.scale(sx, sy)
        return self

    def translate(self, tx, ty):
        self.affine.translate(tx, ty)
        return self

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        # This is meant to skew the text path, and the skew transform must be
        # applied before other transform.

        return renderer, gc, tpath, self.affine + affine, rgbFace


def Skew(xShear, yShear):
    return Affine().skew_deg(xShear, yShear)


class PostAffine(Affine):
    """Similar to Affine, but it will be applied after the path's affine.
    """

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        # This is meant to skew the text path, and the skew transform must be
        # applied before other transform.

        return renderer, gc, tpath, affine + self.affine, rgbFace


class Recenter(ChainablePathEffect):
    """
    PathEffect that apply offsets so that the given points to be zero.
    """
    def __init__(self, axes, ox, oy, coords="data",
                 sign=1):
        super().__init__()
        self._axes = axes
        self._ox = ox
        self._oy = oy
        self._coords = coords
        self._sign = sign

    def restore(self):
        return type(self)(self._axes, self._ox, self._oy,
                          coords=self._coords, sign=-self._sign)

    def _convert(self, renderer, gc, tpath, affine, rgbFace):

        is_mixed_backend = hasattr(renderer, "figure")  # mixed backend. only
                                                        # tested for pdf.

        # This is to better support ImageEffect/Clipboard in pdf backend.
        if not is_mixed_backend and (self._axes.figure.dpi != renderer.dpi):
            orig_dpi = self._axes.figure.dpi
            self._axes.figure.dpi = renderer.dpi

            tr = TR.get_xy_transform(renderer, self._coords, axes=self._axes)
            ox, oy = tr.transform_point([self._ox, self._oy])

            affine = affine + mtransforms.Affine2D().translate(-self._sign*ox,
                                                               -self._sign*oy)
            self._axes.figure.dpi = orig_dpi
        else:
            tr = TR.get_xy_transform(renderer, self._coords, axes=self._axes)
            ox, oy = tr.transform_point([self._ox, self._oy])

            affine = affine + mtransforms.Affine2D().translate(-self._sign*ox,
                                                               -self._sign*oy)


        return renderer, gc, tpath, affine, rgbFace
