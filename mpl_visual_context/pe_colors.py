import colorsys
from numbers import Number
import numpy as np
import matplotlib.colors as mcolors

def _apply_scale_or_const(v0, v1):
    if isinstance(v1, Number):
        return v1
    elif isinstance(v1, str):
        if v1[-1] == "%":
            f = float(v1[:-1]) / 100
            if f > 0:
                return  f * v0
            else:
                return  (1 + f * (1 - v0))


def _apply_hls(hls0, hls1):
    return [_apply_scale_or_const(v0, v1) for v0, v1 in zip(hls0, hls1)]

class HLSModifier:
    """A line based PathEffect which re-draws a stroke."""

    def __init__(self, h="100%", l="100%", s="100%", alpha="100%",
                 dh=0, dl=0, ds=0, dalpha=0):
        """
        h, l, s :
           float between 0 an 1 will be interpreted as a fixed valye
           string of the form "50%" will be interpreted as a fraction to be multiplied. Negtaive percentage will invert the l to (1 - l), multiply the fact, and dp(1 - l).

        Negative percentage of l is useful to make color bright. l value of black is 0. So its "50%" will till be 0. "-50%" will make it 0.5
        """
        super().__init__()
        self.hls = (h, l, s)
        self.alpha = alpha
        self.d_hls = (dh, dl, ds)
        self.d_alpha = dalpha

    def apply_to_hls(self, hls, alpha):
        _hls = _apply_hls(hls, self.hls)
        h, l, s = [v + v1 for v, v1 in zip(_hls,  self.d_hls)]
        _alpha = _apply_scale_or_const(alpha, self.alpha)
        alpha = [_alpha + self.d_alpha]

        l = np.clip(l, 0, 1)
        s = np.clip(s, 0, 1)

        alpha = np.clip(alpha, 0, 1)

        return (h, l, s), alpha

    def apply_to_color(self, c):
        c_rgba = mcolors.to_rgba(c)

        c_rgb = c_rgba[:3]
        alpha = c_rgba[3]

        c_hls = colorsys.rgb_to_hls(*c_rgb)

        (h, l, s), alpha = self.apply_to_hls(c_hls, alpha)

        c_rgb_new = colorsys.hls_to_rgb(h, l, s)

        return np.append(c_rgb_new, alpha)
