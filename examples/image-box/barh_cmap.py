"""
====================
Horizontal bar chart w/ Gradient
====================

This example is based on barh.py example from matplotlib.
"""
import matplotlib.pyplot as plt
import numpy as np

# import seaborn as sns
# sns.set_theme()
import mplcyberpunk
plt.style.use("cyberpunk")

# Fixing random state for reproducibility
np.random.seed(19680801)

fig, ax = plt.subplots(num=1, clear=True)

# Example data
people = ('Tom', 'Dick', 'Harry', 'Slim', 'Jim')
y_pos = np.arange(len(people))
performance = 3 + 10 * np.random.rand(len(people))
error = np.random.rand(len(people))

bars = ax.barh(y_pos, performance, xerr=error, align='center')
ax.set_yticks(y_pos, labels=people)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Performance')
ax.set_title('How fast do you want to go today?')

from mpl_visual_context.image_box_effect import (GradientBboxImage,
                                                 ImageClipEffect)

bbox_image = GradientBboxImage("right", alpha="right",
                               extent=[0, 0, 1., 1],
                               coords=bars)

pe = [ImageClipEffect(bbox_image, ax=ax)]

for p in bars:
    p.set_path_effects(pe)

plt.show()
