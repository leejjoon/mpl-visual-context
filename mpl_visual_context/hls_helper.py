import colorsys
from numbers import Number
import numpy as np
import matplotlib.colors as mcolors
from numbers import Number


def _convert_scale_or_const(v1):
    if isinstance(v1, str):
        if v1[-1] == "%":
            f = float(v1[:-1]) / 100
            if f > 0:
                return (f, 0)
            else:
                return (-f, 1 + f)
    return (0, v1)


class HLSModify_axb:
    @staticmethod
    def _check_ab(ab):
        if isinstance(ab, Number):
            return 0, ab

        try:
            a, b = ab
            assert isinstance(a, Number) and isinstance(b, Number)
            return a, b
        except:
            raise ValueError(
                "Unsupported parameter: requires a single number a seuqence of two numbers"
            )

    def __repr__(self):
        # "HLSab: h={self.hls_a[0]}xh + "
        s_hls = ", ".join(
            [f"{n}'={a}*{n}+{b}" for n, a, b in zip("hls", self.hls_a, self.hls_b)]
        )
        s_alpha = f"a'={self.alpha_a}*a+{self.alpha_b}"

        return f"HLSModify({s_hls}, {s_alpha})"

    def __init__(
        self, h_ab=(1, 0), l_ab=(1, 0), s_ab=(1, 0), alpha_ab=(1, 0), clip_mode="clip"
    ):
        """ """
        super().__init__()
        h_a, h_b = self._check_ab(h_ab)
        l_a, l_b = self._check_ab(l_ab)
        s_a, s_b = self._check_ab(s_ab)
        self.alpha_a, self.alpha_b = self._check_ab(alpha_ab)
        self.hls_a = np.array([h_a, l_a, s_a])
        self.hls_b = np.array([h_b, l_b, s_b])
        self.clip_mode = clip_mode

    def apply_to_hls(self, hls, alpha):
        h, l, s = self.hls_a * hls + self.hls_b
        alpha = self.alpha_a * alpha + self.alpha_b

        if self.clip_mode == "clip":
            l, s, alpha = np.clip([l, s, alpha], 0, 1)
            # hls = np.clip(hls, 0, 1)
            # alpha = np.clip(alpha, 0, 1)
        # else:
        #     hls %= 1
        #     alpha %= 1

        h %= 1

        return [h, l, s], alpha

    def apply_to_color(self, c):
        c_rgba = mcolors.to_rgba(c)

        c_rgb = c_rgba[:3]
        alpha = c_rgba[3]

        c_hls = colorsys.rgb_to_hls(*c_rgb)

        (h, l, s), alpha = self.apply_to_hls(c_hls, alpha)

        c_rgb_new = colorsys.hls_to_rgb(h, l, s)
        return np.append(c_rgb_new, [alpha])
