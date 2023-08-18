"""
====================
Demo
====================

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

from mpl_visual_context.image_box_effect import (GradientBboxImage,
                                                 ImageClipEffect)
from mpl_visual_context.patheffects import HLSModify

df_weather = pd.read_csv("end-part2_df.csv", index_col="date")

df_2016 = df_weather.filter(like="2016", axis=0).copy()

df_2016.reset_index(inplace=True)
df_2016["month"] = df_2016["date"].apply(lambda s: int(s.split("-")[1]))

import calendar

use_cyberpunk = False
if use_cyberpunk:
    import mplcyberpunk
    plt.style.use("cyberpunk")
    cmap = None
else:
    sns.set_theme()
    import cmocean as cmo
    cmap = "cmo.thermal"


fig, ax = plt.subplots(1, 1, num=1, clear=True)

sns.kdeplot(df_2016, # ["meantempm"],
            x="meantempm",
            hue="month",
            ax=ax,
            fill=True, linewidth=2,
            )

ax.set_xlim(-18, 38)
ax.set_axisbelow(True)

ax.set_xticks([-15, 0, 15, 30])
ax.set_xlabel("Mean Temperature (C)", fontdict={"fontsize":"large"})

from mpl_selector import categorical_selector
from mpl_visual_context.spreader import spready

gs = categorical_selector(ax, "legend")
polys = gs.select("Poly")

dy = 0.5 * max([p.get_datalim(p.axes.transData).height for p in polys])

yindices = np.array([int(c) for c in gs.categories])
month_names = [calendar.month_name[i] for i in yindices]

yoffsets = spready(polys, yindices, dy=-dy)

ax.set_ylim(min(yoffsets), max(yoffsets) + dy)
ax.set_yticks(yoffsets, labels=month_names)
ax.set_ylabel("")

from mpl_visual_context.axes_panel import AxesDivider, InsetDivider, add_panel

# convert labels to panels

# divider = AxesDivider(ax)
divider = InsetDivider(ax)

panels = {}
panels["y-ticklabels"] = add_panel(divider, "left", "ticklabels")
panels["x-label"] = add_panel(divider, "bottom", "label")
panels["x-ticklabels"] = add_panel(divider, "bottom", "ticklabels")

from mpl_visual_context import check_dark

pe_panel = dict(light=HLSModify(dh=0., dl=-0.05),
                dark=HLSModify(dh=0., dl=0.05))

for panel in panels.values():
    if check_dark(panel.patch.get_fc()):
        pe = pe_panel["dark"]
    else:
        pe = pe_panel["light"]

    panel.patch.set_path_effects([pe])

panel = panels["y-ticklabels"]
panel.grid(True)
panel.annotations_set_va("bottom")
panel.annotations_set_offset((0, 3))

# gradient effect

panel = panels["x-label"]
bbox_image = GradientBboxImage("right", alpha=0.7,
                               extent=[0, 0, 1, 1],
                               coords="axes fraction",
                               cmap=cmap)

panel.add_artist(bbox_image)

for p in polys:
    bbox_image = GradientBboxImage("right", alpha="up",
                                   extent=[0, 0, 1, 1],
                                   coords=("axes fraction", p),
                                   cmap=cmap)
    pe = [ImageClipEffect(bbox_image, ax=ax, clip_box=None)]
    p.set_path_effects(pe)
    p.set_zorder(p.get_zorder() + 3)

# FIXME This does not affect the drawing, but affect the tight_bbox.
polys.set("clip_on", False)

ax.legend_.remove()

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()
