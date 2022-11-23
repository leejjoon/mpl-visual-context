import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matplotlib.transforms as mtransforms

from mpl_visual_context.image_box_effect import (TransformedBboxImage,
                                                 ImageClipEffect)

# 네브라스카주 링컨시 데이터 다운: https://github.com/amcquistan/WeatherPredictPythonML
df_weather = pd.read_csv("end-part2_df.csv", index_col="date")

# 2016년 데이터만 선택
df_2016 = df_weather.filter(like="2016", axis=0)

# 날짜에서 월 추출
df_2016.reset_index(inplace=True)
df_2016["month"] = df_2016["date"].apply(lambda s: int(s.split("-")[1]))

### 시각화
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
            ec="w",
            )

# from mpl_selector.selector import Selector, categorical_selector
from mpl_selector import categorical_selector
# s = Selector(ax)

# gs = s.guess_category_from_legend()
gs = categorical_selector(ax, "legend")
ax.set_xlim(-18, 38)

def get_heights(artists):
    yy = []
    for a in artists:
        pp = a.get_paths()
        maxy = max([max(p.vertices[:, 1]) for p in pp])
        yy.append(maxy)

    return max(yy)

def spready(artists, yindices, dy=None):
    n = len(artists)
    if dy is None:
        dy = 1.
    yoffsets = yindices * dy
    for y, a in zip(yoffsets, artists):
        tr = mtransforms.Affine2D().translate(0, y) + ax.transData
        a.set_transform(tr)
        a.set_zorder(a.get_zorder() - 0.001 * y)
    return yoffsets

    # gs.categories, gs.select("Poly")):

polys = gs.select("Poly")

# dy = 0.005
dy = 0.5 * max([p.get_datalim(p.axes.transData).height for p in polys])

yindices = np.array([int(c) for c in gs.categories])

polys.set("clip_on", False)

yoffsets = spready(polys, yindices, dy=-dy)

ax.set_ylim(min(yoffsets)-0.01*dy, max(yoffsets)+0.99*dy)

month_names = [calendar.month_name[int(i)] for i in gs.categories]
ax.set_yticks(yoffsets, labels=month_names)

data = np.linspace(0, 1, 256).reshape((1, 256))
bbox_image = TransformedBboxImage(data,
                                  extent=[-29, 0, 40, 1],
                                  coords=("data", "figure fraction"),
                                  cmap="cmo.thermal",
                                  clip_box=fig.bbox)

# ax.add_artist(bbox_image)
# bbox_image.set_clip_box(fig.bbox)

# pe = [ImageClipEffect(bbox_image, remove_from_axes=True)]
pe = [ImageClipEffect(bbox_image, ax=ax)]
polys.set("path_effects", pe)

# df = df_2016.query(f"month=={i}")


ax.grid(True, alpha=0.5)
ax.set_axisbelow(True)

ax.set_xticks([-15, 0, 15, 30])
# ax.set_yticks(yoffsets)

from mpl_visual_context.axes_helper import get_axislines

def add_category_labels():
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)

    axc = divider.append_axes("left", 1.2, pad=0., sharey=ax)
    axc.grid(True, alpha=0.5)
    axc.set_xticks([])
    axc.set_facecolor("0.85")

    axislines = get_axislines(axc)
    axislines[:].spine.set_visible(False)
    axislines[:].toggle(all=False)

    for i, y in zip(gs.categories, yoffsets):
        axc.annotate(calendar.month_name[int(i)], (0.5, y),
                     xytext=(0, 3),
                     ha="center", va="bottom",
                     xycoords=("axes fraction", "data"),
                     textcoords="offset points",
                     fontsize="large",
                     # color="w",
                     # fontdict={"fontsize":"large"},
                     )

add_category_labels()

if True:

    ax.tick_params(axis="x", direction="inout", color="lightgray", 
                   length=5, width=2, labelsize="large")

    ax.set_xlabel("Mean Temperature (℃)", fontdict={"fontsize":"large"})

    axislines = get_axislines(ax)

    axislines[:].spine.set_visible(False)
    axislines["left"].toggle(all=False)

    ax.legend_.remove()

# ax.set_facecolor("y")
plt.tight_layout()
plt.show()
