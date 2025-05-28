import pytest
from examples.image_effect.plot_demo_image_effect import plot_demo_image_effect

@pytest.mark.mpl_image_compare
def test_plot_demo_image_effect():
    fig = plot_demo_image_effect()
    return fig
