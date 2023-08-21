"""
====================
Violing Chart w/ ImageEffects
====================

"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()

tips = seaborn.load_dataset("tips")

fig, ax = plt.subplots(num=1, clear=True)
seaborn.violinplot(x ='day', y ='tip', data = tips, ax=ax)

from matplotlib.collections import PolyCollection
import mpl_visual_context.patheffects as pe
import mpl_visual_context.image_effect as ie

colls = [p for p in ax.collections if isinstance(p, PolyCollection)]

shadow = pe.ImageEffect(ie.AlphaAxb((0.3, 0))
                        | ie.Pad(10) | ie.Fill("k") | ie.Dilation(3)
                        | ie.Gaussian(4) | ie.Offset(3, -3))
light = pe.ImageEffect(ie.LightSource(erosion_size=5, gaussian_size=5))

pe_list = [pe.FillOnly() | shadow, pe.FillOnly() | light]

for x, coll in enumerate(colls):
    coll.set_path_effects(pe_list)

plt.show()
