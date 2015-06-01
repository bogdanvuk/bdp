
Welcome to BDP
==============

BDP (Block Diagrams in Python) aims to become a Python fronted for `TikZ <http://www.texample.net/tikz/>`_ when it comes to drawing block diagrams in order to facilitate the process. BDP wraps the `TikZ <http://www.texample.net/tikz/>`_ statements into the Python objects so that users can describe diagrams in pure Python. However, inserting raw `TikZ <http://www.texample.net/tikz/>`_ in BDP is also possible. Benefits from using BDP comprise:

- Diagram description in Python which should render it more readable
- Step-by-step debugging of the diagram description
- Use the tools and design environments available for Python development (code completion, refactoring, documentation utilities...)
- Use vast Python library of packages

.. bdp::
    :width: 30%
    
    block.size=(6,3)
    
    fig << block(r"Python \\ Description")
    fig << prev(r"TikZ \\ Renderer").left()

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
