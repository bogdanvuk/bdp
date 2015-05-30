Prerequisites
=============

The following executables are used for rasterizing TeX documents:

* ``pdflatex``
* ``pdftoppm``
* ``pnmcrop``
* ``pnmtopng``

On a Debian_ or a `Debian-derived`_ system, they could be installed
with::

    # apt-get install texlive
    # apt-get install poppler-utils
    # apt-get install netpbm

If you want to generate diagrams with TikZ_, install::

    # apt-get install texlive-pictures

