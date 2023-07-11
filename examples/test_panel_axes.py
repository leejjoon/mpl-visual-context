import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_visual_context.axes_panel import axis_to_panels, title_to_panel
from mpl_visual_context.axes_panel import InsetDivider, AxesDivider
from mpl_visual_context.axes_panel import add_panel

if True:
    fig, axs = plt.subplots(2, 2, num=1, clear=True)
    fig.subplots_adjust(left=0.18, right=0.95, bottom=0.25, top=0.92,
                        wspace=0.6, hspace=0.9)

    for ax, which in zip(axs.flat,
                         [["label"],
                          ["ticklabels"],
                          ["label", "ticklabels"],
                          ["ticklabels", "label"]]):

        ax.set_ylabel("Y-label")
        ax.set_xlabel("X-label")
        ax.set_title("Title")

        divider = AxesDivider(ax)
        # divider = InsetDivider(ax)

        ax_host = ax
        for w in which:
            ax1 = add_panel(divider, "left", w, pad=0)
            ax_host = ax1

        ax_host = ax
        for w in which:
            ax1 = add_panel(divider, "bottom", w, pad=0)
            ax_host = ax1

        add_panel(divider, "top", "title", pad=0)

plt.tight_layout()
plt.show()
