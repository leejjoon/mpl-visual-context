
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# Create the data : copied from examples/kde_ridgeplot.py
rs = np.random.RandomState(1979)
x = rs.randn(100)


fig, ax = plt.subplots(1, 1, num=1, clear=True)

sns.kdeplot(x, fill=True, lw=2, ec="r")

ax.set_ylim(ymin=-0.02)

from mpl_visual_context.patheffects import PartialStroke, OpenStroke

p = ax.collections[0]

# The 1st half of the path is the bottom line, thus we only strke the 2nd half,
# and do not close the path.
p.set_path_effects([PartialStroke(0.5, 1.) | OpenStroke()])

plt.show()
