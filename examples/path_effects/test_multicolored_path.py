from mpl_visual_context.patheffects import GCModify, Smooth
from mpl_visual_context.image_box import ImageBox
from mpl_visual_context.patheffects_multicolor import MultiColorLine

import matplotlib.pyplot as plt
fig, ax = plt.subplots(num=1, clear=True)

l, = ax.plot([1, 3, 2])
t = ax.text(0.5, 0.5, "Matplotlib", size=60, ha="center", va="center",
            transform=ax.transAxes)

ib = ImageBox("right", coords="axes fraction")
pe = MultiColorLine(ax, ib, min_length=10)

ib2 = ImageBox("up", coords="axes fraction", cmap="rainbow")
pe2 = MultiColorLine(ax, ib2, min_length=10)

# There could be gaps visible between segments. You may change the capstyle to
# workaround this.
t.set_path_effects([GCModify(linewidth=1, capstyle="round") |  pe])
l.set_path_effects([Smooth() | pe2])

plt.show()
