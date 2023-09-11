"""
====================
Smooth demo, w/ closed path
====================

Adopted from seaborn's errorband_lineplots example
"""

import numpy as np
import numpy as np
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
# from mpl_visual_context.patheffects import Smooth, StrokeColor, GCModify

from mpl_visual_context.patheffects import Smooth, SmoothClosed


import seaborn as sns
# sns.set_theme(style="darkgrid")

# Load an example dataset with long-form data
fmri = sns.load_dataset("fmri")

fig, ax = plt.subplots(num=1, clear=True)
# Plot the responses for different events and regions
sns.lineplot(x="timepoint", y="signal",
             hue="region", style="event",
             data=fmri, ax=ax)

# there are 10 lines. linesof ax.lines[4:] have no data. Not sure what they
# are.
for l in ax.lines[:4]:
    l.set_path_effects([Smooth()])

for col in ax.collections:
    col.set_path_effects([SmoothClosed()])

plt.show()
