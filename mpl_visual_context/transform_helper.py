import numpy as np

from matplotlib.collections import Collection
from .mpl_fix import CollectionFix
from matplotlib.transforms import (
    Affine2D,
    Bbox,
    BboxBase,
    BboxTransformTo,
    Transform,
)
from matplotlib.artist import Artist
from matplotlib.container import Container

def _get_window_extent(s, renderer):
    bbox = s.get_window_extent(renderer)
    if not np.any(np.isfinite(bbox.get_points())) and isinstance(s, Collection):
        bbox = CollectionFix.get_window_extent(s)
    return bbox


class TR:
    """
    A helper class to make a transform silimar to how Annotation does. The
    coordinate can be:

            - One of the following strings:

              ==================== ============================================
              Value                Description
              ==================== ============================================
              'figure points'      Points from the lower left of the figure
              'figure pixels'      Pixels from the lower left of the figure
              'figure fraction'    Fraction of figure from lower left
              'subfigure points'   Points from the lower left of the subfigure
              'subfigure pixels'   Pixels from the lower left of the subfigure
              'subfigure fraction' Fraction of subfigure from lower left
              'axes points'        Points from lower left corner of axes
              'axes pixels'        Pixels from lower left corner of axes
              'axes fraction'      Fraction of axes from lower left
              'data'               Use the coordinate system of the object
                                   being annotated (default)
              ==================== ============================================

              Note that 'subfigure pixels' and 'figure pixels' are the same
              for the parent figure, so users who want code that is usable in
              a subfigure can use 'subfigure pixels'.

            - An `.Artist`: *xy* is interpreted as a fraction of the artist's
              `~matplotlib.transforms.Bbox`. E.g. *(0, 0)* would be the lower
              left corner of the bounding box and *(0.5, 1)* would be the
              center top of the bounding box.

            - A `.Transform` to transform *xy* to screen coordinates.

            - A function with one of the following signatures::

                def transform(renderer) -> Bbox
                def transform(renderer) -> Transform

              where *renderer* is a `.RendererBase` subclass.

              The result of the function is interpreted like the `.Artist` and
              `.Transform` cases above.

            - A tuple *(xcoords, ycoords)* specifying separate coordinate
              systems for *x* and *y*. *xcoords* and *ycoords* must each be
              of one of the above described types.

            See :ref:`plotting-guide-annotation` for more details.

    """

    def __init__(self):
        pass
        # self.axes = ax

    @staticmethod
    def get_xy_transform(renderer, s, axes=None):
        """
        adopted from get_xy_transform of Text.Annotate.
        """

        if isinstance(s, (list, Container)):
            # Container is subclass of Tuple, so it needs to be before the case
            # of tuple.
            bboxes = [_get_window_extent(s1, renderer) for s1 in s]
            bbox = Bbox.union(bboxes)
            return BboxTransformTo(bbox)
        elif isinstance(s, tuple):
            s1, s2 = s
            from matplotlib.transforms import blended_transform_factory

            tr1 = TR.get_xy_transform(renderer, s1, axes=axes)
            tr2 = TR.get_xy_transform(renderer, s2, axes=axes)
            tr = blended_transform_factory(tr1, tr2)
            return tr
        elif callable(s):
            tr = s(renderer)
            if isinstance(tr, BboxBase):
                return BboxTransformTo(tr)
            elif isinstance(tr, Transform):
                return tr
            else:
                raise RuntimeError("Unknown return type")
        elif isinstance(s, Artist):
            bbox = _get_window_extent(s, renderer)
            return BboxTransformTo(bbox)
        elif isinstance(s, BboxBase):
            return BboxTransformTo(s)
        elif isinstance(s, Transform):
            return s
        elif not isinstance(s, str):
            raise RuntimeError(f"Unknown coordinate type: {s!r}")

        if axes is None:
            raise ValueError("axes argument is requred.")

        figure = axes.figure

        if s == 'data':
            return axes.transData
        # elif s == 'polar':
        #     from matplotlib.projections import PolarAxes
        #     tr = PolarAxes.PolarTransform()
        #     trans = tr + self.axes.transData
        #     return trans

        s_ = s.split()
        if len(s_) != 2:
            raise ValueError(f"{s!r} is not a recognized coordinate")

        bbox0, xy0 = None, None

        bbox_name, unit = s_
        # if unit is offset-like
        if bbox_name == "figure":
            bbox0 = figure.figbbox
        elif bbox_name == "subfigure":
            bbox0 = figure.bbox
        elif bbox_name == "axes":
            bbox0 = axes.bbox
        # elif bbox_name == "bbox":
        #     if bbox is None:
        #         raise RuntimeError("bbox is specified as a coordinate but "
        #                            "never set")
        #     bbox0 = self._get_bbox(renderer, bbox)

        if bbox0 is not None:
            xy0 = bbox0.p0
        elif bbox_name == "offset":
            raise ValueError("offset is not supported")
            # xy0 = self._get_ref_xy(renderer)

        if xy0 is not None:
            # reference x, y in display coordinate
            ref_x, ref_y = xy0
            if unit == "points":
                # dots per points
                dpp = figure.dpi / 72
                tr = Affine2D().scale(dpp)
            elif unit == "pixels":
                tr = Affine2D()
            elif unit == "fontsize":
                raise ValueError("fontsize is not supported")
                # fontsize = self.get_size()
                # dpp = fontsize * igure.dpi / 72
                # tr = Affine2D().scale(dpp)
            elif unit == "fraction":
                w, h = bbox0.size
                tr = Affine2D().scale(w, h)
            else:
                raise ValueError(f"{unit!r} is not a recognized unit")

            return tr.translate(ref_x, ref_y)

        else:
            raise ValueError(f"{s!r} is not a recognized coordinate")


