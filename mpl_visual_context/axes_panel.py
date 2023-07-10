from abc import ABC, abstractmethod

from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.axes_size import MaxWidth, MaxHeight, Fixed

from mpl_visual_context.axes_helper import get_axislines


class _PanelBase(ABC):
    @abstractmethod
    def _get_axc_max_extent(self, ax, divider) -> tuple:
        pass

    @abstractmethod
    def _populate_components(self, axc, max_extent):
        pass


    def __init__(self, ax, divider=None):
        self.ax_orig = ax
        self.annotations = []

        if divider is None:
            divider = make_axes_locatable(ax)

        # FIXME For now, the new axes will be on the left side.

        axc, max_extent = self._get_axc_max_extent(ax, divider)

        self.axislines = get_axislines(axc)

        self._populate_components(axc, max_extent)

        self.ax = axc
        self.divider = divider

    def set_ha(self, ha):
        for a in self.annotations:
            a.set_ha(ha)

    def set_va(self, va):
        for a in self.annotations:
            a.set_va(va)

    def set_offset(self, offset):
        for a in self.annotations:
            a.xyann = offset


class _TickLabelPanelBase(_PanelBase):
    @abstractmethod
    def _get_tick_locs_labels(self) -> tuple:
        pass

    def _populate_components(self, axc, max_extent):
        ticklocs, coords, ticklabels = self._get_tick_locs_labels()

        for loc, s in zip(ticklocs, ticklabels):
            a = axc.annotate(s, loc,
                             xytext=(0, 0),
                             # ha="center", va="bottom",
                             ha="center", va="center",
                             xycoords=coords,
                             textcoords="offset points",
                             fontsize="large",
                             # color="w",
                             # fontdict={"fontsize":"large"},
                             annotation_clip=True,
                             )
            max_extent.add_artist(a)
            self.annotations.append(a)


class YTickLabelPanel(_TickLabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_width = MaxWidth([])
        axc = divider.append_axes("left", max_width + Fixed(0.2),
                                  pad=0, sharey=ax)
        axc.set_xticks([])

        return axc, max_width

    def _get_tick_locs_labels(self):
        ax = self.ax_orig
        ticklocs = [(0.5, l) for l in ax.yaxis.get_ticklocs()]
        ticklabels = [t.get_text() for t in ax.yaxis.get_ticklabels()]
        coords = ("axes fraction", "data")
        return ticklocs, coords, ticklabels

    def set_xpos(self, pos):
        for a in self.annotations:
            a.xy = (pos, a.xy[-1])

class XTickLabelPanel(_TickLabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_height = MaxHeight([])
        axc = divider.append_axes("bottom", max_height + Fixed(0.2),
                                  pad=0, sharex=ax)
        axc.set_yticks([])

        return axc, max_height

    def _get_tick_locs_labels(self):
        ax = self.ax_orig
        ticklocs = [(l, 0.5) for l in ax.xaxis.get_ticklocs()]
        coords = ("data", "axes fraction")
        ticklabels = [t.get_text() for t in ax.xaxis.get_ticklabels()]

        return ticklocs, coords, ticklabels

    def set_ypos(self, pos):
        for a in self.annotations:
            a.xy = (a.xy[0], pos)


class _LabelPanelBase(_PanelBase):
    # @abstractmethod
    # def _get_tick_locs_labels(self) -> tuple:
    #     pass

    @abstractmethod
    def _get_main_label(self) -> str:
        pass

    def _populate_components(self, axc, max_extent):
        s = self._get_main_label()

        a = axc.annotate(s, (0.5, 0.5),
                         xytext=(0, 0),
                         # ha="center", va="bottom",
                         ha="center", va="center",
                         xycoords="axes fraction",
                         textcoords="offset points",
                         fontsize="large",
                         # color="w",
                         # fontdict={"fontsize":"large"},
                         annotation_clip=True,
                         )

        max_extent.add_artist(a)
        self.annotations.append(a)


class XLabelPanel(_LabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_height = MaxHeight([])
        axc = divider.append_axes("bottom", max_height + Fixed(0.2),
                                  pad=0., sharex=ax)
        axc.grid(False)

        return axc, max_height

    def _get_main_label(self):
        s = self.ax_orig.get_xlabel()
        return s


class YLabelPanel(_LabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_width = MaxWidth([])
        axc = divider.append_axes("left", max_width + Fixed(0.2),
                                  pad=0., sharex=ax)
        axc.grid(False)

        return axc, max_width

    def _get_main_label(self):
        s = self.ax_orig.get_ylabel()
        return s


def axis_to_panels(divider, axis="both", which=None):
    if axis not in ["x", "y", "both"]:
        raise ValueError()

    axis_to_convert = axis
    if which is None:
        which = ["ticks", "label"]

    ax = divider._axes

    if axis_to_convert == "x":
        _axis = [("x", ax.xaxis)]
    elif axis_to_convert == "y":
        _axis = [("y", ax.yaxis)]
    else:
        _axis = [("x", ax.xaxis),
                 ("y", ax.yaxis)]

    panels = {}
    for axisname, axis in _axis:
        if axis.get_visible():
            dir = dict(x="bottom", y="left")[axisname]
            ticklabels = axis.get_ticklabels()
            for w in which:
                if ( "ticks" in w
                     and ticklabels
                     and any([t.get_visible() for t in ticklabels]) ):
                    klass = dict(x=XTickLabelPanel, y=YTickLabelPanel)[axisname]
                    panels[f"{axisname}-ticklabels"] = klass(ax, divider=divider)
                    axis.set_tick_params(**{f"label{dir}": False})
                if ( "label" in w
                     and axis.label.get_visible()
                     and axis.label.get_text()):
                    klass = dict(x=XLabelPanel, y=YLabelPanel)[axisname]
                    panels[f"{axisname}-label"] = klass(ax, divider=divider)
                    axis.label.set_visible(False)

    for k, panel in panels.items():
        panel.axislines[:].spine.set_visible(False)
        panel.axislines[:].toggle(all=False)

    return panels
