
.. _command_line:

Rendering
============

Command line
------------

BDP package can be run from command line to render the images of the BDP diagrams described in Python.

.. argparse::
   :ref: bdp.render.argparser
   :prog: bdp

From Python
-----------

For rendering a BDP figure from the Python script, the *render_fig()* function can be used.

.. autofunction:: bdp.render.render_fig
