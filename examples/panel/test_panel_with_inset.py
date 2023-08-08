import matplotlib.pyplot as plt
import seaborn as sns

# sns.set_theme()

from mpl_visual_context.axes_panel import PanelMaker

# plt.style.use("dark_background")


if True:
    fig, ax = plt.subplots(num=1, clear=True)

    title_panel = PanelMaker(ax).add_panel("top", "empty", pad=0.,
                                           axes_kwargs=dict(fc="k"))

    title_panel.anchor("SESSION 12", "lower left", borderpad=0.5,
                       color="w", size=15)
    title_panel.anchor(r"$\sigma=2.3$", "lower right", color="w")
    # title_panel.patch.set(lw=1, ec="k")

# plt.tight_layout()
plt.show()
