import matplotlib.pyplot as plt
import seaborn as sns

# sns.set_theme()

# from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
# from mpl_visual_context.axes_panel import axis_to_panels, title_to_panel
from mpl_visual_context.axes_panel import InsetDivider

# plt.style.use("dark_background")

if True:
    fig, ax = plt.subplots(num=1, clear=True)
    ax.set_ylabel("Test")
    ax.set_xlabel("X-label")
    ax.set_title("Title")

    # divider = make_axes_locatable(ax)
    divider = InsetDivider(ax)
    from mpl_visual_context.axes_panel import add_panel
    panels = {
        "y-ticklabels": add_panel(divider, "left", "ticklabels", pad=0.),
        "y-label": add_panel(divider, "left", "label", pad=0.),
        "x-ticklabels": add_panel(divider, "bottom", "ticklabels", pad=0.),
        "x-label": add_panel(divider, "bottom", "label", pad=0.),
        "title": add_panel(divider, "top", "title", pad=0.0,
                           axes_kwargs=dict(fc="y")),
    }

    panels["title"].annotate("Right", (1, 0.5),
                             xytext=(-5, 0),
                             va="center", ha="right")
    panels["title"].patch.set_alpha(0.3)

plt.tight_layout()
plt.show()
