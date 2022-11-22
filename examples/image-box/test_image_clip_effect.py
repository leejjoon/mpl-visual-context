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
ax.set_xlim(-40, 40)

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
dy = 0.005

yindices = np.array([int(c) for c in gs.categories])

polys = gs.select("Poly")

yoffsets = spready(polys, yindices, dy=-dy)
ax.set_ylim(min(yoffsets)-0.1*dy, max(yoffsets)+1.5*dy)

month_names = [calendar.month_name[int(i)] for i in gs.categories]
ax.set_yticks(yoffsets, labels=month_names)
# for tck in ax.get_yticklabels():
#     print(tck)

#     ax.annotate(calendar.month_name[int(i)], (0.2, y), ha="right", va="bottom",

data = np.linspace(0, 1, 256).reshape((1, 256))
bbox_image = TransformedBboxImage(data,
                                  extent=[-29, 0, 40, 1],
                                  coords=("data", "axes fraction"),
                                  cmap="cmo.thermal")

ax.add_artist(bbox_image)

pe = [ImageClipEffect(bbox_image, remove_from_axes=True)]

# df = df_2016.query(f"month=={i}")

polys.set("path_effects", pe)

ax.grid(True, alpha=0.5)
ax.set_axisbelow(True)

ax.set_xticks([-20, 0, 20, 40])
# ax.set_yticks(yoffsets)

if True:
    for i, y in zip(gs.categories, yoffsets):
        ax.annotate(calendar.month_name[int(i)], (0.2, y), ha="right", va="bottom",
                    xycoords=("axes fraction", "data"),
                    fontsize="large",
                    # fontdict={"fontsize":"large"},
                    )

    ax.tick_params(axis="x", direction="inout", color="lightgray", 
                   length=5, width=2, labelsize="large")

    ax.set_xlabel("Mean Temperature (℃)", fontdict={"fontsize":"large"})

    from mpl_visual_context.axes_helper import get_axislines
    axislines = get_axislines(ax)

    axislines[:].spine.set_visible(False)
    axislines["left"].toggle(all=False)

    ax.legend_.remove()

plt.tight_layout()
plt.show()
