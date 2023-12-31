"""
==============
Round Corner
==============

"""

from mpl_visual_context.patheffects_image_box import AlphaGradient
from mpl_visual_context.patheffects import RoundCorner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patheffects import Normal

# Fixing random state for reproducibility
np.random.seed(19680801)

fig, ax = plt.subplots(num=1, clear=True)

# Example data
n = 5
x_pos = np.arange(n)
performance = 5 * np.random.rand(n)

bars = ax.bar(x_pos, performance, align='center', alpha=0.7)

pe = [RoundCorner() | AlphaGradient("up")]
for p in bars:
    p.set_path_effects(pe)

plt.show()
