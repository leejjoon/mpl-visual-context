import pytest
from examples.plot_showcase_violin import plot_violin

@pytest.mark.mpl_image_compare
def test_plot_violin():
    fig = plot_violin()
    return fig
