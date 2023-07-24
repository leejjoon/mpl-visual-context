import numpy as np

import matplotlib.pyplot as plt
import mplcyberpunk

from mpl_visual_context.pe_cyberfunk import GlowStroke
from mpl_visual_context.image_box_effect import (ImageClipEffect,
                                                 ArtistBboxAlpha)
from matplotlib.patheffects import Normal

plt.style.use("cyberpunk")

fig, ax = plt.subplots(num=1, clear=True)

x = np.linspace(0, 7, 20)
y1 = np.sin(x)
y2 = np.cos(x)
l1, = ax.plot(y1, marker='o')
l2, = ax.plot(y2, marker='o')
ax.set_title("Cyberpunk", fontsize=30)
p1 = ax.fill_between(x=np.arange(len(y1)), y1=y1, y2=0)
p2 = ax.fill_between(x=np.arange(len(y1)), y1=y2, y2=0)

from matplotlib.patheffects import Stroke, Normal

for l in [l1, l2]:
    l.set_path_effects([GlowStroke()])

for p in [p1, p2]:
    p.set_alpha(0.3)
    # bbox can be a callable objects with a renderer as an argument, returning
    # a bbox object.
    def get_bbox_up(renderer):
        # returns a bbox enclosing an artist in data coordinate, but its bottom
        # coordinate replaced to zero.
        ax = p.axes
        bbox = p.get_datalim(ax.transData)
        y1, y2 = ax.get_ylim()
        bbox.y0 = 0
        return bbox
    def get_bbox_down(renderer):
        # returns a bbox enclosing an artist in data coordinate, but its upper
        # coordinate replaced to zero.
        ax = p.axes
        bbox = p.get_datalim(ax.transData)
        y1, y2 = ax.get_ylim()
        bbox.y1 = 0
        return bbox

    bbox_image_up = ArtistBboxAlpha(p, alpha="up", bbox=get_bbox_up,
                                    coords="data")
    bbox_image_down = ArtistBboxAlpha(p, alpha="down", bbox=get_bbox_down,
                                      coords="data")
    pe = [ImageClipEffect(bbox_image_up, ax=ax),
          ImageClipEffect(bbox_image_down, ax=ax)]
    p.set_path_effects(pe)

plt.show()
