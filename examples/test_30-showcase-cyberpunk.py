import pytest
from examples.plot_showcase_cyberpunk import plot_cyberpunk

@pytest.mark.mpl_image_compare
def test_plot_cyberpunk():
    fig = plot_cyberpunk()
    return fig
