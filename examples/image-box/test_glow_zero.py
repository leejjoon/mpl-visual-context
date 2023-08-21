"""
====================
Gradient in data coordinates
====================

"""
import numpy as np

import matplotlib.pyplot as plt
import mplcyberpunk

# from mpl_visual_context.pe_cyberfunk import GlowStroke
from matplotlib.patheffects import Normal
from mpl_visual_context.patheffects import (Glow, AlphaGradient)
from mpl_visual_context.artist_helper import get_datalim

plt.style.use("cyberpunk")

fig, ax = plt.subplots(num=1, clear=True)

x = np.linspace(0, 7, 20)
y1 = np.sin(x)
y2 = np.cos(x)

l1, = ax.plot(y1, marker='o')
l2, = ax.plot(y2, marker='o')
p1 = ax.fill_between(x=np.arange(len(y1)), y1=y1, y2=0)
p2 = ax.fill_between(x=np.arange(len(y1)), y1=y2, y2=0)

ax.set_title("Cyberpunk", fontsize=30)

for l in [l1, l2]:
    l.set_path_effects([Glow(), Normal()])

for p in [p1, p2]:
    # bbox can be a callable objects with a renderer as an argument, returning
    # a bbox object.
    def get_bbox_up(renderer):
        # returns a bbox enclosing an artist in data coordinate, but its bottom
        # coordinate replaced to zero.
        bbox = get_datalim(p)
        bbox.y0 = 0
        return bbox
    def get_bbox_down(renderer):
        # returns a bbox enclosing an artist in data coordinate, but its upper
        # coordinate replaced to zero.
        bbox = get_datalim(p)
        bbox.y1 = 0
        return bbox

    alpha_max = 0.3
    bbox_image_up = AlphaGradient(f"0 ^ {alpha_max}", bbox=get_bbox_up,
                                  axes=ax, coords="data")
    bbox_image_down = AlphaGradient(f"{alpha_max} ^ 0.", bbox=get_bbox_down,
                                    axes=ax, coords="data")
    p.set_path_effects([bbox_image_up, bbox_image_down])

plt.show()
