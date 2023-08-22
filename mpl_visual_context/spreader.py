import matplotlib.transforms as mtransforms


def spready(artists, yindices, dy=None):
    n = len(artists)
    if dy is None:
        dy = 1.0
    yoffsets = yindices * dy
    for y, a in zip(yoffsets, artists):
        tr = mtransforms.Affine2D().translate(0, y) + a.axes.transData
        a.set_transform(tr)
        a.set_zorder(a.get_zorder() - 0.001 * y)
    return yoffsets

    # gs.categories, gs.select("Poly")):


# Use get_datalim instead
def get_heights(artists):
    yy = []
    for a in artists:
        pp = a.get_paths()
        maxy = max([max(p.vertices[:, 1]) for p in pp])
        yy.append(maxy)

    return max(yy)
