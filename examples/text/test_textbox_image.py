import matplotlib.pyplot as plt

# import mplcyberpunk
# plt.style.use("cyberpunk")

fig = plt.figure(num=1, clear=True)
ax = fig.add_subplot(111)

ax.set_title("Title", size=20,
             bbox=dict(boxstyle="round", pad=0.5))

t1 = ax.text(0.5, 0.3, "Matplotlib", size=40, weight="bold",
             va="center", ha="center",
             bbox=dict(boxstyle="rarrow", pad=0.4)
)

t2 = ax.text(0.5, 0.7, "Matplotlib", size=40, weight="bold",
             va="center", ha="center",
             bbox=dict(boxstyle="larrow", pad=0.4)
)

if True:
    from mpl_visual_context.image_box_effect import (GradientBboxImage,
                                                     ColorBboxAlpha,
                                                     ImageClipEffect)

    # Title
    bp_title = ax.title.get_bbox_patch()
    c = plt.rcParams["patch.facecolor"]
    bbox_image_title = ColorBboxAlpha(c, alpha="up", coords=bp_title)
    pe_title = [ImageClipEffect(bbox_image_title, ax=ax, clip_box=None)]
    bp_title.set_path_effects(pe_title)

    # upper LArrow
    from matplotlib.colors import LinearSegmentedColormap
    bp1 = t1.get_bbox_patch()
    cmap = LinearSegmentedColormap.from_list("mycmap", ["y", "r"])
    bbox_image = GradientBboxImage("right", alpha="right",
                                   extent=[-0.3, 0, 1.3, 1],
                                   coords=bp1, cmap=cmap)
    pe = [ImageClipEffect(bbox_image, ax=ax, clip_box=None)]
    bp1.set_path_effects(pe)

    # lower RArrow
    bp2 = t2.get_bbox_patch()
    cmap = plt.get_cmap()
    bbox_image = GradientBboxImage("right", alpha="up",
                                   coords=bp2, cmap=cmap)
    pe = [ImageClipEffect(bbox_image, ax=ax, clip_box=None)]
    bp2.set_path_effects(pe)


plt.show()
