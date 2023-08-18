"""
====================
Violing Chart
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
from mpl_visual_context.patheffects_image_bbox import (BboxAlphaPathEffect,
                                                       ColorBboxAlpha)
import mpl_visual_context.patheffects as pe

colls = [p for p in ax.collections if isinstance(p, PolyCollection)]

from mpl_visual_context.patheffects_base import AbstractPathEffect
from matplotlib.transforms import BboxTransformTo, Bbox, TransformedPath

from mpl_visual_context.patheffects_image_bbox import AlphaGradient

pe_list = [
    AlphaGradient("0.7 > 0.1 > 0.7"),
    (pe.StrokeColorFromFillColor() |
     pe.HLSModify(l="-50%") |
     pe.StrokeOnly())
]

for x, coll in enumerate(colls):
    coll.set_path_effects(pe_list)

plt.show()
