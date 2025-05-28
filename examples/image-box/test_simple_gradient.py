import pytest
from examples.image_box.plot_simple_gradient import plot_simple_gradient

@pytest.mark.mpl_image_compare
def test_plot_simple_gradient():
    fig = plot_simple_gradient()
    return fig
