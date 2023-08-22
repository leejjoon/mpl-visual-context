"""
====================
Image Effect
====================

"""
import numpy as np
from matplotlib.patheffects import AbstractPathEffect, Normal
from matplotlib import cbook
import matplotlib.pyplot as plt
from mpl_visual_context.patheffects import StrokeOnly, GCModify, ImageEffect

from abc import abstractmethod



fig, ax = plt.subplots(num=1, clear=True)
t1 = ax.text(
    0.5,
    0.5,
    "M",
    size=100,
    color="y",
    weight="bold",
    va="center",
    ha="center",
)

t2 = ax.text(
    1.5,
    0.5,
    "M",
    size=100,
    color="r",
    weight="bold",
    va="center",
    ha="center",
)

ax.set_xlim(0, 2)

from mpl_visual_context.image_effect import (AlphaAxb,
                                             Pad, Fill, Dilation, Gaussian,
                                             Offset)

from mpl_visual_context.image_effect import LightSource, LightSourceSharp


shadow = ImageEffect(AlphaAxb((0.3, 0))
                     | Pad(10) | Fill("k") | Dilation(5)
                     | Gaussian(5) | Offset(3, -3))

t1.set_path_effects([shadow,
                     ImageEffect(Pad(10) | LightSource(azdeg=215))
                     ])

t2.set_path_effects([shadow,
                     ImageEffect(Pad(10) | LightSourceSharp(azdeg=215))])
# t1.set_path_effects([
#     ImageEffect(Pad(10) | Fill("y") | LightSourceFlat() | AlphaAxb((0, 1))),
#     # ImageEffect(Pad(10) | LightSourceSharp(dist_min=5))
#     ImageEffect(Pad(10) | LightSource())
#                      ])
plt.show()
