from abc import abstractmethod
from matplotlib.path import Path

from .path_effects_container import PathEffectsContainer

from .patheffects_base import ChainablePathEffect, GCModify

from .patheffects_color import (
    HLSModify,
    HLSaxb,
    ColorMatrix,
    FillColor,
    StrokeColor,
    FillColorFromStrokeColor,
    StrokeColorFromFillColor,
)
from .patheffects_path import (
    Partial,
    Open,
    FillOnly,
    StrokeOnly,
    ClipPathFromPatch,
    ClipPathSelf,
    ClipRect,
    Smooth,
    SmoothFillBetween,
)
from .patheffects_transform import Offset
from .patheffects_image_box import FillImage, AlphaGradient

# from .pe_cyberfunk import GlowStroke as Glow
from .patheffects_glow import Glow, CmapGlow
from .patheffects_image_effect import ImageEffect


