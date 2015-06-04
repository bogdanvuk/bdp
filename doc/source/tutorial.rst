
.. _tutorial:

BDP short tutorial
==================

Block diagrams consist mainly of blocks connected by lines, hence minly two BDP objects will be used for drawing called *block* and *path*. All drawing objects in BDP are called **templates**. Templates carry descriptions of diagram components in form of many attributes which can be accessed, modified or added as a regular Python object attributes. New templates can be derived from the existing ones by calling them with a list of attributes that are be changed. Finally, the templates can be rendered to the diagram by passint them to the *fig* object:

.. literalinclude:: images/example1.py

Resulting in:

.. figure:: images/example1.png

Lets start with a simple example