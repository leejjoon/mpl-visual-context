import numpy as np
import matplotlib.colors as mcolors
from .patheffects import ColorModifyStroke

# matrix values are from https://github.com/skratchdot/color-matrix/blob/master/lib/filters.js
# which is MIT licensed.

color_matrix_filters = {
	'grayscale': [
		0.299, 0.587, 0.114,
		0.299, 0.587, 0.114,
		0.299, 0.587, 0.114,
	],
	'sepia': [
		0.393, 0.769, 0.189,
		0.349, 0.686, 0.168,
		0.272, 0.534, 0.131,
	],
	'nightvision': [
		0.1, 0.4, 0,
		0.3, 1, 0.3,
		0, 0.4, 0.1,
	],
	'warm': [
		1.06, 0, 0,
		0, 1.01, 0,
		0, 0, 0.93,
	],
	'cool': [
		0.99, 0, 0,
		0, 0.93, 0,
		0, 0, 1.08,
	],
}


def _get_matrix():
    return dict((k, np.array(l).reshape((3, 3)))
                for k, l in color_matrix_filters.items())


class ColorMatrixStroke(ColorModifyStroke):
    _color_matrix = _get_matrix()

    def __init__(self, kind):
        self._m = self._color_matrix[kind]

    def apply_to_color(self, c):
        c_rgba = mcolors.to_rgba(c)

        c_rgb = c_rgba[:3]
        alpha = c_rgba[3]

        c_rgb_new = self._m @ c_rgb

        return np.append(c_rgb_new, alpha)
