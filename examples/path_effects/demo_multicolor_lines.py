"""
================
multi color line demo
================

Motivated by colored-plot.py in Scientific Visualisation book by Np. P. Rougier
"""

import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(12, 3), num=1)
fig.clf()
fig.patch.set_facecolor("black")
ax = fig.add_axes([0, 0, 1, 1], frameon=False)

# 100 points are enough for us
X = np.linspace(-5 * np.pi, +5 * np.pi, 100)

for d in np.linspace(0, 1, 15):
    dy = d / 2 + (1 - np.abs(X) / X.max()) ** 2
    dx = 1 + d / 3
    Y = dy * np.sin(dx * X) + 0.1 * np.cos(3 + 5 * X)
    l1, = ax.plot(X, Y, alpha=d)

ax.set_xlim(X.min(), X.max())
ax.set_ylim(-2.0, 2.0)

from mpl_visual_context.image_box import ImageBox
from mpl_visual_context.patheffects import Smooth
from mpl_visual_context.patheffects_multicolor import MultiColorLine

ib = ImageBox("right", cmap="rainbow", coords="axes fraction",
              axes=ax)
for l1 in ax.lines:
    l1.set_path_effects([Smooth() | MultiColorLine(ib)])

plt.show()
