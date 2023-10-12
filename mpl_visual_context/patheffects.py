"""Collection of PathEffects classes.

Most of the PathEffects that inherit from `ChainablePathEffect`, and they can be pipelined
using a `|` operator to make a custom patheffects. For example, "Smooth() |
FillColor('r')`" will smooth the path and fill the region in red.

These are list of patheffects currently available.

    - color modification : `HLSModify`, `HLSaxb`, `ColorMatrix`, `FillColor`, `StrokeColor`, `FillColorFromStrokeColor`, `StrokeColorFromFillColor`
    - path modification : `Partial`, `Open`, `FillOnly`, `StrokeOnly`, `Smooth`, `SmoothFillBetween`
    - clip modification : `ClipPathFromPatch`, `ClipPathSelf`, `ClipRect`
    - transform modification : `Offset`
    - other (non-chainable): `FillImage`, `AlphaGradient`, `Glow`, `CmapGlow`, `ImageEffect`

Note that PathEffects classified as "other (non-chainable)" are not inherited
from `ChainablePathEffect`. They can be used in the pipeline but should be at
the end (or immediatenly followed by `ImageEffect`, see below), i.e.,
"FillColor('r') | Glow()" is okay but "Glow() | FillColor('r')" is not.

The `ImageEffect` is very special. It should be at the end of the pipeline,
even after other non-chainable PathEffects. It is a patheffect version of MPL's
agg filter. It will render the artist (w/ path effects in the pipeline) as an
image (using the Agg backend), apply image processing (e.g., GaussianBlur),
then place the image at the canvas.

"""

__all__ = ["GCModify", "Clipboard",
           "HLSModify", "HLSaxb", "ColorMatrix",
           "FillColor", "StrokeColor",
           "FillColorFromStrokeColor", "StrokeColorFromFillColor",
           "Partial", "Open", "FillOnly", "StrokeOnly",
           "ClipPathFromPatch", "ClipPathSelf", "ClipRect",
           "Smooth", "SmoothFillBetween", "RoundCorner",
           "Offset", "Affine", "Skew", "PostAffine", "Recenter",
           "FillImage", "AlphaGradient", "Gradient",
           "Glow", "CmapGlow",
           "ImageEffect",
           ]

from abc import abstractmethod
from matplotlib.path import Path

from .path_effects_container import PathEffectsContainer

from .patheffects_base import GCModify, Clipboard

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
    RoundCorner,
)
from .patheffects_transform import (Offset,
                                    Affine, Skew, PostAffine,
                                    Recenter)
from .patheffects_image_box import FillImage, AlphaGradient, Gradient

# from .pe_cyberfunk import GlowStroke as Glow
from .patheffects_glow import Glow, CmapGlow
from .patheffects_image_effect import ImageEffect
