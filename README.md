# mpl-visual-context

<img src="https://mpl-visual-context.readthedocs.io/en/latest/_images/mpl-visual-context-demo.png" width="600">

**Enhance your Matplotlib visualizations with richer visual context and sophisticated effects.**

`mpl-visual-context` is a Python library that expands Matplotlib's capabilities, allowing you to easily add contextual elements, apply complex visual effects, and create more compelling and informative plots. Whether you need to highlight data, guide the viewer's eye, or simply make your charts more aesthetically pleasing, `mpl-visual-context` provides the tools you need.

## Key Features

*   **Advanced PathEffects:** Go beyond Matplotlib's standard path effects with a suite of composable effects. Create custom pipelines for unique visual styles, including:
    *   Modifying colors (e.g., `HLSModify`, `StrokeColorFromFillColor`).
    *   Altering path properties (e.g., `StrokeOnly`, `FillOnly`, `Smooth`).
    *   Applying glow, multiple strokes, and other stylistic effects (e.g., `Glow`, `CmapGlow`).
*   **Image-Based Effects:** Integrate image-based elements directly into your plots:
    *   Generate gradient fills (`AlphaGradient`, `Gradient`).
    *   Apply image processing filters to artists (`ImageEffect`).
*   **Composable API:** Many effects are designed to be chained together, offering flexibility and control over the final appearance of your plot elements.

## Installation

```console
pip install mpl_visual_context
```

## Quick Start: Adding a Glow Effect

Here's a simple example of how to apply a glow effect to a line plot:

```python
import matplotlib.pyplot as plt
from mpl_visual_context.patheffects import Glow
from matplotlib.patheffects import Normal # For the original line

# Sample data
x = [0, 1, 2, 3, 4]
y = [0, 2, 1, 3, 1]

fig, ax = plt.subplots(figsize=(6, 4))
line, = ax.plot(x, y, linewidth=2, label="My Data")

# Apply a glow effect
# The Normal() effect ensures the original line is also drawn
line.set_path_effects([Glow(alpha_max=0.8, n_glow_lines=10), Normal()])

ax.set_title("Plot with Glow Effect")
ax.legend()
plt.show()
```

## Documentation

Our documentation provides comprehensive information on all features and how to use them:

*   **User Guide:** For detailed explanations and task-oriented guides, start with our [User Guide](https://mpl-visual-context.readthedocs.io/en/latest/USERGUIDE.html).
*   **Example Gallery:** Explore a gallery of examples showcasing various features at the [ReadTheDocs site](https://mpl-visual-context.readthedocs.io/en/latest/examples/index.html).
*   **API Reference:** For detailed information on specific classes and functions, consult the [API documentation](https://mpl-visual-context.readthedocs.io/en/latest/API.html).

The documentation is actively being developed and improved.

## Contributing

We welcome contributions! Whether it's bug reports, feature suggestions, documentation improvements, or code contributions, please check out our [Contribution Guidelines](https_mpl_visual_context.readthedocs.io/en/latest/Contributing.html) (assuming this will be the link, adjust if different, or link to a `CONTRIBUTING.md` file if it exists).

## Getting Help & Reporting Issues

*   If you have questions or need help, please feel free to [open an issue on GitHub](https://github.com/leejjoon/mpl-visual-context/issues) (adjust link if this is not the correct issue tracker).
*   To report bugs, please also use the GitHub issue tracker.

## License

`mpl-visual-context` is licensed under the MIT License. See the `LICENSE` file for more details. (Assuming MIT and a LICENSE file exists, adjust as necessary).
