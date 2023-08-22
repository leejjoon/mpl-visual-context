from abc import abstractmethod
import matplotlib.transforms as mtransforms

from .patheffects_base import ChainablePathEffect


class Offset(ChainablePathEffect):
    def __init__(self, ox, oy):
        super().__init__()
        self._ox = ox
        self._oy = oy

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        offset = mtransforms.Affine2D().translate(
            *map(renderer.points_to_pixels, [self._ox, self._oy])
        )

        return renderer, gc, tpath, affine + offset, rgbFace
