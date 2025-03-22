Welcome to mpl_visual_context's documentation!
==============================================

A collection of tools that provide more visual context to your Matplotlib plots.:

.. image:: _static/images/mpl-visual-context-demo.png

Modules
=======

PathEffects
-----------

- Composable PathEffects : PatheEffects can be pipelined to create customize
  effects.

.. code-block:: python

    pe = [HLSModify(l=0.8) | FillOnly(),
          StrokeColorFromFillColor() | StrokeOnly()]
    a.set_path_effects(pe)

Check :doc:`userguide-patheffects` for more information.

ImageBox
~~~~~~~~



Installation
^^^^^^^^^^^^^

.. code-block:: bash

   pip install mpl_visual_context

Getting Help
^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   USERGUIDE
   examples/index
   API
   Contributing



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
