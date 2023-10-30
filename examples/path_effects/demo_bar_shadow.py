"""
==============
HorizontalBarchart with shadows
==============

"""

from mpl_visual_context.patheffects_base import GCModify
from mpl_visual_context.patheffects_image_box import AlphaGradient
from mpl_visual_context.patheffects import RoundCorner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patheffects import Normal

# Fixing random state for reproducibility
np.random.seed(19680)

# Example data
n = 5
x_pos = np.arange(n)
performance = 5 * np.random.rand(n)
colors = [f"C{i}" for i in range(n)]

fig, ax = plt.subplots(num=1, clear=True)

import mpl_visual_context.patheffects as pe
from mpl_visual_context.patheffects_path import BarTransformBase
from matplotlib.path import Path

class CustomBar(BarTransformBase):
    def __init__(self, dh=0.5, orientation="vertical"):
        super().__init__(orientation)
        self._dh = dh

    def _get_surface(self, height):
        # For now, the surface should have coordinates of [-0.5, 0] at LLC, and [0.5, h] at TRC.

        h = height

        M, L = Path.MOVETO, Path.LINETO
        vertices_right = [[0, 0], [0.5, 0], [0.5, h-self._dh]]
        codes_right = [M, L, L]

        vertices_left = [[-0.5, 0], [0, 0], [0, 0]]
        codes_left = [L, L, Path.CLOSEPOLY]

        arc = Path.arc(0, 180)
        vertices_arc = 0.5 * arc.vertices[1:] + [0., h-self._dh]
        vertices = np.vstack([vertices_right, vertices_arc, vertices_left])
        codes = np.concatenate([codes_right, arc.codes[1:], codes_left])
        surface = Path(vertices, codes=codes)

        return surface

class CustomBar2(BarTransformBase):
    def __init__(self, radius=0.3, dh=0.5, orientation="vertical"):
        super().__init__(orientation)
        self._radius = radius
        self._dh = dh

    def _get_surface(self, h):
        circle = Path.circle(center=(0., h-self._dh), radius=self._radius)
        return circle

from mpl_poormans_3d.shadow import ShadowPath
from mpl_visual_context.patheffects_color import BlendAlpha

bars = ax.barh(x_pos, performance, align='center', alpha=0.7, color=colors)
ax.set_xlim(0, 2.8)

cb1 = CustomBar(orientation="horizontal", dh=0)
cb2 = CustomBar2(orientation="horizontal", radius=0.2, dh=0)
pe1 = [
    # pe.GCModify(linewidth=1) | pe.StrokeColorFromFillColor() | pe.StrokeOnly(),
    cb1,
    cb1 | pe.ClipPathSelf() | ShadowPath(135, 7) | pe.HLSModify(l="80%"),
    cb2 | ShadowPath(135, 5) | pe.HLSModify(l="80%"),
    cb2 | pe.GCModify(alpha=1) | pe.HLSModify(l=0.95),
]

for p in bars:
    p.set_path_effects(pe1)

for x, p in zip(x_pos, performance):
    ax.annotate(f"{p:.2f}", (p-0.1, x),
                va="center_baseline", ha="right", size=20, color="w")

pe2 = [
    ShadowPath(135, 5) | pe.HLSModify(l="20%") | pe.GCModify(alpha=0.5),
    pe.FillOnly()
]

for t in ax.texts:
    t.set_path_effects(pe2)

plt.show()
