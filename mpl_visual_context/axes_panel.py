from abc import ABC, abstractmethod

from matplotlib.axes._base import _AxesBase
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

from mpl_toolkits.axes_grid1.axes_size import MaxWidth, MaxHeight, Fixed
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from mpl_visual_context.axes_helper import get_axislines

from matplotlib.offsetbox import AnchoredOffsetbox
from matplotlib.offsetbox import TextArea

from .mpl_fix import fix_axes_size
fix_axes_size()


class PanelAxes_(Axes):
    def __init__(self, *kl, **kwargs):
        super().__init__(*kl, **kwargs)

        self.ax_host = None
        self.axislines = get_axislines(self)
        self.annotations = []
        # = self._get_axc_max_extent(ax, divider)

        # self.ax = axc
        # self.divider = divider

    def set_host(self, ax_host, direction):
        self.ax_host = ax_host
        self.direction = direction
        self._populate_components_from(ax_host)

    def _populate_components_from(self, ax_host):
        self.grid(False)

    # def set_extent_list(self, extent_list):
    #     self._extent_list = extent_list

    def add_annotation(self, ann, add_to_extent=True):
        # if add_to_extent:
        #     self._extent_list.append(ann)
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

    def anchor(
        self, text_or_offsetbox, loc, pad=0, borderpad=0.5, frameon=False, **kwargs
    ):
        """

        pad : padding around the offsetbox created.
        borderpad : padding between the offset box and the axes.
        """

        if isinstance(text_or_offsetbox, str):
            ob = TextArea(text_or_offsetbox, textprops=kwargs)
        else:
            ob = text_or_offsetbox

        box = AnchoredOffsetbox(
            loc, child=ob, pad=pad, borderpad=borderpad, frameon=frameon
        )
        self.add_artist(box)
        self.add_annotation(box)

    def _populate_components_from(self, ax_host):
        # FIXME can we refactor this to use axislines?
        # host_axislines = get_axislines(ax_host)
        if self.direction in ["left", "right"]:
            self.yaxis.set_tick_params(**ax_host.yaxis.get_tick_params())
        elif self.direction in ["bottom", "top"]:
            self.xaxis.set_tick_params(**ax_host.xaxis.get_tick_params())

        self.axislines[:].toggle(all=False)
        # self.grid(False)
        # self.axislines[:].toggle(all=False)


class _PanelAxesBase(PanelAxes_):
    """This has an attribute of _extent_list, which is supposed to be linked to
    the MaxWidth or MaxHeight size.

    """

    # @abstractmethod
    # def _get_axc_max_extent(self, ax, divider) -> tuple:
    #     pass

    # @abstractmethod
    # def _populate_components_from(self, ax_arent):
    #     pass

    def __init__(self, *kl, **kwargs):
        super().__init__(*kl, **kwargs)
        self._extent_list = []

        # self.ax_host = None
        # self.axislines = get_axislines(self)
        # self.annotations = []
        # self._extent_list = []
        # # = self._get_axc_max_extent(ax, divider)

        # # self.ax = axc
        # # self.divider = divider

    # def set_host(self, ax_host, direction):
    #     # self.ax_host = ax_host
    #     # self.direction = direction
    #     super().set_host(ax_host, direction)
    #     self._populate_components_from(ax_host)

    def set_extent_list(self, extent_list):
        self._extent_list = extent_list

    def add_to_extent_list(self, a):
        self._extent_list.append(a)

    def add_annotation(self, ann, add_to_extent=True):
        if add_to_extent:
            self._extent_list.append(ann)
        super().add_annotation(ann)
        # self.annotations.append(ann)

    # def annotation_set(self, **kwargs):
    #     for a in self.annotations:
    #         a.set(**kwargs)

    # def annotations_set_ha(self, ha):
    #     for a in self.annotations:
    #         a.set_ha(ha)

    # def annotations_set_va(self, va):
    #     for a in self.annotations:
    #         a.set_va(va)

    # def annotations_set_offset(self, offset):
    #     for a in self.annotations:
    #         a.xyann = offset


class PanelAxes(_PanelAxesBase):
    pass


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
            a = self.annotate(
                s.get_text(),
                loc,
                xytext=(0, 0),
                xycoords=coords,
                textcoords="offset points",
                annotation_clip=True,
            )
            a.update_from(s)
            a.set(ha="center", va="center")
            self.add_annotation(a)

        self.grid(False)


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

        a = super().annotate(
            s.get_text(),
            (0.5, 0.5),
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


def add_panel(
    divider,
    direction,
    kind,
    pad=0.0,
    size=None,
    axes_class=None,
    axes_kwargs=None,
    path_effects=None,
):
    assert kind in ["title", "label", "ticklabels", "empty"]

    if axes_kwargs is None:
        axes_kwargs = {}

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
        else:
            axes_class = PanelAxes

    if direction in ["left", "right"]:
        h_axes = divider._h_axes
        ax_host = h_axes[0] if direction == "left" else h_axes[-1]

        size1 = MaxWidth([]) if size is None else size
        axes_kwargs.update(sharey=ax_host)
        axc = divider.append_axes(
            direction, size1 + Fixed(0.2), pad=pad, axes_class=axes_class, **axes_kwargs
        )
        axc.set_xticks([])
        axis = ax_host.yaxis
    elif direction in ["bottom", "top"]:
        v_axes = divider._v_axes
        ax_host = v_axes[0] if direction == "bottom" else v_axes[-1]

        size1 = MaxHeight([]) if size is None else size
        axes_kwargs.update(sharex=ax_host)
        axc = divider.append_axes(
            direction, size1 + Fixed(0.2), pad=pad, axes_class=axes_class, **axes_kwargs
        )
        axc.set_yticks([])
        axis = ax_host.xaxis
    else:
        raise ValueError()

    if size is None:
        extent_list = size1._artist_list
        axc.set_extent_list(extent_list)

    axc.set_host(ax_host, direction)

    # FIXME We need to reorganize the logic for below and who does what. For
    # now, some are done in the panel class, some are done in here.
    axis.set_tick_params(**{f"label{direction}": False})
    # axis.set_tick_params(**{f"{direction}": False})

    if direction == "top" and kind != "title":
        axc.set_title(ax_host.get_title())
        axc.title.set_visible(ax_host.title.get_visible())
        # For now, we only update the visibility. Using "update_from" somehow
        # does not work, not sure why.
        ax_host.title.set_visible(False)

    if kind not in ["title", "empty"]:
        axis.label.set_visible(False)

    if kind == "title":
        ax_host.title.set_visible(False)

    from .patheffects import HLSModify
    from . import check_dark

    if path_effects is None:
        dl = 0.08
        if check_dark(axc.patch.get_fc()):
            # pe = HLSModifyStroke(l="-98%")
            pe = HLSModify(dl=dl)
        else:
            # pe = HLSModifyStroke(l="98%")
            pe = HLSModify(dl=-dl)
        path_effects = [pe]

    axc.patch.set_path_effects(path_effects)
    # axislines = get_axislines(axc)
    # axislines[:].line.set_visible(False)

    return axc


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


class AxesDivider:
    def __init__(self, ax):
        self._axes = ax
        self._h_axes = [ax]
        self._v_axes = [ax]
        self._divider = make_axes_locatable(ax)

    def append_axes(self, direction, size, pad=0, **kwargs):
        ax = self._divider.append_axes(direction, size, pad=pad, **kwargs)

        if direction == "left":
            ax0 = self._h_axes[0]
            self._h_axes.insert(0, ax)
        elif direction == "right":
            ax0 = self._h_axes[-1]
            self._h_axes.insert(0, ax)
        elif direction == "bottom":
            ax0 = self._v_axes[0]
            self._v_axes.insert(0, ax)
        elif direction == "top":
            ax0 = self._v_axes[-1]
            self._v_axes.append(ax)

        ax.set_zorder(ax0.get_zorder() - 1)

        return ax


class InsetDivider:
    def __init__(self, ax):
        self._axes = ax
        self._h_axes = [ax]
        self._v_axes = [ax]

    def append_axes(self, direction, size, pad=0, **kwargs):
        klass = kwargs.pop("axes_class", None)
        # axes_kwargs = kwargs.pop("axes_kwargs", None)
        # if axes_kwargs is None:
        #     axes_kwargs = {}
        # if kwargs:
        #     raise ValueError(f"unknown keyword arguments {kwargs}")
        axes_kwargs = kwargs

        if direction == "left":
            ax = self._h_axes[0]
            axes_kwargs.update(sharey=ax)
            inax = inset_axes(
                ax,
                width=size,
                height="100%",
                loc='upper right',
                axes_class=klass,
                axes_kwargs=axes_kwargs,
                bbox_to_anchor=(0, 0, 0, 1),
                bbox_transform=ax.transAxes,
                borderpad=(pad, 0),
            )
            self._h_axes.insert(0, inax)
        elif direction == "right":
            ax = self._h_axes[-1]
            axes_kwargs.update(sharey=ax)
            inax = inset_axes(
                ax,
                width=size,
                height="100%",
                loc='upper left',
                axes_class=klass,
                axes_kwargs=axes_kwargs,
                bbox_to_anchor=(1, 0, 1, 1),
                bbox_transform=ax.transAxes,
                borderpad=(pad, 0),
            )
            self._h_axes.append(inax)
        elif direction == "bottom":
            ax = self._v_axes[0]
            axes_kwargs.update(sharex=ax)
            inax = inset_axes(
                ax,
                width="100%",
                height=size,
                loc='upper right',
                axes_class=klass,
                axes_kwargs=axes_kwargs,
                bbox_to_anchor=(0, 0, 1, 0),
                bbox_transform=ax.transAxes,
                borderpad=(0, pad),
            )
            self._v_axes.insert(0, inax)
        elif direction == "top":
            ax = self._v_axes[-1]
            axes_kwargs.update(sharex=ax)
            inax = inset_axes(
                ax,
                width="100%",
                height=size,
                loc='lower left',
                axes_class=klass,
                axes_kwargs=axes_kwargs,
                bbox_to_anchor=(0, 1, 1, 1),
                bbox_transform=ax.transAxes,
                borderpad=(0, pad),
            )
            self._v_axes.append(inax)

        # We use WindowExtentProxyArtist so that tight_layout works.
        pa = WindowExtentProxyArtist(inax)
        pa.set_visible(True)
        ax.add_artist(pa)
        pa.set_in_layout(True)
        inax.set_zorder(ax.get_zorder() - 1)
        return inax


class PanelMaker:
    def __init__(self, ax, mode="inset"):
        self._ax = ax
        if mode == "inset":
            self.divider = InsetDivider(ax)
        else:
            self.divider = AxesDivider(ax)

    def add_panel(
        self,
        direction,
        kind,
        pad=0.0,
        size=None,
        axes_class=None,
        axes_kwargs=None,
        path_effects=None,
    ):
        panel = add_panel(
            self.divider,
            direction,
            kind,
            pad=pad,
            size=size,
            axes_class=axes_class,
            axes_kwargs=axes_kwargs,
            path_effects=path_effects,
        )
        return panel
