# ----------------------------------------------------------------------------
# Title:   Scientific Visualisation - Python & Matplotlib
# Author:  Nicolas P. Rougier
# License: BSD
# ----------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.patheffects import Stroke, Normal

fig = plt.figure(figsize=(8, 3))
ax = fig.add_axes([0, 0, 1, 1], frameon=False)
family = "Pacifico"
size = 100
text = "Matplotlib"

def get_pe(cmap=cm.magma, nstep=20, max_lw=225):
    pe = []
    for x in np.linspace(1, 0, nstep):
        lw, color = x * max_lw, cmap(1 - x)
        pe.append(Stroke(linewidth=lw + 1, foreground="black"))
        pe.append(Stroke(linewidth=lw, foreground=color))

    return pe

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
)
t.set_path_effects(get_pe())

t = ax.text(
    1.0,
    0.01,
    "https://matplotlib.org ",
    va="bottom",
    ha="right",
    size=10,
    color="white",
    family="Roboto",
    alpha=0.50,
)

# plt.savefig("../../figures/typography/text-outline.pdf")
plt.show()
