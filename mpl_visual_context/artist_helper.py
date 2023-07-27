from matplotlib.artist import Artist
from matplotlib.transforms import Bbox

class ArtistsExtent(Artist):
    def __init__(self, artists):
        self._artists = artists

    def get_window_extent(self, renderer):
        extents = [a.get_window_extent(renderer) for a in self._artists]
        return Bbox.union(extents)
