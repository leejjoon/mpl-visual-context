import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_visual_context.axes_panel import axis_to_panels, title_to_panel
from mpl_visual_context.axes_panel import InsetDivider

if True:
    fig, ax = plt.subplots(num=1, clear=True)
    ax.set_ylabel("Test")
    ax.set_xlabel("X-label")
    ax.set_title("Title")

    # divider = make_axes_locatable(ax)
    divider = InsetDivider(ax)
    panelsx = axis_to_panels(divider, axis="x", pad=0.1)
    panelsy = axis_to_panels(divider, axis="y", pad=0.1)
    panel_title = title_to_panel(divider, pad=0.5)

    panel_title["title"].annotate("Right", (1, 0.5),
                                  xytext=(-5, 0),
                                  va="center", ha="right")

plt.tight_layout()
plt.show()
