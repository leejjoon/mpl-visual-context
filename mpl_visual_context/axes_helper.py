"""
Helper class to tweak the visibility of various axes components.

"""
# Let's have a anoatomy of matplotlib guide this class.

"""
Axes
    axis: left, right, ..
      - ticks
         - major
         - minor
      - ticklabels
      - grid
      - spine
      - label
    title
    legend
title
legend
"""

from mpl_toolkits.axes_grid1.mpl_axes import (
    Axes as _Axes,
    SimpleAxisArtist as _SimpleAxisArtist,
)


class SimpleAxisArtist(_SimpleAxisArtist):
    def __init__(self, axis, axisnum, spine):
        super().__init__(axis, axisnum, spine)
        self.spine = self.line


def get_axislines(ax):
    axislines = _Axes.AxisDict(ax)
    axislines.update(
        bottom=SimpleAxisArtist(ax.xaxis, 1, ax.spines["bottom"]),
        top=SimpleAxisArtist(ax.xaxis, 2, ax.spines["top"]),
        left=SimpleAxisArtist(ax.yaxis, 1, ax.spines["left"]),
        right=SimpleAxisArtist(ax.yaxis, 2, ax.spines["right"]),
    )

    return axislines
