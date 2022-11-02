from matplotlib.patheffects import AbstractPathEffect

from .pe_colors import HLSModifier

class ColorModifyStroke(AbstractPathEffect):
    """A line based PathEffect which re-draws a stroke."""

    def __init__(self, h="100%", l="100%", s="100%", alpha="100%",
                 dh=0, dl=0, ds=0, dalpha=0):
        """
        The path will be stroked with its gc updated with the given
        keyword arguments, i.e., the keyword arguments should be valid
        gc parameter values.
        """
        super().__init__()
        self._modifier = HLSModifier(h, l, s, alpha, dh, dl, ds, dalpha)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):
        """Draw the path with updated gc."""
        gc0 = renderer.new_gc()
        gc0.copy_properties(gc)

        # change the stroke color
        rgb = self._modifier.apply_to_color(gc0.get_rgb())
        gc0.set_foreground(rgb)

        # chage the fill color
        if rgbFace is not None:
            rgbFace = self._modifier.apply_to_color(rgbFace)
        renderer.draw_path(
            gc0, tpath, affine, rgbFace)


def main():
    import matplotlib.pyplot as plt
    import seaborn as sns
    df_peng = sns.load_dataset("penguins")

    fig, ax = plt.subplots(figsize=(5, 3), constrained_layout=True, clear=True)
    sns.countplot(y="species", data=df_peng, ax=ax)

    pe = [ColorModifyStroke(l = "-50%", s="100%")]

    p = ax.patches[0]
    p.set_ec("k")
    p.set_path_effects(pe)
    p = ax.patches[1]
    p.set_ec("k")
    p = ax.patches[2]
    p.set_path_effects(pe)

    plt.show()

if __name__ == '__main__':
    main()
