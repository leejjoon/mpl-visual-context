# Adopted from the example in Nicolas P. Rougier's book.

from matplotlib.transforms import IdentityTransform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patheffects import Stroke, Normal

fig = plt.figure(figsize=(8, 3), num=1, clear=True)
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
family = "Pacifico"
size = 60
text = "Matplotlib"

t = ax.text(
    0.5,
    0.45,
    text,
    size=size,
    color="black",
    weight="bold",
    va="center",
    ha="center",
    family=family,
    # bbox=dict(boxstyle="round4", ec="k", fc="none", pad=0.4)
)

from mpl_visual_context.patheffects import ClipPathFromPatch


def get_pe(
    cmap=cm.viridis, nstep=10, max_lw=45, c0=0, c1=1, clippath=None, linecolor="black"
):
    pe = []
    for x, c in zip(np.linspace(1, 0, nstep), np.linspace(c0, c1, nstep)):
        lw, color = x * max_lw, cmap(c)
        pe.append(
            ClipPathFromPatch(clippath) | Stroke(linewidth=lw + 1, foreground=linecolor)
        )
        pe.append(ClipPathFromPatch(clippath) | Stroke(linewidth=lw, foreground=color))

    return pe


# bp = t.get_bbox_patch()
bp = None
t.set_path_effects(get_pe(c0=0.8, max_lw=80, nstep=5, linecolor="k", clippath=bp))

plt.show()
