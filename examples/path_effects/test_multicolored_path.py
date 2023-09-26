from mpl_visual_context.patheffects import GCModify, Smooth
from mpl_visual_context.image_box import ImageBox
from mpl_visual_context.patheffects_multicolor import MultiColorLine

import matplotlib.pyplot as plt
fig, ax = plt.subplots(num=1, clear=True)

l, = ax.plot([1, 3, 2])
t = ax.text(0.5, 0.5, "Matplotlib", size=60, ha="center", va="center",
            transform=ax.transAxes)
ib = ImageBox("right", coords="axes fraction", zorder=1)
# ax.add_artist(ib)

pe = MultiColorLine(ax, ib, min_length=10)

t.set_path_effects([GCModify(linewidth=1) |  pe])
l.set_path_effects([Smooth() | pe])

plt.show()
