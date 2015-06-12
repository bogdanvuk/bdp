
Welcome to BDP
==============

BDP (Block Diagrams in Python) aims to become a Python fronted for `TikZ <http://www.texample.net/tikz/>`_ when it comes to drawing block diagrams in order to facilitate the process. BDP wraps the `TikZ <http://www.texample.net/tikz/>`_ statements into the Python objects so that users can describe diagrams in pure Python. However, inserting raw `TikZ <http://www.texample.net/tikz/>`_ in BDP is also possible. Figure below shows an BDP example image which represents the BDP compilation process.

.. image:: https://raw.githubusercontent.com/bogdanvuk/bdp/master/doc/source/images/compile_process.png
    :width: 40%

Figure can be rendered with the `compile_process.py <https://github.com/bogdanvuk/bdp/blob/master/doc/source/images/compile_process.py>`_ BDP diagram. It can be rendered into the PNG with BDP via command line::

   # bdp compile_process.py -p

For a complete list of command line options please take a look at `command_line <http://bdp.readthedocs.org/en/latest/command_line.html#command-line>`_ chapter of the documentation.

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

.. image:: https://raw.githubusercontent.com/bogdanvuk/bdp/master/doc/source/images/uml.png

Figure can be rendered with the `uml.py <https://github.com/bogdanvuk/bdp/blob/master/doc/source/images/uml.py>`_ BDP diagram.

Where to start?
===============

Installation
------------

BDP package currently supports only Python 3. Following are alternative ways to install BDP.

Install BDP using pip::

    pip3 install bdp

Install BDP using easy_install::

    easy_install3 bdp

Install BDP from source::

    python3 setup.py install

BDP requires TeX Live, which could be installed on a Debian or a Debian-derived systems, with::

    # sudo apt-get install texlive

For converting PDF to PNG, pdftoppm, pnmcrop and pnmtopng are needed, which could be installed on a Debian or a Debian-derived systems, with::

   # sudo apt-get install poppler-utils
   # sudo apt-get install netpbm

Read the documentation
----------------------

Read the `BDP documentation <http://bdp.readthedocs.org/en/latest/>`_

Checkout the examples
---------------------

BDP images used in documentation are located in the `images <https://github.com/bogdanvuk/bdp/tree/master/doc/source/images>`_ repository documentation folder.

Get involved
------------

Pull your copy from `github repository <https://github.com/bogdanvuk/bdp>`_
