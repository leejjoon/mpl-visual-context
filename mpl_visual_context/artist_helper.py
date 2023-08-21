import numpy as np
from matplotlib.artist import Artist
from matplotlib.transforms import Bbox


class ArtistsExtent(Artist):
    def __init__(self, artists):
        self._artists = artists

    def get_window_extent(self, renderer):
        extents = [a.get_window_extent(renderer) for a in self._artists]
        return Bbox.union(extents)


def get_datalim(a):
    if hasattr(a, "get_xydata"):  # Line2D
        xy = a.get_xydata()
        xmax, ymax = np.nanmax(xy, axis=0)
        xmin, ymin = np.nanmin(xy, axis=0)

        bbox = Bbox.from_extents(xmin, ymin, xmax, ymax)
    elif hasattr(a, "get_datalim"):
        bbox = a.get_datalim(a.axes.transData)
    else:
        raise ValueError(f"do not know how to get datalim of the artst: {a}")

    return bbox


class ArtistListWithPE(Artist):
    """A simple container to filter multiple artists at once."""

    def __init__(self, artist_list, pe):
        super().__init__()
        self._artist_list = artist_list
        self._pe = pe

    def draw(self, renderer):
        for a in self._artist_list:
            pe0 = a.get_path_effects()
            a.set_path_effects(self._pe)
            a.draw(renderer)
            a.set_path_effects(pe0)
