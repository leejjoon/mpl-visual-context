# from matplotlib.patheffects import AbstractPathEffect
from abc import abstractmethod

class AbstractPathEffect:
    """
    A base class for path effects.

    Subclasses should override the ``draw_path`` method to add effect
    functionality.
    """

    # def __init__(self, offset=(0., 0.)):
    #     """
    #     Parameters
    #     ----------
    #     offset : (float, float), default: (0, 0)
    #         The (x, y) offset to apply to the path, measured in points.
    #     """
    #     self._offset = offset

    # def _offset_transform(self, renderer):
    #     """Apply the offset to the given transform."""
    #     return mtransforms.Affine2D().translate(
    #         *map(renderer.points_to_pixels, self._offset))

    def _update_gc(self, gc, new_gc_dict):
        """
        Update the given GraphicsContext with the given dict of properties.

        The keys in the dictionary are used to identify the appropriate
        ``set_`` method on the *gc*.
        """
        new_gc_dict = new_gc_dict.copy()

        dashes = new_gc_dict.pop("dashes", None)
        if dashes:
            gc.set_dashes(**dashes)

        for k, v in new_gc_dict.items():
            set_method = getattr(gc, 'set_' + k, None)
            if not callable(set_method):
                raise AttributeError(f'Unknown property {k}')
            set_method(v)
        return gc

    # def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
    #     """
    #     Derived should override this method. The arguments are the same
    #     as :meth:`matplotlib.backend_bases.RendererBase.draw_path`
    #     except the first argument is a renderer.
    #     """
    #     # Get the real renderer, not a PathEffectRenderer.
    #     if isinstance(renderer, PathEffectRenderer):
    #         renderer = renderer._renderer
    #     return renderer.draw_path(gc, tpath, affine, rgbFace)


class ChainablePathEffect(AbstractPathEffect):
    def __or__(self, other):
        if isinstance(other, PathEffectTerminated):
            return PathEffectTerminated(self, other)
        elif isinstance(other, ChainablePathEffect):
            return ChainedPathEffect(self, other)
        else:
            return PathEffectTerminated(self, other)

    @abstractmethod
    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        return renderer, gc, tpath, affine, rgbFace

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        renderer, gc, tpath, affine, rgbFace = self._convert(
            renderer, gc, tpath, affine, rgbFace
        )
        if renderer is not None:
            renderer.draw_path(gc, tpath, affine, rgbFace)

from typing import List

class ChainedPathEffect(ChainablePathEffect):
    def __init__(self, pe1: ChainablePathEffect, pe2: ChainablePathEffect):
        if isinstance(pe1, ChainedPathEffect):
            pe1l = pe1._pe_list
        else:
            pe1l = [pe1]
            # self._pe_list = pe1._pe_list + [pe2]
        if isinstance(pe2, ChainedPathEffect):
            pe2l = pe2._pe_list
            # self._pe_list = [pe1] + pe2._pe_list
        else:
            pe2l = [pe2]

        self._pe_list = pe1l + pe2l

    @classmethod
    def from_pe_list(cls, pe_list: List[ChainablePathEffect]):
        self = cls.__new__(cls)
        self._pe_list = pe_list
        return self

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        for pe in self._pe_list:
            renderer, gc, tpath, affine, rgbFace = pe._convert(
                renderer, gc, tpath, affine, rgbFace
            )
        return renderer, gc, tpath, affine, rgbFace

    def __repr__(self):
        s = " | ".join([repr(pe) for pe in self._pe_list])
        return "ChainedStroke({})".format(s)


class PathEffectTerminated(AbstractPathEffect):
    """
    Chained Patheffect that no longer can be chained, because the last patheffect is not chainable.
    """

    def __init__(self, pe1: ChainablePathEffect, pe2: AbstractPathEffect):
        self._pe_list = []
        if isinstance(pe1, ChainedPathEffect):
            self._pe_list.extend(pe1._pe_list)
        else:
            self._pe_list.append(pe1)

        if isinstance(pe2, PathEffectTerminated):
            self._pe_list.extend(pe2._pe_list)
            pe_final = pe2._pe_final
        else:
            pe_final = pe2

        self._pe_final = pe_final

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        for pe in self._pe_list:
            renderer, gc, tpath, affine, rgbFace = pe._convert(
                renderer, gc, tpath, affine, rgbFace
            )
        return renderer, gc, tpath, affine, rgbFace

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        renderer, gc, tpath, affine, rgbFace = self._convert(
            renderer, gc, tpath, affine, rgbFace
        )
        self._pe_final.draw_path(renderer, gc, tpath, affine, rgbFace)

    def __repr__(self):
        s = " | ".join([repr(pe) for pe in self._pe_list])
        return "PathEffectTerminated({}, {})".format(s, self._pe_final)


class GCModify(ChainablePathEffect):
    def __init__(self, **kwargs):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self._gc = kwargs

    def _convert(self, renderer, gc, tpath, affine, rgbFace):
        gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
        gc0.copy_properties(gc)
        gc0 = self._update_gc(gc0, self._gc)

        return renderer, gc0, tpath, affine, rgbFace


# Clipbaord is experimental.

class ClipboardBase:
    ATTR_NAMES = ["renderer", "gc", "tpath", "affine", "rgbFace"]

class Clipboard(ClipboardBase, dict):


    def __init__(self, renderer=False, gc=True, tpath=True, affine=True, rgbFace=True):
        _ = dict(renderer=renderer, gc=gc, tpath=tpath, affine=affine,
                 rgbFace=rgbFace)
        self.attr_to_store = set(k for k in self.ATTR_NAMES if _.get(k, False))

    def copy(self):
        return CopyToClipboard(self)

    def paste(self):
        return PasteFromClipboard(self)


class CopyToClipboard(ChainablePathEffect):
    def __init__(self, clipboard):
        """
        clipboard : Clipboard
        """
        self.clipboard = clipboard

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        _ = dict(renderer=renderer, gc=gc, tpath=tpath, affine=affine,
                 rgbFace=rgbFace)
        for k in self.clipboard.attr_to_store:
            if k == "affine":
                self.clipboard[k] = _[k]
            else:
                self.clipboard[k] = _[k]

        return renderer, gc, tpath, affine, rgbFace


class PasteFromClipboard(ChainablePathEffect):
    def __init__(self, clipboard):
        """
        clipboard : Clipboard
        """
        self.clipboard = clipboard

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        _ = dict(renderer=renderer, gc=gc, tpath=tpath, affine=affine,
                 rgbFace=rgbFace)
        r = tuple(self.clipboard.get(k, _[k]) for k in self.clipboard.ATTR_NAMES)
        # self.clipboard.clear()
        return r

class PasteFrom(ChainablePathEffect, ClipboardBase):
    def __init__(self, clipboard):
        """
        clipboard : dict-like
        """
        self.clipboard = clipboard

    def _convert(self, renderer, gc, tpath, affine, rgbFace=None):
        _ = dict(renderer=renderer, gc=gc, tpath=tpath, affine=affine,
                 rgbFace=rgbFace)
        r = tuple(self.clipboard.get(k, _[k]) for k in self.ATTR_NAMES)
        # self.clipboard.clear()
        return r
