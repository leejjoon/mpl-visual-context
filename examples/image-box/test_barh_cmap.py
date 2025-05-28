import pytest
from examples.image_box.plot_barh_cmap import plot_barh_cmap

@pytest.mark.mpl_image_compare
def test_plot_barh_cmap():
    fig = plot_barh_cmap()
    return fig
