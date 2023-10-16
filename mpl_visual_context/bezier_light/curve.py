# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper for B |eacute| zier Curves.

.. |eacute| unicode:: U+000E9 .. LATIN SMALL LETTER E WITH ACUTE
   :trim:

See :doc:`../../algorithms/curve-curve-intersection` for examples using the
:class:`Curve` class to find intersections.

.. testsetup:: *

   import numpy as np
   import bezier

   def binary_exponent(value):
       if value == 0.0:
           return -np.inf
       _, result = np.frexp(value)
       # Shift [1/2, 1) --> [1, 2) borrows one from exponent
       return result - 1
"""

import numpy as np

from . import _base
from . import hazmat_curve_helpers as _curve_helpers

class Curve(_base.Base):
    r"""Represents a B |eacute| zier `curve`_.

    .. _curve: https://en.wikipedia.org/wiki/B%C3%A9zier_curve

    We take the traditional definition: a B |eacute| zier curve is a mapping
    from :math:`s \in \left[0, 1\right]` to convex combinations
    of points :math:`v_0, v_1, \ldots, v_n` in some vector space:

    .. math::

       B(s) = \sum_{j = 0}^n \binom{n}{j} s^j (1 - s)^{n - j} \cdot v_j

    .. image:: ../../images/curve_constructor.png
       :align: center

    .. doctest:: curve-constructor

       >>> import bezier
       >>> import numpy as np
       >>> nodes = np.asfortranarray([
       ...     [0.0, 0.625, 1.0],
       ...     [0.0, 0.5  , 0.5],
       ... ])
       >>> curve = bezier.Curve(nodes, degree=2)
       >>> curve
       <Curve (degree=2, dimension=2)>

    .. testcleanup:: curve-constructor

       import make_images
       make_images.curve_constructor(curve)

    Args:
        nodes (Sequence[Sequence[numbers.Number]]): The nodes in the curve.
            Must be convertible to a 2D NumPy array of floating point values,
            where the columns represent each node while the rows are the
            dimension of the ambient space.
        degree (int): The degree of the curve. This is assumed to
            correctly correspond to the number of ``nodes``. Use
            :meth:`from_nodes` if the degree has not yet been computed.
        copy (bool): Flag indicating if the nodes should be copied before
            being stored. Defaults to :data:`True` since callers may
            freely mutate ``nodes`` after passing in.
        verify (bool): Flag indicating if the degree should be verified against
            the number of nodes. Defaults to :data:`True`.
    """

    __slots__ = ("_degree",)  # From constructor

    def __init__(self, nodes, degree, *, copy=True, verify=True):
        super().__init__(nodes, copy=copy)
        self._degree = degree
        self._verify_degree(verify)

    @classmethod
    def from_nodes(cls, nodes, copy=True):
        """Create a :class:`.Curve` from nodes.

        Computes the ``degree`` based on the shape of ``nodes``.

        Args:
            nodes (Sequence[Sequence[numbers.Number]]): The nodes in the curve.
                Must be convertible to a 2D NumPy array of floating point
                values, where the columns represent each node while the rows
                are the dimension of the ambient space.
            copy (bool): Flag indicating if the nodes should be copied before
                being stored. Defaults to :data:`True` since callers may
                freely mutate ``nodes`` after passing in.

        Returns:
            Curve: The constructed curve.
        """
        nodes_np = _base.sequence_to_array(nodes)
        _, num_nodes = nodes_np.shape
        degree = cls._get_degree(num_nodes)
        return cls(nodes_np, degree, copy=copy, verify=False)

    @staticmethod
    def _get_degree(num_nodes):
        """Get the degree of the current curve.

        Args:
            num_nodes (int): The number of nodes provided.

        Returns:
            int: The degree of the current curve.
        """
        return num_nodes - 1

    def _verify_degree(self, verify):
        """Verify that the number of nodes matches the degree.

        Args:
            verify (bool): Flag indicating if the degree should be verified
                against the number of nodes.

        Raises:
            ValueError: If ``verify`` is :data:`True` and the number of nodes
                does not match the degree.
        """
        if not verify:
            return

        _, num_nodes = self._nodes.shape
        expected_nodes = self._degree + 1
        if expected_nodes == num_nodes:
            return

        msg = (
            f"A degree {self._degree} curve should have "
            f"{expected_nodes} nodes, not {num_nodes}."
        )
        raise ValueError(msg)

    @property
    def length(self):
        r"""The length of the current curve.

        Computes the length via:

        .. math::

           \int_{B\left(\left[0, 1\right]\right)} 1 \, d\mathbf{x} =
           \int_0^1 \left\lVert B'(s) \right\rVert_2 \, ds

        Returns:
            float: The length of the current curve.
        """
        return _curve_helpers.compute_length(self._nodes)

    @property
    def __dict__(self):
        """dict: Dictionary of current curve's property namespace.

        This is just a stand-in property for the usual ``__dict__``. This
        class defines ``__slots__`` so by default would not provide a
        ``__dict__``.

        This also means that the current object can't be modified by the
        returned dictionary.
        """
        return {
            "_dimension": self._dimension,
            "_nodes": self._nodes,
            "_degree": self._degree,
        }

    def copy(self):
        """Make a copy of the current curve.

        Returns:
            Curve: Copy of current curve.
        """
        return Curve(self._nodes, self._degree, copy=True, verify=False)

    def evaluate(self, s):
        r"""Evaluate :math:`B(s)` along the curve.

        This method acts as a (partial) inverse to :meth:`locate`.

        See :meth:`evaluate_multi` for more details.

        .. image:: ../../images/curve_evaluate.png
           :align: center

        .. doctest:: curve-eval
           :options: +NORMALIZE_WHITESPACE

           >>> nodes = np.asfortranarray([
           ...     [0.0, 0.625, 1.0],
           ...     [0.0, 0.5  , 0.5],
           ... ])
           >>> curve = bezier.Curve(nodes, degree=2)
           >>> curve.evaluate(0.75)
           array([[0.796875],
                  [0.46875 ]])

        .. testcleanup:: curve-eval

           import make_images
           make_images.curve_evaluate(curve)

        Args:
            s (float): Parameter along the curve.

        Returns:
            numpy.ndarray: The point on the curve (as a two dimensional
            NumPy array with a single column).
        """
        return _curve_helpers.evaluate_multi(
            self._nodes, np.asfortranarray([s])
        )

    def specialize(self, start, end):
        """Specialize the curve to a given sub-interval.

        .. image:: ../../images/curve_specialize.png
           :align: center

        .. doctest:: curve-specialize

           >>> nodes = np.asfortranarray([
           ...     [0.0, 0.5, 1.0],
           ...     [0.0, 1.0, 0.0],
           ... ])
           >>> curve = bezier.Curve(nodes, degree=2)
           >>> new_curve = curve.specialize(-0.25, 0.75)
           >>> new_curve.nodes
           array([[-0.25 ,  0.25 ,  0.75 ],
                  [-0.625,  0.875,  0.375]])

        .. testcleanup:: curve-specialize

           import make_images
           make_images.curve_specialize(curve, new_curve)

        This is a generalized version of :meth:`subdivide`, and can even
        match the output of that method:

        .. testsetup:: curve-specialize2

           import numpy as np
           import bezier

           nodes = np.asfortranarray([
               [0.0, 0.5, 1.0],
               [0.0, 1.0, 0.0],
           ])
           curve = bezier.Curve(nodes, degree=2)

        .. doctest:: curve-specialize2

           >>> left, right = curve.subdivide()
           >>> also_left = curve.specialize(0.0, 0.5)
           >>> np.all(also_left.nodes == left.nodes)
           True
           >>> also_right = curve.specialize(0.5, 1.0)
           >>> np.all(also_right.nodes == right.nodes)
           True

        Args:
            start (float): The start point of the interval we
                are specializing to.
            end (float): The end point of the interval we
                are specializing to.

        Returns:
            Curve: The newly-specialized curve.
        """
        new_nodes = _curve_helpers.specialize_curve(self._nodes, start, end)
        return Curve(new_nodes, self._degree, copy=False, verify=False)

