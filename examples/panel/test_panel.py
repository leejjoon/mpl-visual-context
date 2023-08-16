import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_visual_context.image_box_effect import (GradientBboxImage,
                                                 ImageClipEffect)
from mpl_visual_context.patheffects import HLSModify

# plt.style.use("dark_background")
sns.set_theme()
# import mplcyberpunk
# plt.style.use("cyberpunk")

tips = sns.load_dataset("tips")

fig, ax = plt.subplots(1, 1, num=1, clear=True)

# fig, axs = plt.subplots(1, 1, num=1, clear=True, figsize=(5, 8))
# ax = axs[0]

# # Draw a nested violinplot and split the violins for easier comparison
# sns.violinplot(data=tips, x="day", y="total_bill", hue="smoker",
#                split=True, inner="quart", linewidth=1,
#                palette={"Yes": "b", "No": ".85"},
#                ax=ax)
# sns.despine(left=True)

# ax = axs[1]

# Draw a nested violinplot and split the violins for easier comparison
sns.violinplot(data=tips, x="day", y="total_bill", hue="smoker",
               split=True, inner="quart", linewidth=1,
               palette={"Yes": "b", "No": ".85"},
               ax=ax)
# sns.despine(left=True)
# sns.despine()

# from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
# from mpl_visual_context.axes_panel import axis_to_panels
# divider = make_axes_locatable(ax)
# panels = axis_to_panels(divider, axis="y")
# panels = axis_to_panels(divider, axis="x",
#                         which=["ticks", "label"])

from mpl_visual_context.axes_panel import InsetDivider, AxesDivider
from mpl_visual_context.axes_panel import add_panel
divider = InsetDivider(ax)
# divider = AxesDivider(ax)
panels = {
    "y-ticklabels": add_panel(divider, "left", "ticklabels", pad=0.),
    "y-label": add_panel(divider, "left", "label", pad=0.),
    "x-ticklabels": add_panel(divider, "bottom", "ticklabels", pad=0.),
    "x-label": add_panel(divider, "bottom", "label", pad=0.),
}

# ax.set_title("Title")
# title = add_panel(divider, "top", "title",
#                   pad=0.)

legend_panel = add_panel(divider, "top", "empty",
                         pad=0.)

# title = add_panel(divider, "top", "title",
#                   pad=0.)

# legend_panel = title

from mpl_visual_context.legend_helper import (extract_offset_boxes_from_legend,
                                              set_max_length)
from matplotlib.offsetbox import     HPacker, VPacker

leg_title, oblist = extract_offset_boxes_from_legend(ax.legend_)
set_max_length(oblist)
pack = HPacker(pad=0., sep=10, children=[leg_title] + oblist)

from matplotlib.offsetbox import AnnotationBbox, AnchoredOffsetbox

# ann = AnnotationBbox(pack, (1, 0.5), xybox=(-15, 0), xycoords='axes fraction',
#                      boxcoords="offset points", box_alignment=(1, 0.5),
#                      frameon=False,
#                      in_layout=False,
#                      )
# title.add_artist(ann)
# title._extent_list.append(ann)

box = AnchoredOffsetbox("right", child=pack,
                        pad=0,
                        frameon=False)
legend_panel.add_artist(box)
legend_panel.add_to_extent_list(box)

ax.legend_.remove()

plt.tight_layout()
plt.show()
