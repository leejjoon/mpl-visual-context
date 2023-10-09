import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

from mpl_visual_context.patheffects_color import StrokeColorFromFillColor

# sns.set_theme(style="ticks")
import mplcyberpunk

plt.style.use("cyberpunk")

diamonds = sns.load_dataset("diamonds")

fig, ax = plt.subplots(figsize=(7, 5), num=1, clear=True)

sns.despine(fig)

import numpy as np
bins = np.logspace(2.5, 4.3, 20)

g = diamonds.groupby("cut")
cut_names = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']

bottom = np.zeros(len(bins)-1, dtype="i")
hh = []
for i, cut in enumerate(cut_names):
    g1 = g.get_group(cut)
    cnt, edges = np.histogram(g1["price"], bins=bins)
    hh.append((cut, cnt, edges, bottom))
    bottom = bottom + cnt

for cut, cnt, edges, bottom in hh[::-1]:
    sp = ax.stairs(bottom+cnt, edges, baseline=bottom, fill=True,
                   label=cut)

ax.set_xscale("log")
ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
ax.set_xticks([500, 1000, 2000, 5000, 10000])
ax.legend()

ax.set_title("Diamonds", size=60)

from mpl_visual_context.patheffects import (RoundCorner, AlphaGradient,
                                            GCModify, StrokeOnly, StrokeColorFromFillColor,
                                            StrokeColor, FillColor,
                                            Recenter,
                                            FillImage, Partial)
from mpl_visual_context.patheffects_multicolor import MultiColorLine
from mpl_visual_context.image_box import ColorBox, ImageBox

from matplotlib.patheffects import PathEffectRenderer
from mpl_visual_context.patheffects_base import ChainablePathEffect

from mpl_visual_context.patheffects_color import BlendAlpha

class MorePathEffect(ChainablePathEffect):
    def __init__(self, pel):
        self._pel = pel

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        renderer = PathEffectRenderer(self._pel, renderer)
        return renderer, gc, tpath, affine, rgbFace

from mpl_visual_context.patheffects import ImageEffect, FillOnly, Affine, PostAffine
from mpl_visual_context.image_effect import GaussianBlur, Pad, AlphaAxb, Dilation, Erosion

bg = ax.patch.get_fc()


for p in ax.patches:
    ib_line = ColorBox(p.get_fc(), alpha="up",
                       coords=p, axes=ax)
    ib = ColorBox(p.get_fc(), alpha="0 ^ 0.5",
                  coords=p, axes=ax, blend_color=bg)
    # with the blend_color is set, the image will be blended with the given
    # color and alpha is set to 1. We do this to hide the glow under the FillImage.

    rc = RoundCorner(10)
    p.set_path_effects([
        (Partial(0, 0.5) | rc
         | GCModify(linewidth=4, alpha=1) # The alpha of line is 0 (no stroke),
                                          # so we override.
         | MultiColorLine(ib_line, min_length=5)
         | ImageEffect(Pad(20)
                       | GaussianBlur(10, channel_slice=slice(3, 4))
                       # The background have color of white (1, 1, 1). Thus we
                       # need to erode it to expand the colored region.
                       | Erosion(40, channel_slice=slice(0, 3))
                       | AlphaAxb((2, 0))
                       )
         ),
        rc | FillImage(ib),
        # We use round capstyle to remove aps between line segments. However,
        # this will make line more opaque when alpha is used. We use
        # RemoveAlpha to blend the alpha with the background color.
        (Partial(0, 0.5) | rc | GCModify(linewidth=4, capstyle="round", alpha=1.)
         | MorePathEffect([BlendAlpha(bg)])
         | MultiColorLine(ib_line, min_length=5)),
    ])

    # Now we apply patheffects to the title.

    p = ax.title
    ib = ImageBox("right", #alpha="1 ^ 0.2 ^ 1",
                  coords=p, axes=ax)

    p.set_path_effects([
        (
            GCModify(linewidth=2)
            | MultiColorLine(ib, min_length=5)
            | ImageEffect(Pad(40)
                          | GaussianBlur(10, channel_slice=slice(3, 4))
                          # The background have color of white (1, 1, 1). Thus we
                          # need to erode it to expand the colored region.
                          | Erosion(40, channel_slice=slice(0, 3))
                          | AlphaAxb((1.5, 0))
                          )
         ),
        (
            GCModify(linewidth=2, capstyle="round")
            | MultiColorLine(ib, min_length=5)
         ),
        (
            FillImage(ib, alpha=0.5)
        ),
    ])

fig.tight_layout()
plt.show()
