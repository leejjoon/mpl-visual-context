# from the book

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patheffects import Stroke, Normal

fig = plt.figure(figsize=(8, 3))
ax = fig.add_axes([0, 0, 1, 1], frameon=True)
family = "Pacifico"
size = 100
cmap = plt.cm.magma
text = "Matplotlib"

t = ax.text(
        0.5,
        0.45,
        text,
        size=size,
        color="white",
        weight="bold",
        va="center",
        ha="center",
        family=family,
        #:w
        #       zorder=-lw + 1,
    )
pe = []
for x in np.linspace(1, 0, 20):
    lw, color = x * 25, cmap(x)
    pe.append(Stroke(linewidth=lw, foreground=color))

t.set_path_effects(pe)

# ax.set_fc(cmap(0))
plt.show()

