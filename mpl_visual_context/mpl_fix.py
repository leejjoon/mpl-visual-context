import numpy as np
from matplotlib import path as mpath
from matplotlib import transforms
from matplotlib.collections import Collection


class CollectionFix(Collection):
    def get_window_extent(self, renderer=None):
        # Since we will be calling this as
        # `CollectionFix.get_window_extent(self)` where self is not an instance
        # of Collection Fix, we should avoid using `self.get_datalim`.
        return CollectionFix.get_datalim(self, transforms.IdentityTransform())

    def get_datalim(self, transData):
        # This is a fixed version Collection.get_datalim

        transform = self.get_transform()
        offset_trf = self.get_offset_transform()
        if not (
            isinstance(offset_trf, transforms.IdentityTransform)
            or offset_trf.contains_branch(transData)
            or isinstance(transData, transforms.IdentityTransform)
        ):
            # if the offsets are in some coords other than data,
            # then don't use them for autoscaling.
            return transforms.Bbox.null()
        offsets = self.get_offsets()

        paths = self.get_paths()
        if not len(paths):
            # No paths to transform
            return transforms.Bbox.null()

        if not transform.is_affine:
            paths = [transform.transform_path_non_affine(p) for p in paths]
            # Don't convert transform to transform.get_affine() here because
            # we may have transform.contains_branch(transData) but not
            # transforms.get_affine().contains_branch(transData).  But later,
            # be careful to only apply the affine part that remains.

        # if any(transform.contains_branch_seperately(transData)):
        if any(transform.contains_branch_seperately(transData)) or isinstance(
            transData, transforms.IdentityTransform
        ):
            # collections that are just in data units (like quiver)
            # can properly have the axes limits set by their shape +
            # offset.  LineCollections that have no offsets can
            # also use this algorithm (like streamplot).
            if isinstance(offsets, np.ma.MaskedArray):
                offsets = offsets.filled(np.nan)
                # get_path_collection_extents handles nan but not masked arrays
            return mpath.get_path_collection_extents(
                transform.get_affine() - transData,
                paths,
                self.get_transforms(),
                offset_trf.transform_non_affine(offsets),
                offset_trf.get_affine().frozen(),
            )

        # NOTE: None is the default case where no offsets were passed in
        if self._offsets is not None:
            # this is for collections that have their paths (shapes)
            # in physical, axes-relative, or figure-relative units
            # (i.e. like scatter). We can't uniquely set limits based on
            # those shapes, so we just set the limits based on their
            # location.
            offsets = (offset_trf - transData).transform(offsets)
            # note A-B means A B^{-1}
            offsets = np.ma.masked_invalid(offsets)
            if not offsets.mask.all():
                bbox = transforms.Bbox.null()
                bbox.update_from_data_xy(offsets)
                return bbox
        return transforms.Bbox.null()


# AxesImage.get_window_extent has a bug that it always calculates window extent
# in transData.
def image_get_window_extent(im, renderer=None):
    x0, x1, y0, y1 = im._extent
    bbox = Bbox.from_extents([x0, y0, x1, y1])
    return bbox.transformed(im.get_transform())


from numbers import Real
from mpl_toolkits.axes_grid1.axes_size import Fixed, Fraction, _Base
def from_any(size, fraction_ref=None):
    """
    Create a Fixed unit when the first argument is a float, or a
    Fraction unit if that is a string that ends with %. The second
    argument is only meaningful when Fraction unit is created.

    >>> a = Size.from_any(1.2) # => Size.Fixed(1.2)
    >>> Size.from_any("50%", a) # => Size.Fraction(0.5, a)
    """
    if isinstance(size, Real):
        return Fixed(size)
    elif isinstance(size, str):
        if size[-1] == "%":
            return Fraction(float(size[:-1]) / 100, fraction_ref)
    elif isinstance(size, _Base):
        return size

    raise ValueError("Unknown format")

def fix_axes_size():
    import mpl_toolkits.axes_grid1.axes_size

    mpl_toolkits.axes_grid1.axes_size.from_any = from_any


def _get_anchored_bbox(loc, bbox, parentbbox, borderpad):
    """
    Return the (x, y) position of the *bbox* anchored at the *parentbbox* with
    the *loc* code with the *borderpad*.
    """
    # This is only called internally and *loc* should already have been
    # validated.  If 0 (None), we just let ``bbox.anchored`` raise.
    c = [None, "NE", "NW", "SW", "SE", "E", "W", "E", "S", "N", "C"][loc]
    from collections.abc import Sequence
    if isinstance(borderpad, Sequence):
        container = parentbbox.padded(-borderpad[0], -borderpad[1])
    else:
        container = parentbbox.padded(-borderpad)
    return bbox.anchored(c, container=container).p0

from matplotlib.offsetbox import Bbox, _compat_get_offset
from matplotlib.offsetbox import AnchoredOffsetbox as _AnchoredOffsetbox

class AnchoredOffsetbox(_AnchoredOffsetbox):
    @_compat_get_offset
    def get_offset(self, bbox, renderer):
        # docstring inherited
        from collections.abc import Sequence
        s = renderer.points_to_pixels(self.prop.get_size_in_points())
        if isinstance(self.borderpad, Sequence):
            padx = self.borderpad[0] * s
            pady = self.borderpad[1] * s
        else:
            padx = pady = self.borderpad * s

        bbox_to_anchor = self.get_bbox_to_anchor()
        # x0, y0 = _get_anchored_bbox(
        #     self.loc, Bbox.from_bounds(0, 0, bbox.width, bbox.height),
        #     bbox_to_anchor, (padx, pady))
        x0, y0 = _get_anchored_bbox(
            self.loc, Bbox.from_bounds(0, 0, bbox.width, bbox.height),
            bbox_to_anchor, (padx, pady))
        return x0 - bbox.x0, y0 - bbox.y0

import matplotlib.offsetbox
matplotlib.offsetbox.AnchoredOffsetbox.get_offset = AnchoredOffsetbox.get_offset

import matplotlib.transforms as mtransforms
class BboxBase(mtransforms.BboxBase):
    def padded(self, w_pad, h_pad=None):
        """
        Construct a `Bbox` by padding this one on all four sides.

        Parameters
        ----------
        w_pad : float
            Width pad
        h_pad : float, optional
            Height pad.  Defaults to *w_pad*.

        """
        points = self.get_points()
        if h_pad is None:
            h_pad = w_pad
        return Bbox(points + [[-w_pad, -h_pad], [w_pad, h_pad]])
mtransforms.BboxBase.padded = BboxBase.padded
