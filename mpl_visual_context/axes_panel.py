from abc import ABC, abstractmethod

from matplotlib.axes._base import _AxesBase
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

from mpl_toolkits.axes_grid1.axes_size import MaxWidth, MaxHeight, Fixed
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from mpl_visual_context.axes_helper import get_axislines


class _PanelAxesBase(Axes):
    @abstractmethod
    def _get_axc_max_extent(self, ax, divider) -> tuple:
        pass

    @abstractmethod
    def _populate_components_from(self, ax_arent):
        pass


    def __init__(self, *kl, **kwargs):
        super().__init__(*kl, **kwargs)

        self.ax_host = None
        self.axislines = get_axislines(self)
        self.annotations = []
        self._extent_list = None
        # = self._get_axc_max_extent(ax, divider)

        # self.ax = axc
        # self.divider = divider

    def set_host(self, ax_host, direction):
        self.ax_host = ax_host
        self.direction = direction
        self._populate_components_from(ax_host)

    def set_extent_list(self, extent_list):
        self._extent_list = extent_list

    def add_annotation(self, ann, add_to_extent=True):
        if add_to_extent:
            self._extent_list.append(ann)
        self.annotations.append(ann)

    def annotation_set(self, **kwargs):
        for a in self.annotations:
            a.set(**kwargs)

    def annotations_set_ha(self, ha):
        for a in self.annotations:
            a.set_ha(ha)

    def annotations_set_va(self, va):
        for a in self.annotations:
            a.set_va(va)

    def annotations_set_offset(self, offset):
        for a in self.annotations:
            a.xyann = offset

# FIXME For now, TickLabelPanel have annotations associated with ticklabels,
# frozen at the creation time. It would be good if this is somehow synced with
# the host axes.
class _TickLabelPanelAxesBase(_PanelAxesBase):
    @abstractmethod
    def _get_tick_locs_labels(self, ax_host) -> tuple:
        pass

    def _populate_components_from(self, ax_host):
        ticklocs, coords, ticklabels = self._get_tick_locs_labels(ax_host)

        for loc, s in zip(ticklocs, ticklabels):
            a = self.annotate(s.get_text(), loc,
                              xytext=(0, 0),
                              xycoords=coords,
                              textcoords="offset points",
                              annotation_clip=True,
                              )
            a.update_from(s)
            a.set(ha="center", va="center")
            self.add_annotation(a)


class YTickLabelPanelAxes(_TickLabelPanelAxesBase):
    def _get_tick_locs_labels(self, ax_host):
        ticklocs = [(0.5, l) for l in ax_host.yaxis.get_ticklocs()]
        ticklabels = [t for t in ax_host.yaxis.get_ticklabels()]
        coords = ("axes fraction", "data")
        return ticklocs, coords, ticklabels

    def _populate_components_from(self, ax_host):
        super()._populate_components_from(ax_host)

        self.set_ylabel(ax_host.get_ylabel())
        self.axislines[:].toggle(all=False)
        if ax_host.yaxis.label.get_visible():
            self.axislines[self.direction].toggle(label=True)

    def set_xpos(self, pos):
        for a in self.annotations:
            a.xy = (pos, a.xy[-1])


class XTickLabelPanelAxes(_TickLabelPanelAxesBase):
    def _get_tick_locs_labels(self, ax_host):
        ticklocs = [(l, 0.5) for l in ax_host.xaxis.get_ticklocs()]
        coords = ("data", "axes fraction")
        ticklabels = [t for t in ax_host.xaxis.get_ticklabels()]

        return ticklocs, coords, ticklabels

    def _populate_components_from(self, ax_host):
        super()._populate_components_from(ax_host)

        self.set_xlabel(ax_host.get_xlabel())
        self.axislines[:].toggle(all=False)
        self.axislines[self.direction].toggle(label=True)

    def set_ypos(self, pos):
        for a in self.annotations:
            a.xy = (a.xy[0], pos)



class _LabelPanelAxesBase(_PanelAxesBase):
    # @abstractmethod
    # def _get_tick_locs_labels(self) -> tuple:
    #     pass

    @abstractmethod
    def _get_main_label(self, ax_host) -> str:
        pass

    def _populate_components_from(self, ax_host):
        s = self._get_main_label(ax_host)

        a = super().annotate(s.get_text(), (0.5, 0.5),
                             xytext=(0, 0),
                             # ha="center", va="bottom",
                             xycoords="axes fraction",
                             textcoords="offset points",
                             annotation_clip=True,
                             )
        a.update_from(s)
        a.set(ha="center", va="center")

        self.add_annotation(a)

        # FIXME can we refactor this to use axislines?
        # host_axislines = get_axislines(ax_host)
        if self.direction in ["left", "right"]:
            self.yaxis.set_tick_params(**ax_host.yaxis.get_tick_params())
        elif self.direction in ["bottom", "top"]:
            self.xaxis.set_tick_params(**ax_host.xaxis.get_tick_params())

        self.grid(False)
        # self.axislines[:].toggle(all=False)

    def annotate(self, s, *kl, **kwargs):

        kwargs["xycoords"] = "axes fraction"
        kwargs["textcoords"] = "offset points"
        kwargs["annotation_clip"] = True
        a = super().annotate(s, *kl, **kwargs)

        self.add_annotation(a, add_to_extent=False)


class XLabelPanelAxes(_LabelPanelAxesBase):

    def _get_main_label(self, ax_host):
        s = ax_host.xaxis.label
        return s


class YLabelPanelAxes(_LabelPanelAxesBase):

    def _get_main_label(self, ax_host):
        s = ax_host.yaxis.label
        return s


class TitlePanelAxes(_LabelPanelAxesBase):

    def _get_main_label(self, ax_host):
        s = ax_host.title
        return s



##
##
##

def add_panel(divider, direction, kind,
              pad=0.,
              axes_class=None):
    assert kind in ["title", "label", "ticklabels"]

    if axes_class is None and kind is not None:
        if kind == "ticklabels":
            if direction in ["left", "right"]:
                axes_class = YTickLabelPanelAxes
            else:
                axes_class = XTickLabelPanelAxes
        elif kind == "label":
            if direction in ["left", "right"]:
                axes_class = YLabelPanelAxes
            else:
                axes_class = XLabelPanelAxes
        elif kind == "title":
            axes_class = TitlePanelAxes

    if direction in ["left", "right"]:
        h_axes = divider._h_axes
        ax_host = h_axes[0] if direction == "left" else h_axes[-1]

        max_width = MaxWidth([])
        axc = divider.append_axes(direction, max_width + Fixed(0.2),
                                  pad=pad, sharey=ax_host,
                                  axes_class=axes_class)
        extent_list = max_width._artist_list
        axc.set_xticks([])
        axis = ax_host.yaxis
    elif direction in ["bottom", "top"]:
        v_axes = divider._v_axes
        ax_host = v_axes[0] if direction == "bottom" else v_axes[-1]

        max_height = MaxHeight([])
        axc = divider.append_axes(direction, max_height + Fixed(0.2),
                                  pad=pad, sharex=ax_host,
                                  axes_class=axes_class)
        extent_list = max_height._artist_list
        axc.set_yticks([])
        axis = ax_host.xaxis
    else:
        raise ValueError()

    axc.set_extent_list(extent_list)
    axc.set_host(ax_host, direction)

    axis.set_tick_params(**{f"label{direction}": False})
    axis.set_tick_params(**{f"{direction}": False})
    axis.label.set_visible(False)

    if kind == "title":
        ax_host.title.set_visible(False)

    return axc


# class XTickLabelPanel(_TickLabelPanelBase):
#     def _get_axc_max_extent(self, ax, divider):
#         max_height = MaxHeight([])
#         axc = divider.append_axes("bottom", max_height + Fixed(0.2),
#                                   pad=self.pad, sharex=ax)
#         axc.set_yticks([])

#         return axc, max_height

#     def _get_tick_locs_labels(self):
#         ax = self.ax_orig
#         ticklocs = [(l, 0.5) for l in ax.xaxis.get_ticklocs()]
#         coords = ("data", "axes fraction")
#         ticklabels = [t for t in ax.xaxis.get_ticklabels()]

#         return ticklocs, coords, ticklabels

#     def set_ypos(self, pos):
#         for a in self.annotations:
#             a.xy = (a.xy[0], pos)


class _PanelBase(ABC):
    @abstractmethod
    def _get_axc_max_extent(self, ax, divider) -> tuple:
        pass

    @abstractmethod
    def _populate_components(self, axc, max_extent):
        pass


    def __init__(self, ax, divider, pad=0.5):
        self.ax_orig = ax
        self.annotations = []
        self.pad = pad
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
            a = axc.annotate(s.get_text(), loc,
                             xytext=(0, 0),
                             xycoords=coords,
                             textcoords="offset points",
                             annotation_clip=True,
                             )
            a.update_from(s)
            a.set(ha="center", va="center")
            max_extent.add_artist(a)
            self.annotations.append(a)


class YTickLabelPanel(_TickLabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_width = MaxWidth([])
        axc = divider.append_axes("left", max_width + Fixed(0.2),
                                  pad=self.pad, sharey=ax)
        axc.set_xticks([])

        return axc, max_width

    def _get_tick_locs_labels(self):
        ax = self.ax_orig
        ticklocs = [(0.5, l) for l in ax.yaxis.get_ticklocs()]
        ticklabels = [t for t in ax.yaxis.get_ticklabels()]
        coords = ("axes fraction", "data")
        return ticklocs, coords, ticklabels

    def set_xpos(self, pos):
        for a in self.annotations:
            a.xy = (pos, a.xy[-1])


class XTickLabelPanel(_TickLabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_height = MaxHeight([])
        axc = divider.append_axes("bottom", max_height + Fixed(0.2),
                                  pad=self.pad, sharex=ax)
        axc.set_yticks([])

        return axc, max_height

    def _get_tick_locs_labels(self):
        ax = self.ax_orig
        ticklocs = [(l, 0.5) for l in ax.xaxis.get_ticklocs()]
        coords = ("data", "axes fraction")
        ticklabels = [t for t in ax.xaxis.get_ticklabels()]

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

        a = axc.annotate(s.get_text(), (0.5, 0.5),
                         xytext=(0, 0),
                         # ha="center", va="bottom",
                         xycoords="axes fraction",
                         textcoords="offset points",
                         annotation_clip=True,
                         )
        a.update_from(s)
        a.set(ha="center", va="center")

        max_extent.add_artist(a)
        self.annotations.append(a)

    def annotate(self, s, *kl, **kwargs):
        # s = self._get_main_label()

        kwargs["xycoords"] = "axes fraction"
        kwargs["textcoords"] = "offset points"
        kwargs["annotation_clip"] = True
        a = self.ax.annotate(s, *kl, **kwargs)

        # a.set(ha="center", va="center")

        # max_extent.add_artist(a)
        self.annotations.append(a)


class XLabelPanel(_LabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_height = MaxHeight([])
        axc = divider.append_axes("bottom", max_height + Fixed(0.2),
                                  pad=self.pad, sharex=ax)
        axc.grid(False)

        return axc, max_height

    def _get_main_label(self):
        s = self.ax_orig.xaxis.label
        return s


class YLabelPanel(_LabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_width = MaxWidth([])
        axc = divider.append_axes("left", max_width + Fixed(0.2),
                                  pad=self.pad, sharex=ax)
        axc.grid(False)

        return axc, max_width

    def _get_main_label(self):
        s = self.ax_orig.yaxis.label
        return s


class TitlePanel(_LabelPanelBase):
    def _get_axc_max_extent(self, ax, divider):
        max_height = MaxHeight([])
        axc = divider.append_axes("top", max_height + Fixed(0.2),
                                  pad=self.pad)
        axc.grid(False)

        return axc, max_height

    def _get_main_label(self):
        s = self.ax_orig.title
        return s


def axis_to_panels(divider, axis="both", which=None, pad=0.):
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
                    panels[f"{axisname}-ticklabels"] = klass(ax,
                                                             divider, pad)
                    axis.set_tick_params(**{f"label{dir}": False})
                if ( "label" in w
                     and axis.label.get_visible()
                     and axis.label.get_text()):
                    klass = dict(x=XLabelPanel, y=YLabelPanel)[axisname]
                    panels[f"{axisname}-label"] = klass(ax,
                                                        divider, pad)
                    axis.label.set_visible(False)

    for k, panel in panels.items():
        # panel.axislines[:].spine.set_visible(False)
        panel.axislines[:].toggle(all=False)

    return panels


def title_to_panel(divider, pad=0.):
    ax = divider._axes

    panels = {}
    title = ax.title
    if title.get_visible() and title.get_text():
        panels["title"] = TitlePanel(ax, divider, pad=pad)
        title.set_visible(False)

    for k, panel in panels.items():
        panel.axislines[:].toggle(all=False)

    return panels


# WindowExtentProxyArtist is derived from _AxesBase so that it is picked up by
# the Axes.get_default_bbox_extra_artists.

class WindowExtentProxyArtist(_AxesBase):
    def __init__(self, ax):
        super().__init__(ax.figure, [0, 0, 0, 0])
        self._axes = None
        self._proxy_artist = ax

    def get_window_extent(self, renderer):
        return self._proxy_artist.get_window_extent(renderer=renderer)

    def get_tightbbox(self, renderer):
        return self._proxy_artist.get_tightbbox(renderer=renderer)

    def draw(self, renderer):
        pass


class AxesDivider():
    def __init__(self, ax):
        self._axes = ax
        self._h_axes = [ax]
        self._v_axes = [ax]
        self._divider = make_axes_locatable(ax)

    def append_axes(self, direction, size, pad=0, **kwargs):
        ax = self._divider.append_axes(direction, size, pad=pad, **kwargs)

        if direction == "left":
            self._h_axes.insert(0, ax)
        elif direction == "right":
            self._h_axes.insert(0, ax)
        elif direction == "bottom":
            self._v_axes.insert(0, ax)
        elif direction == "top":
            self._v_axes.append(ax)

        return ax


class InsetDivider():
    def __init__(self, ax):
        self._axes = ax
        self._h_axes = [ax]
        self._v_axes = [ax]

    def append_axes(self, direction, size, pad=0, **kwargs):
        klass = kwargs.pop("axes_class", None)
        if direction == "left":
            ax = self._h_axes[0]
            inax = inset_axes(ax,
                              width=size,
                              height="100%",
                              loc='upper right',
                              axes_kwargs=dict(sharey=ax),
                              axes_class=klass,
                              bbox_to_anchor=(0, 0, 0, 1),
                              bbox_transform=ax.transAxes,
                              borderpad=(pad, 0))
            self._h_axes.insert(0, inax)
        elif direction == "right":
            ax = self._h_axes[-1]
            inax = inset_axes(ax,
                              width=size,
                              height="100%",
                              loc='upper left',
                              axes_kwargs=dict(sharey=ax),
                              axes_class=klass,
                              bbox_to_anchor=(1, 0, 1, 1),
                              bbox_transform=ax.transAxes,
                              borderpad=(pad, 0))
            self._h_axes.append(inax)
        elif direction == "bottom":
            ax = self._v_axes[0]
            inax = inset_axes(ax,
                              width="100%",
                              height=size,
                              loc='upper right',
                              axes_kwargs=dict(sharex=ax),
                              axes_class=klass,
                              bbox_to_anchor=(0, 0, 1, 0),
                              bbox_transform=ax.transAxes,
                              borderpad=(0, pad))
            self._v_axes.insert(0, inax)
        elif direction == "top":
            ax = self._v_axes[-1]
            inax = inset_axes(ax,
                              width="100%",
                              height=size,
                              loc='lower left',
                              axes_kwargs=dict(sharex=ax),
                              axes_class=klass,
                              bbox_to_anchor=(0, 1, 1, 1),
                              bbox_transform=ax.transAxes,
                              borderpad=(0, pad))
            self._v_axes.append(inax)

        # We use WindowExtentProxyArtist so that tight_layout works.
        pa = WindowExtentProxyArtist(inax)
        pa.set_visible(True)
        ax.add_artist(pa)
        pa.set_in_layout(True)

        return inax
