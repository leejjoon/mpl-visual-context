# Adopted from seaborn's timeseries_facets example

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="dark")
flights = sns.load_dataset("flights")

fig, ax = plt.subplots()

sns.lineplot(
    data=flights, x="month", y="passengers", units="year",
    hue="year",
    estimator=None,
    ax=ax
)

fig.tight_layout()

from mpl_visual_context.patheffects import Smooth

pe_smooth = Smooth()
for l in ax.lines:
    l.set_path_effects([pe_smooth])

plt.show()
