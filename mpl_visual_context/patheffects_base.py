from matplotlib.patheffects import AbstractPathEffect
from abc import abstractmethod


class ChainablePathEffect(AbstractPathEffect):
    def __or__(self, other):
        if isinstance(other, ChainablePathEffect):
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
        renderer.draw_path(gc, tpath, affine, rgbFace)


class ChainedPathEffect(ChainablePathEffect):
    def __init__(self, pe1: ChainablePathEffect, pe2: ChainablePathEffect):
        if isinstance(pe1, ChainedPathEffect):
            self._pe_list = pe1._pe_list + [pe2]
        else:
            self._pe_list = [pe1, pe2]

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
        if isinstance(pe1, ChainedPathEffect):
            self._pe_list = pe1._pe_list
        else:
            self._pe_list = [pe1]

        self._pe_final = pe2

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
