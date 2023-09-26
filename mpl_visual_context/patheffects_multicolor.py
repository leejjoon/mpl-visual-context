import numpy as np
from matplotlib.patheffects import AbstractPathEffect
import matplotlib.transforms as mtransforms
from matplotlib import colormaps
from .bezier_helper import mpl2bezier, beziers2mpl


class MultiColorLine(AbstractPathEffect):
    def __init__(
            self,
            axes,
            image_box,
            min_length=10,
    ):
        self.image_box = image_box
        self.axes = axes
        self.min_length = min_length
        # self.close = close # whether to close the path or not

    def get_segmented(self, path, min_length):

        bl = mpl2bezier(path)
        segmented_paths = [] # list of Path
        segmented_xy = [] # xy positions

        for bb, close_poly in bl:

            bb_segmented = []

            # This is to make connections between paths smooth. We combine the
            # last segment from the previous path with the 1st segment of the
            # current one.
            seg_first = []
            seg_last = []
            for b in bb:

                n = max(int(b.length / min_length) + 1, 2)
                t = np.linspace(0, 1, n)
                seg_list = [b.specialize(t[i], t[i+1]) for i in range(n-1)]
                if seg_last:  # When this is a first segment
                    bb_segmented.append(seg_last + seg_list[:1])
                else:
                    seg_first = seg_list[:1] # we save it for the end.

                bb_segmented.extend([[s] for s in seg_list[1:-1]])
                seg_last = [seg_list[-1]]

            if close_poly:
                bb_segmented.append(seg_last + seg_first)
            else:
                bb_segmented.extend([seg_last, seg_first])

            segmented_xy.extend([b[0].nodes[:, 0] for b in bb_segmented])

            _paths = [beziers2mpl(b1, close=False) for b1 in bb_segmented]
            segmented_paths.extend(_paths)

        return segmented_paths, np.array(segmented_xy)

    def draw_path(self, renderer, gc, tpath, affine, rgbFace):

        path = affine.transform_path(tpath)
        segmented_paths, segmented_xy = self.get_segmented(path,
                                                           min_length=self.min_length)

        self.image_box.axes = self.axes
        colors = self.image_box.pick_color_from_image(renderer,
                                                      segmented_xy)

        affine0 = mtransforms.IdentityTransform()

        # FIXME We simply use a for loop. Using LineCollection may perform
        # better for supported backend.
        gc1 = renderer.new_gc()
        gc1.copy_properties(gc)

        for p, c in zip(segmented_paths, colors/255.):
            gc1.set_foreground(c)
            renderer.draw_path(gc1, p, affine0, None)

