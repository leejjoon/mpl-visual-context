"""
==========
AGG filter
==========

Most pixel-based backends in Matplotlib use `Anti-Grain Geometry (AGG)`_ for
rendering. You can modify the rendering of Artists by applying a filter via
`.Artist.set_agg_filter`.

.. _Anti-Grain Geometry (AGG): http://agg.sourceforge.net/antigrain.com
"""

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.colors import LightSource
from matplotlib.artist import Artist
import numpy as np
from matplotlib.patheffects import Normal

from mpl_visual_context.image_effect import (StartImageEffect, AlphaAxb,
                                             Pad, Fill, Dilation, Gaussian,
                                             Offset, LightSource)

from mpl_visual_context.patheffects import (StrokeOnly, GCModify,
                                            FillColor)

def filtered_text(ax):
    # mostly copied from contour_demo.py

    # prepare image
    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X**2 - Y**2)
    Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
    Z = (Z1 - Z2) * 2

    # draw
    ax.imshow(Z, interpolation='bilinear', origin='lower',
              cmap=cm.gray, extent=(-3, 3, -2, 2), aspect='auto')
    levels = np.arange(-1.2, 1.6, 0.2)
    CS = ax.contour(Z, levels,
                    origin='lower',
                    linewidths=2,
                    extent=(-3, 3, -2, 2))

    # contour label
    cl = ax.clabel(CS, levels[1::2],  # label every second level
                   inline=True,
                   fmt='%1.1f',
                   fontsize=11)

    # change clabel color to black
    from matplotlib.patheffects import Normal
    for t in cl:
        # t.set_color("k")
        # # to force TextPath (i.e., same font in all backends)
        # t.set_path_effects([Normal()])
        t.set_path_effects([StartImageEffect() |
                            Pad(10) | Fill("w") | Dilation(5) | Gaussian(1),
                            FillColor("k")
                            ])

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)


def drop_shadow_line(ax):
    # copied from examples/misc/svg_filter_line.py

    # draw lines
    l1, = ax.plot([0.1, 0.5, 0.9], [0.1, 0.9, 0.5], "bo-")
    l2, = ax.plot([0.1, 0.5, 0.9], [0.5, 0.2, 0.7], "ro-")

    # gauss = DropShadowFilter(4)

    for l in [l1, l2]:

        l.set_path_effects([StartImageEffect() | AlphaAxb((0.3, 0)) |
                            Pad(10) | Fill("k") | Dilation(3) |
                            Gaussian(3) | Offset(3, -5),
                            Normal()])

    ax.set_xlim(0., 1.)
    ax.set_ylim(0., 1.)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

class ArtistListWithPE(Artist):
    """A simple container to filter multiple artists at once."""

    def __init__(self, artist_list, pe):
        super().__init__()
        self._artist_list = artist_list
        self._pe = pe

    def draw(self, renderer):
        for a in self._artist_list:
            pe0 = a.get_path_effects()
            a.set_path_effects(self._pe)
            a.draw(renderer)
            a.set_path_effects(pe0)


def drop_shadow_patches(ax):
    # Copied from barchart_demo.py
    N = 5
    group1_means = [20, 35, 30, 35, 27]

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35  # the width of the bars

    rects1 = ax.bar(ind, group1_means, width, color='r', ec="w", lw=2)

    group2_means = [25, 32, 34, 20, 25]
    rects2 = ax.bar(ind + width + 0.1, group2_means, width,
                    color='y', ec="w", lw=2)

    al = ArtistListWithPE(rects1 + rects2,
                          [StartImageEffect() | AlphaAxb((0.5, 0)) |
                           Pad(10) | Fill("k") | Dilation(3) |
                           Gaussian(3) | Offset(-3, 3)])
    al.set_zorder(0.5)
    ax.add_artist(al)

    ax.set_ylim(0, 40)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)


def light_filter_pie(ax):
    fracs = [15, 30, 45, 10]
    explode = (0, 0.05, 0, 0)
    pies = ax.pie(fracs, explode=explode)

    light_filter = StartImageEffect() | LightSource(erosion_size=4,
                                                    gaussian_size=4)
    for p in pies[0]:
        p.set_path_effects([light_filter])

    al = ArtistListWithPE(pies[0],
                          [StartImageEffect() | AlphaAxb((0.7, 0)) |
                           Pad(10) | Fill("k") | Dilation(3) |
                           Gaussian(7) | Offset(5, -5)])
    al.set_zorder(0.5)
    ax.add_artist(al)


if True:
    # if __name__ == "__main__":

    fix, axs = plt.subplots(2, 2, num=1, clear=True)

    filtered_text(axs[0, 0])
    drop_shadow_line(axs[0, 1])
    drop_shadow_patches(axs[1, 0])
    light_filter_pie(axs[1, 1])
    axs[1, 1].set_frame_on(True)

    plt.show()
