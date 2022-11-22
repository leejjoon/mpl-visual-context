
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
norm = mcolors.Normalize()

import seaborn as sns

from scipy.stats import gaussian_kde

from mpl_visual_context.image_box_effect import (GradientEffect)

tips = sns.load_dataset("tips")

def kde_xy(y0):
    kde = gaussian_kde(y0)
    import numpy as np
    sample_range = np.nanmax(y0) - np.nanmin(y0)
    x = np.linspace(
        np.nanmin(y0) - 0.5 * sample_range,
        np.nanmax(y0) + 0.5 * sample_range,
        1000,
    )

    y = kde(x)

    return x, y


if True:

    y0 = tips["total_bill"]
    x, y = kde_xy(y0)
    fig, ax = plt.subplots(1, 1, num=1, clear=True)

    y1 = y
    y2 = 2*y
    norm.vmax = max(y2)

    f1 = ax.fill_between(x, y1=y)
    f1.set_ec("k")
    pe_f1 = GradientEffect("up", f1, norm=norm)
    f1.set_path_effects([pe_f1])

    f2 = ax.fill_between(x+ 100, y1=0.05+y2, y2=0.05)
    f2.set_ec("k")
    pe_f2 = GradientEffect("up", f2, norm=norm)
    f2.set_path_effects([pe_f2])


    # f1 = ax.fill_between(x, y1=y)
    # f1.set_path_effects([BboxPathEffect(im)])
    # plt.colorbar(pe_f2.bbox_image)
    plt.show()

