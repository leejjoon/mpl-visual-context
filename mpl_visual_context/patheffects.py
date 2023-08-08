from abc import abstractmethod
from matplotlib.path import Path

from .path_effects_container import PathEffectsContainer

from .patheffects_base import ChainablePathEffect

from .patheffects_color import HLSModify, ColorMatrix, FillColor
from .patheffects_path import (Partial, Open, FillOnly, StrokeOnly,
                               ClipPathFromPatch)
from .patheffects_transform import Offset
# from .pe_cyberfunk import GlowStroke as Glow
from .patheffects_glow import Glow, CmapGlow

class GCModify(ChainablePathEffect):

    def __init__(self, **kwargs):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self._gc = kwargs

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
        gc0.copy_properties(gc)
        gc0 = self._update_gc(gc0, self._gc)

        return renderer, gc0, tpath, affine, rgbFace
