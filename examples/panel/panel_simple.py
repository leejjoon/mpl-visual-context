import matplotlib.pyplot as plt

from mpl_visual_context.axes_panel import PanelMaker

fig, ax = plt.subplots(num=1, clear=True)

title_panel = PanelMaker(ax).add_panel("top", "empty", pad=0.)

title_panel.anchor("SESSION 12", loc="lower left",
                   size=15, borderpad=0.5)
title_panel.anchor(r"$\sigma=2.3$", loc="lower right")

plt.show()
