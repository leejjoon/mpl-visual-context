
from mpl_visual_context.patheffects_color import HLSModify, StrokeColorFromFillColor
import matplotlib.pyplot as plt
import mplcyberpunk
# plt.style.use("cyberpunk")

from mpl_visual_context import check_dark

from mpl_visual_context.patheffects import (GCModify, HLSaxb,
                                            Glow,
                                            StrokeColor, StrokeOnly,
                                            FillColor, FillOnly,
                                            ClipPathSelf)

fig, ax = plt.subplots(num=1, clear=True, figsize=(10, 5))


invert_l = HLSaxb(l_ab=(-1, 1))  # invert the lightness

pe_text_registry = {
    "shadow": [
        GCModify(linewidth=1) | invert_l
        | Glow(alpha_line=10., diff_linewidth=0., offset=(3,-3)),
        FillOnly()
    ],
    "glow": [
        invert_l | Glow(),
        FillOnly(),
        GCModify(linewidth=1) | invert_l | StrokeOnly()
    ],
    "engraved": [
        ClipPathSelf()
        | GCModify(linewidth=1) | invert_l
        | Glow(alpha_line=1., diff_linewidth=.5, offset=(3,-3)),
        GCModify(linewidth=.5) | invert_l | StrokeOnly()
    ],
    "neon": [
        invert_l | Glow(alpha_line=1),
        GCModify(linewidth=3) | StrokeOnly()
     ],
}

if check_dark(ax.patch.get_fc()):
    text_color = "k"
else:
    text_color = "w"

for i, pe in enumerate(pe_text_registry.values()):
    t1 = ax.text(
        i + 0.5,
        0.5,
        "M",
        size=80,
        color=text_color,
        weight="bold",
        va="center",
        ha="center",
    )
    t1.set_path_effects(pe)

ax.set_xlim(0, len(pe_text_registry))

plt.show()
