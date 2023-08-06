#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jae-Joon Lee.
# Distributed under the terms of the Modified BSD License.

# Must import __version__ first to avoid errors importing this file during the build process.
# See https://github.com/pypa/setuptools/issues/1724#issuecomment-627241822
from ._version import __version__

# from .example import example_function

import colorsys
from matplotlib.colors import to_rgb

# from .patheffects import HLSModifyStroke, ColorMatrixStroke
from .pe_cyberfunk import GlowStroke


def check_dark(c):
    c_rgb = to_rgb(c)
    c_hls = colorsys.rgb_to_hls(*c_rgb)
    return c_hls[1] < 0.5
