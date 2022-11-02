from matplotlib import patches as mpatches
from matplotlib.patheffects import AbstractPathEffect

import numpy as np
import matplotlib.colors as mcolors
import colorsys

def set_hls(c, dh=0, dl=0, ds=0, dalpha=0):
    """
    c : (array -like, str) color in RGB space
    dh : (float) change in Hue
        default = 0
    dl : (float) change in Lightness
        default = 0
    ds : (float) change in Saturation
        default = 0
    """
    c_rgba = mcolors.to_rgba(c)

    c_rgb = c_rgba[:3]
    alpha = c_rgba[3]

    c_hls = colorsys.rgb_to_hls(*c_rgb)
    h = c_hls[0] + dh
    l = np.clip(c_hls[1] + dl, 0, 1)
    s = np.clip(c_hls[2] + ds, 0, 1)

    c_rgb_new = colorsys.hls_to_rgb(h, l, s)
    alpha = np.clip(alpha+dalpha, 0, 1)

    return np.append(c_rgb_new, alpha)


class PathPatchEffect(AbstractPathEffect):
    """
    Draws a `.PathPatch` instance whose Path comes from the original
    PathEffect artist.
    """

    def __init__(self, offset=(0, 0), **kwargs):
        """
        Parameters
        ----------
        offset : (float, float), default: (0, 0)
            The (x, y) offset to apply to the path, in points.
        **kwargs
            All keyword arguments are passed through to the
            :class:`~matplotlib.patches.PathPatch` constructor. The
            properties which cannot be overridden are "path", "clip_box"
            "transform" and "clip_path".
        """
        super().__init__(offset=offset)
        self.patch = mpatches.PathPatch([], **kwargs)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        self.patch._path = tpath
        self.patch.set_transform(affine + self._offset_transform(renderer))
        self.patch.set_clip_box(gc.get_clip_rectangle())
        clip_path = gc.get_clip_path()
        if clip_path:
            self.patch.set_clip_path(*clip_path)
        self.patch.draw(renderer)


class Stroke(AbstractPathEffect):
    """A line based PathEffect which re-draws a stroke."""

    def __init__(self, offset=(0, 0), **kwargs):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__(offset)
        self._gc = kwargs

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()  # Don't modify gc, but a copy!
        gc0.copy_properties(gc)
        gc0 = self._update_gc(gc0, self._gc)
        renderer.draw_path(
            gc0, tpath, affine + self._offset_transform(renderer), rgbFace)
        gc0.restore()

class ColorModifyStroke(AbstractPathEffect):
    """A line based PathEffect which re-draws a stroke."""

    def __init__(self, dh=0, dl=0, ds=0, dalpha=0):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self.dh = dh
        self.dl = dl
        self.ds = ds
        self.dalpha = dalpha

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        # change the stroke color
        rgb = set_hls(gc0.get_rgb(), self.dh, self.dl, self.ds)
        gc0.set_foreground(rgb)

        # chage the fill color
        if rgbFace is not None:
            rgbFace = set_hls(rgbFace, self.dh, self.dl, self.ds)
        renderer.draw_path(
            gc0, tpath, affine, rgbFace)
        # gc0.restore()


def main():
    import matplotlib.pyplot as plt
    import seaborn as sns
    df_peng = sns.load_dataset("penguins")

    fig, ax = plt.subplots(figsize=(5, 3), constrained_layout=True, clear=True)
    sns.countplot(y="species", data=df_peng, ax=ax)

    pe = [ColorModifyStroke(ds=-0.2, dl=0.4)]

    p = ax.patches[0]
    p.set_ec("k")
    p.set_path_effects(pe)
    p = ax.patches[1]
    p.set_ec("k")
    p = ax.patches[2]
    p.set_path_effects(pe)
