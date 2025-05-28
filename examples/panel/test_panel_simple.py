import pytest
from examples.panel.plot_panel_simple import plot_panel_simple

@pytest.mark.mpl_image_compare
def test_plot_panel_simple():
    fig = plot_panel_simple()
    return fig
