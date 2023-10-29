"""
==============
Barchart with modified path
==============

"""

from mpl_visual_context.patheffects_image_box import AlphaGradient
from mpl_visual_context.patheffects import RoundCorner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patheffects import Normal

# Fixing random state for reproducibility
np.random.seed(19680)

# Example data
n = 4
x_pos = np.arange(n)
performance = 5 * np.random.rand(n)
colors = [f"C{i}" for i in range(n)]

fig, axs = plt.subplots(2, 2, num=1, clear=True)

ax = axs.flat[0]
bars = ax.bar(x_pos, performance, align='center', alpha=0.7, color=colors)

ax = axs.flat[1]
bars = ax.bar(x_pos, performance, align='center', alpha=0.7, color=colors)
pe = [RoundCorner(10, i_selector=lambda i: i in [2, 3]) | AlphaGradient("0.2 ^ 1.")]
for p in bars:
    p.set_path_effects(pe)

from mpl_visual_context.patheffects_path import BarToArrow

ax = axs.flat[2]
bars = ax.bar(x_pos, performance, align='center', alpha=0.7, color=colors)
pe = [BarToArrow() | AlphaGradient("0.2 ^ 1.")]
for p in bars:
    p.set_path_effects(pe)

import mpl_visual_context.patheffects as pe
from mpl_visual_context.patheffects_path import BarTransformBase
from matplotlib.path import Path

class CustomBar(BarTransformBase):

    def _get_surface(self, height):
        # For now, the surface should have coordinates of [-0.5, 0] at LLC, and [0.5, h] at TRC.

        h = height

        M, L = Path.MOVETO, Path.LINETO
        vertices_right = [[0, 0], [0.5, 0], [0.5, h-0.5]]
        codes_right = [M, L, L]

        vertices_left = [[-0.5, 0], [0, 0], [0, 0]]
        codes_left = [L, L, Path.CLOSEPOLY]

        arc = Path.arc(0, 180)
        vertices_arc = 0.5 * arc.vertices[1:] + [0., h-0.5]
        vertices = np.vstack([vertices_right, vertices_arc, vertices_left])
        codes = np.concatenate([codes_right, arc.codes[1:], codes_left])
        surface = Path(vertices, codes=codes)

        return surface

class CustomBar2(BarTransformBase):
    def __init__(self, radius=0.3):
        super().__init__()
        self._radius = radius

    def _get_surface(self, h):
        circle = Path.circle(center=(0., h-0.5), radius=0.3)
        return circle

ax = axs.flat[3]
bars = ax.bar(x_pos, performance, align='center', alpha=0.7, color=colors)
pe = [
    CustomBar() | AlphaGradient("0.2 ^ 1."),
    pe.FillColor("w") | CustomBar2(),
]
for p in bars:
    p.set_path_effects(pe)

plt.show()
