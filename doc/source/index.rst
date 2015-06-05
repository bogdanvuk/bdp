
Welcome to BDP
==============

BDP (Block Diagrams in Python) aims to become a Python fronted for `TikZ <http://www.texample.net/tikz/>`_ when it comes to drawing block diagrams in order to facilitate the process. BDP wraps the `TikZ <http://www.texample.net/tikz/>`_ statements into the Python objects so that users can describe diagrams in pure Python. However, inserting raw `TikZ <http://www.texample.net/tikz/>`_ in BDP is also possible. Figure below shows an BDP example image which represents the BDP compilation process.

.. _fig-bdp-toolchain:

.. figure:: images/compile_process.png
    :width: 60%

Figure can be rendered with the :ref:`Python code <fig-compile-process>` provided below, which is also available in repository inside `compile_process.py <https://github.com/bogdanvuk/bdp/blob/master/doc/source/images/compile_process.py>`_ BDP diagram. It can be rendered into the PNG with BDP via command line::

   # bdp compile_process.py -p
   
Why BDP?
--------

BDP brings following benefits:

- Diagram description in Python which should render it more readable
- Step-by-step debugging of the diagram description
- Use the tools and design environments available for Python development (debugging, code completion, refactoring, documentation utilities...)
- Use vast Python library of packages

BDP features
------------

BDP package comprises:

- Python classes that wrap the Tikz statements
- Class for rendering PDF and PNG images from the Python description
- Shell entry point for rendering BDP images from command line
- Sphinx extensions for embedding BDP images into the Sphinx documents

Image below is a more complex example, which shows how power of Python programming can be used to generate diagrams with BDP. Image shows an UML-like diagram of few major BDP templates.

.. _fig-uml:

.. figure:: images/uml.png
    :width: 70%
    
Figure can be rendered with the :ref:`Python code <fig-uml-source>` provided below.

Where to start?
===============

Installation
------------

Install BDP using pip::
    
    pip install bdp

Install BDP using easy_install::
    
    easy_install bdp

Install BDP from source::
    
    python setup.py install
    
BDP requires TeX Live, which could be installed on a Debian or a Debian-derived systems, with::

    # sudo apt-get install texlive
    
For converting PDF to PNG, pdftoppm, pnmcrop and pnmtopng are needed, which could be installed on a Debian or a Debian-derived systems, with::

   # sudo apt-get install poppler-utils
   # sudo apt-get install netpbm

Read the documentation
----------------------

Start with the short tutorial :ref:`tutorial`

Checkout the examples
---------------------

BDP images used in documentation are located in the `images <https://github.com/bogdanvuk/bdp/tree/master/doc/source/images>`_ repository documentation folder.

Get involved
------------

Pull your copy from `github repository <https://github.com/bogdanvuk/bdp>`_

Source codes for the examples
=============================

.. _fig-compile-process:

.. literalinclude:: images/compile_process.py
    :caption: BDP description of the compilation process diagram.
    
.. _fig-uml-source:

.. literalinclude:: images/uml.py
    :caption: UML-like diagram of few major BDP templates.    

Contents
========

.. toctree::
   :maxdepth: 2
   
   tutorial
   command_line
