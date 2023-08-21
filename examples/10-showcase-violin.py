"""
====================
Violing Chart demonstraing various mpl-visual-context features
====================

"""

# import numpy as np
from mpl_visual_context.patheffects import AlphaGradient
import matplotlib.pyplot as plt
import mpl_visual_context.patheffects as pe
import seaborn
seaborn.set()

tips = seaborn.load_dataset("tips")

# We start from a simple seaborn violin plot
fig, axs = plt.subplots(2, 2, num=1, clear=True,
                        figsize=(8, 6), layout="constrained")
for ax in axs.flat:
    seaborn.violinplot(x ='day', y ='tip', data = tips, ax=ax)

ax = axs[0, 0]
ax.annotate("(a) Original violin plot",
            (0, 1), xytext=(5, -5),
            xycoords="axes fraction", va="top", ha="left",
            textcoords="offset points", # size=20,
            )

# (b) w/ Brighter fill color
ax = axs[0, 1]
# We select violin patches.
colls = ax.collections[::2]


ax.annotate("(b) Make fill color lighter,\nand stroke with the (original) fill color",
            (0, 1), xytext=(5, -5),
            xycoords="axes fraction", va="top", ha="left",
            textcoords="offset points", # size=20,
            )

pe_list = [pe.HLSModify(l=0.8) | pe.FillOnly(),
           pe.StrokeColorFromFillColor() | pe.StrokeOnly()]

for x, coll in enumerate(colls):
    coll.set_path_effects(pe_list)

# (c) AlphaGradient
ax = axs[1, 0]
colls = ax.collections[::2]

ax.annotate("(c) Fill w/ alpha gradient",
            (0, 1), xytext=(5, -5),
            xycoords="axes fraction", va="top", ha="left",
            textcoords="offset points", # size=20,
            )

pe_list = [pe.AlphaGradient("0.8 > 0.2 > 0.8"),
           (pe.StrokeColorFromFillColor()| pe.StrokeOnly())
           ]

for x, coll in enumerate(colls):
    coll.set_path_effects(pe_list)

# (4) w/ Light effect
ax = axs[1, 1]
colls = ax.collections[::2]

ax.annotate("(d) Light effect and shadow",
            (0, 1), xytext=(5, -5),
            xycoords="axes fraction", va="top", ha="left",
            textcoords="offset points", # size=20,
            )

import mpl_visual_context.image_effect as ie

pe_list = [
    # shadow
    pe.FillOnly() | pe.ImageEffect(ie.AlphaAxb((0.5, 0))
                                   | ie.Pad(10) | ie.Fill("k") | ie.Dilation(3)
                                   | ie.Gaussian(4) | ie.Offset(3, -3)),
    # light effect
    pe.HLSModify(l=0.7) | pe.FillOnly()
    | pe.ImageEffect(ie.LightSource(erosion_size=5, gaussian_size=5)),
]

for x, coll in enumerate(colls):
    coll.set_path_effects(pe_list)

plt.show()
