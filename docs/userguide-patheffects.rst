=======================
 PathEffect User Guide
=======================

`mpl-visual-context.patheffects` module provides a collection of PathEffects.
They can be used to change the path-property of the artist on the drawing time.

Composable PathEffects
======================

We provide PatheEffects that can be pipelined to create custom effects.
For example,

.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   from mpl_visual_context.patheffects import (HLSModify,
                                               StrokeColorFromFillColor,
                                               FillOnly, StrokeOnly)

   fig, ax = plt.subplots()

   # original
   p1 = plt.Circle((0.25, 0.5), 0.2, fc="r", ec="k")
   ax.add_patch(p1)

   # w/ patheffects
   p2 = plt.Circle((0.75, 0.5), 0.2, fc="r", ec="k")
   ax.add_patch(p2)

   # set the color lightness to 0.8 and draw with fill-only (no stroke)
   pe_fill = HLSModify(l=0.8) | FillOnly()
   # set the stroke color to original fill color and stroke (no fill)
   pe_stroke = StrokeColorFromFillColor() | StrokeOnly()

   p2.set_path_effects([pe_fill, pe_stroke])

   plt.show()


The PathEffects inherit from `ChainablePathEffect` can be
pipelined using a `|` operator to make a custom patheffects. 

Here is the list.


.. currentmodule:: mpl_visual_context.patheffects

* Color-related

.. autosummary::
   :toctree:
   :nosignatures:

   HLSModify
   HLSaxb
   ColorMatrix
   FillColor
   FillColorFromStrokeColor
   StrokeColor
   StrokeColorFromFillColor

* Path-related

.. autosummary::
   :toctree:
   :nosignatures:

   StrokeOnly
   FillOnly
   Open
   Partial
   Smooth
   SmoothFillBetween

* Clip-related

.. autosummary::
   :toctree:
   :nosignatures:

   ClipPathFromPatch
   ClipPathSelf
   ClipRect

* Tranform-related

.. autosummary::
   :toctree:
   :nosignatures:

   Offset

ImageBox PathEffect
===================

We provide PathEffect that actually draws images (not path), most notable
example is to provide a gradient effect.


.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   from mpl_visual_context.patheffects import (AlphaGradient, StrokeOnly)

   fig, ax = plt.subplots()

   # original
   p1 = plt.Circle((0.25, 0.5), 0.2, fc="r", ec="k")
   ax.add_patch(p1)

   # w/ patheffects
   p2 = plt.Circle((0.75, 0.5), 0.2, fc="r", ec="k")
   ax.add_patch(p2)

   p2.set_path_effects([AlphaGradient("up"),
                        StrokeOnly()])

   plt.show()

.. autosummary::
   :toctree:
   :nosignatures:

   AlphaGradient
   FillImage

.. autosummary::
   :toctree:
   :nosignatures:

   Glow
   CmapGlow

ImageEffect
===========

The `ImageEffect` is very special. It is a patheffect version of MPL's
agg filter. It will render the artist (w/ path effects in the pipeline) as an
image (using the Agg backend), apply image processing (e.g., GaussianBlur),
then place the image at the canvas.

It can be pipelines, but should be at the end of the pipeline. It can be placed
even after other non-chainable PathEffects.


.. plot::
   :include-source:
   :align: center

   import matplotlib.pyplot as plt
   from mpl_visual_context.patheffects import FillOnly, ImageEffect
   from mpl_visual_context.image_effect import LightSource


   fig, ax = plt.subplots()

   # w/ patheffects
   p2 = plt.Circle((0.75, 0.5), 0.2, fc="r", ec="k")
   ax.add_patch(p2)

   p2.set_path_effects([FillOnly() | ImageEffect(LightSource(erosion_size=10,
                                                             gaussian_size=10))])

   plt.show()


.. autosummary::
   :toctree:
   :nosignatures:

   ImageEffect



* Others

.. autosummary::
   :toctree:
   :nosignatures:

   AlphaGradient
   FillImage
   Glow
   CmapGlow
   ImageEffect

