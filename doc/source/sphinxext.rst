
.. _sphinxext:

BDP Sphinx Extension
====================

BDP package comprises an extension for embedding BDP diagrams in Sphinx documentation. The extension introduces a singled directive *bdp* which can be used to either embed BDP diagram from external file, or render the supplied BDP description. The *bdp* directive is a subclass of the *figure* directive, so all the options of the *figure* directive can also be applied to the *bdp* directive. In addition *:caption:* option can be used to specify the diagram caption.

Specifying an external file::

    .. bdp:: images/example_bdp.py
       :caption: This is an example BDP diagram

Suplying a BDP description inline::

    .. bdp::
       :caption: This is an example BDP diagram
       
       fig << block('Example')
       fig << block('BDP')
       fig << block('diagram')

