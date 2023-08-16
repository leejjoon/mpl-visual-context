import numpy as np

import matplotlib.pyplot as plt
import mplcyberpunk

from mpl_visual_context.pe_cyberfunk import GlowStroke
from mpl_visual_context.image_box_effect import (ImageClipEffect,
                                                 ArtistBboxAlpha)
from matplotlib.patheffects import Normal

plt.style.use("cyberpunk")

fig, ax = plt.subplots(num=1, clear=True)

y1 = [1, 3, 9, 5, 2, 1, 1]
y2 = [4, 5, 5, 7, 10, 8, 6]
l1, = ax.plot(y1, marker='o')
l2, = ax.plot(y2, marker='o')
ax.set_title("Cyberpunk", fontsize=30)
p1 = ax.fill_between(x=np.arange(len(y1)), y1=y1, y2=0)
p2 = ax.fill_between(x=np.arange(len(y1)), y1=y2, y2=0)

from matplotlib.patheffects import Normal

for l in [l1, l2]:
    l.set_path_effects([GlowStroke()])

for p in [p1, p2]:
    p.set_alpha(0.3)

    bbox_image = ArtistBboxAlpha(p, alpha="up")
    pe = [ImageClipEffect(bbox_image, ax=ax)]
    p.set_path_effects(pe)

plt.show()
