from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matplotlib.transforms as mtransforms

from mpl_visual_context.image_box_effect import (TransformedBboxImage,
                                                 GradientBboxImage,
                                                 ImageClipEffect)
from mpl_visual_context.patheffects import HLSModifyStroke

df_weather = pd.read_csv("end-part2_df.csv", index_col="date")

df_2016 = df_weather.filter(like="2016", axis=0).copy()

df_2016.reset_index(inplace=True)
df_2016["month"] = df_2016["date"].apply(lambda s: int(s.split("-")[1]))

import calendar 
import cmocean as cmo

sns.set_theme()

fig, ax = plt.subplots(1, 1, num=1, clear=True)

# fig.set_facecolor("k")

sns.kdeplot(df_2016, # ["meantempm"],
            x="meantempm",
            hue="month",
            ax=ax,
            fill=True, linewidth=2,
            # ec="none",
            )

ax.set_xlim(-18, 38)
# ax.grid(True, alpha=0.5)
ax.set_axisbelow(True)

ax.set_xticks([-15, 0, 15, 30])
ax.set_xlabel("Mean Temperature (C)", fontdict={"fontsize":"large"})


# from mpl_selector.selector import Selector, categorical_selector
from mpl_selector import categorical_selector
from mpl_visual_context.spreader import spready
# s = Selector(ax)

# gs = s.guess_category_from_legend()
gs = categorical_selector(ax, "legend")
polys = gs.select("Poly")

dy = 0.5 * max([p.get_datalim(p.axes.transData).height for p in polys])


yindices = np.array([int(c) for c in gs.categories])
month_names = [calendar.month_name[i] for i in yindices]

yoffsets = spready(polys, yindices, dy=-dy)

ax.set_ylim(min(yoffsets), max(yoffsets) + dy)

ax.set_yticks(yoffsets, labels=month_names)

ax.set_ylabel("")

# from mpl_visual_context.axes_helper import get_axislines
# from mpl_visual_context.axes_panel import YTickLabelPanel # YLabelPanel
# from mpl_visual_context.axes_panel import XTickLabelPanel, XLabelPanel

from mpl_visual_context.axes_panel import axis_to_panels


if True:
    divider = make_axes_locatable(ax)
    panels = axis_to_panels(divider, axis="y")
    # panels_x = axis_to_panels(divider, axis="x", which=["ticks"])
    panels_x = axis_to_panels(divider, axis="x", which=["label", "ticks"])
    # panels_x = axis_to_panels(divider, axis="x")
    panels.update(panels_x)

    pe = HLSModifyStroke(dh=0, l=0.9)
    for panel in panels.values():
        panel.ax.patch.set_path_effects([pe])

    panel = panels["y-ticklabels"]
    panel.set_va("bottom")
    panel.set_offset((0, 3))


if True:
    panel = panels["x-label"]
    bbox_image = GradientBboxImage("right", alpha=0.7,
                                   extent=[0, 0, 1, 1],
                                   # extent=[0, y1, 1, y2],
                                   coords="axes fraction",
                                   cmap="cmo.thermal")

    # pe = [ImageClipEffect(bbox_image, ax=ax)]
    panel.ax.add_artist(bbox_image)

    from matplotlib.patheffects import withStroke
    for a in panel.annotations:
        a.set_path_effects([withStroke(foreground="w", linewidth=5,
                                       alpha=0.7)])

    for p in polys:
        bbox_image = GradientBboxImage("right", alpha="up",
                                       extent=[0, 0, 1, 1],
                                       coords=("axes fraction", p),
                                       cmap="cmo.thermal")
        bbox_image.set_clip_box(None)

        pe = [ImageClipEffect(bbox_image, ax=ax)]
        p.set_path_effects(pe)

    polys.set("ec", "none")

    # FIXME This does not affect the drawing, but affect the tight_bbox.
    polys.set("clip_on", False)

    ax.spines["top"].set_visible(False)


ax.legend_.remove()

# ax.set_facecolor("y")
plt.tight_layout()
plt.show()
