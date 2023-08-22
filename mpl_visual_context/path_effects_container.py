from matplotlib.patheffects import Normal

# from .color_matrix import ColorMatrixStroke as CMS
# from .patheffects import HLSModifyStroke
# from mpl_visual_context.patheffects import ColorMatrixStroke as CMS
# from mpl_visual_context.patheffects import HLSModifyStroke

# class PathEffectsRegistry():
#     def __init__(self):
#         self._registered = {}

#     def register(self, name, pe_list):
#         self._registered[name] = pe_list


class PathEffectsContainer:
    _normal = [Normal()]

    def __init__(self, registry: dict):
        self._registry = registry
        self._current_name = None

    def use(self, name):
        self._current_name = name

    def __iter__(self):
        if self._current_name is None:
            return iter(self._normal)
        else:
            return iter(self._registry[self._current_name])


def _example():
    # from mpl_visual_context.patheffects import ColorMatrixStroke as CMS
    # from mpl_visual_context.patheffects import HLSModifyStroke
    registry = dict(
        grayscale=[],
        sepia=[],
        warm=[],
        cool=[],
        bright=[HLSModifyStroke(l="-50%")],
        bright_gray=[HLSModifyStroke(l="-50%") | CMS("grayscale")],
    )
    pec = PathEffectsContainer(registry)
    pec.use("bright")


# class ColorModifyStroke(AbstractPathEffect):
#     pass
