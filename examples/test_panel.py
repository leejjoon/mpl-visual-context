import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_visual_context.image_box_effect import (GradientBboxImage,
                                                 ImageClipEffect)
from mpl_visual_context.patheffects import HLSModifyStroke

sns.set_theme()

tips = sns.load_dataset("tips")

fig, ax = plt.subplots(1, 1, num=1, clear=True)
ax = ax

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
sns.despine(left=True)

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_visual_context.axes_panel import axis_to_panels
divider = make_axes_locatable(ax)
panels = axis_to_panels(divider, axis="y")
panels = axis_to_panels(divider, axis="x",
                        which=["ticks", "label"])
plt.tight_layout()
plt.show()
