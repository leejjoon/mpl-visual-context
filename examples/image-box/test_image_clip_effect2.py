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
            ec="none",
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


from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# # Create an inset outside the axes
# axins = inset_axes(ax, width=1, height="100%",
#                    bbox_to_anchor=(0., 0, 0, 1),
#                    bbox_transform=ax.transAxes, loc=1, borderpad=0)
# axins.tick_params(left=False, right=True, labelleft=False, labelright=True)

# ticks_to_table(ax, "left", o1=0, o2=1)

from mpl_visual_context.axes_helper import get_axislines

from mpl_visual_context.axes_panel import YTickLabelPanel
from mpl_visual_context.axes_panel import XTickLabelPanel, XLabelPanel

if True:
    tla_y = YTickLabelPanel(ax)
    tla_y.axislines[:].spine.set_visible(False)
    tla_y.axislines[:].toggle(all=False)

    tla_y.set_va("bottom")
    # tla.set_ha("left")
    # tla.set_xpos(0.)
    # tla.set_offset((5, 3))

    tla_y.set_offset((0, 3))

    pe = HLSModifyStroke(dh=0, s="-30%")
    tla_y.ax.patch.set_path_effects([pe])

    tla_x = XTickLabelPanel(ax, divider=tla_y.divider)
    tla_x.axislines[:].toggle(all=False)
    tla_x.axislines["bottom"].toggle(label=True)
    tla_x.axislines[:].spine.set_visible(False)

    tla_x.ax.set_xlabel(ax.get_xlabel())
    tla_x.set_offset((0, -2))

    # tla_x.ax.patch.set_path_effects([pe])

    tla_x2 = XLabelPanel(ax, divider=tla_y.divider)
    tla_x2.axislines[:].spine.set_visible(False)
    tla_x2.ax.patch.set_path_effects([pe])

    ax.set_xlabel("")

# def add_category_labels():
#     divider = make_axes_locatable(ax)

#     max_width = MaxWidth([])
#     axc = divider.append_axes("left", max_width + Fixed(0.2),
#                               pad=0, sharey=ax)
#     # axc.grid(True, alpha=0.5)
#     axc.set_xticks([])
#     # axc.set_facecolor("0.85")

#     axislines = get_axislines(axc)
#     axislines[:].spine.set_visible(False)
#     axislines[:].toggle(all=False)

#     for i, y in zip(gs.categories, yoffsets):
#         a = axc.annotate(calendar.month_name[int(i)], (0.5, y),
#                          xytext=(0, 0),
#                          # ha="center", va="bottom",
#                          ha="center", va="center",
#                          xycoords=("axes fraction", "data"),
#                          textcoords="offset points",
#                          fontsize="large",
#                          # color="w",
#                          # fontdict={"fontsize":"large"},
#                          )
#         max_width.add_artist(a)

#     return axc

# axc = add_category_labels()

# pe = HLSModifyStroke(dh=0, s="-30%")
# axc.patch.set_path_effects([pe])


for p in polys:
    bbox_image = GradientBboxImage("right",
                                   alpha="up",
                                   extent=[0, 0, 1, 1],
                                   # extent=[0, y1, 1, y2],
                                   coords=("axes fraction", p),
                                   cmap="cmo.thermal")

    pe = [ImageClipEffect(bbox_image, ax=ax)]
    p.set_path_effects(pe)
    #("path_effects", pe)

bbox_image = GradientBboxImage("right",
                               # alpha="up",
                               alpha=0.7,
                               extent=[0, 0, 1, 1],
                               # extent=[0, y1, 1, y2],
                               coords="axes fraction",
                               cmap="cmo.thermal")

# pe = [ImageClipEffect(bbox_image, ax=ax)]
tla_x.ax.add_artist(bbox_image)

from matplotlib.patheffects import withStroke, Stroke, Normal
# pe = [withStroke(foreground="gray", linewidth=1.2)]
pe = [Stroke(foreground="w", linewidth=1.5, alpha=0.5),
      Stroke(foreground="gray", linewidth=.7, alpha=0.5),
      Normal()]

from mpl_visual_context.pe_value_from_image import ValueFromImage
pe = [ValueFromImage(bbox_image)]

for a in tla_x.annotations:
    a.set_color("k")
    a.set_path_effects(pe)

# FIXME This does not affect the drawing, but affect the tight_bbox.
polys.set("clip_on", False)


if True:

    # ax.tick_params(axis="x", direction="inout", color="lightgray", 
    #                length=5, width=2, labelsize="large")

    axislines = get_axislines(ax)

    axislines[:].spine.set_visible(False)
    axislines["left"].toggle(all=False)

    ax.legend_.remove()

from matplotlib.transforms import Bbox, BboxTransform

def get_image_data_at_disp_xy(im, x, y, backend=None):
    """
    Return the image value at the event position or *None* if the event is
    outside the image.

    See Also
    --------
    matplotlib.artist.Artist.get_cursor_data
    """
    disp_extent = im.get_window_extent(backend)
    # if im.origin == 'upper':
    #     ymin, ymax = ymax, ymin
    arr = im.get_array()
    # disp_extent = Bbox([[xmin, ymin], [xmax, ymax]])
    array_extent = Bbox([[0, 0], [arr.shape[1], arr.shape[0]]])
    trans = BboxTransform(boxin=disp_extent, boxout=array_extent)
    point = trans.transform([x, y])
    if any(np.isnan(point)):
        return None
    j, i = point.astype(int)
    # Clip the coordinates at array bounds
    if not (0 <= i < arr.shape[0]) or not (0 <= j < arr.shape[1]):
        return None
    else:
        return arr[i, j]


# ax.set_facecolor("y")
plt.tight_layout()
plt.show()
