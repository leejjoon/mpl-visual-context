import pytest
from examples.plot_showcase_planets import plot_planets

@pytest.mark.mpl_image_compare
def test_plot_planets():
    fig = plot_planets()
    return fig
