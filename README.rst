goulib
======

library of useful Python code for scientific + technical applications.

see the `IPython notebook <http://nbviewer.ipython.org/github/Goulu/goulib/blob/master/notebook.ipynb>`_ for an overview of features

.. image:: https://badge.fury.io/gh/goulu%2Fgoulib.svg
    :target: https://badge.fury.io/gh/goulu%2Fgoulib
.. image:: http://img.shields.io/badge/license-LGPL-green.svg
    :target: https://github.com/goulu/goulib/blob/master/LICENSE.TXT
    :alt: License
.. image:: https://badge.fury.io/py/goulib.svg
    :target: https://pypi.python.org/pypi/goulib/
    :alt: Version
.. image:: https://travis-ci.org/goulu/goulib.svg?branch=master
    :target: https://travis-ci.org/goulu/goulib
    :alt: Build
.. image:: https://coveralls.io/repos/github/goulu/Goulib/badge.svg?branch=master
    :target: https://coveralls.io/github/goulu/Goulib?branch=master
    :alt: Coverage
.. image:: https://readthedocs.org/projects/goulib/badge/?version=latest
  :target: http://goulib.readthedocs.org/en/latest/
  :alt: Doc
  
:author: Philippe Guglielmetti goulib@goulu.net
:installation: "pip install goulib"
:distribution: https://pypi.python.org/pypi/goulib
:documentation: https://goulib.readthedocs.org/
:notebook: .. image:: https://mybinder.org/badge_logo.svg :target: https://mybinder.org/v2/gh/goulu/goulib/master?filepath=notebook.ipynb
:source: https://github.com/goulu/goulib

Modules
-------

**colors**
	very simple RGB color management
**container**
    sorted collection
**datetime2**
	additions to datetime standard library
**decorators**
	useful decorators
**drawing**
	Read/Write and handle vector graphics in .dxf, .svg and .pdf formats
**expr**
	simple symbolic math expressions
**geom**, **geom3d**
	2D + 3D geometry
**graph**
	efficient Euclidian Graphs for `NetworkX <http://networkx.github.io/>`_ and related algorithms
**image**
    image processing and conversion
**interval**
	operations on [x..y[ intervals
**itertools2**
	additions to itertools standard library
**markup**
	simple HTML/XML generation (forked from `markup <http://pypi.python.org/pypi/markup/>`_)
**math2**
	additions to math standard library
**motion**
	motion simulation (kinematics)
**optim**
	optimization algorithms : knapsack, traveling salesman, simulated annealing
**periodic**
	periodic functions (WIP)
**piecewise**
	piecewise-defined functions
**plot**
    plotable rich object display on IPython notebooks
**polynomial**
	manipulation of polynomials
**stats**
    very basic statistics functions
**table**
	Table class with Excel + CSV I/O, easy access to columns, HTML output, and much more.
**tests**
    utilities for unit tests (using nose)
**workdays**
	WorkCalendar class with datetime operations on working hours, handling holidays
	merges and improves `BusinessHours <http://pypi.python.org/pypi/BusinessHours/>`_ and `workdays <http://pypi.python.org/pypi/workdays/>`_ packages

Requirements
------------

quite a lot of packages are needed for the full functionality of goulib, but most modules need only a small subset with lazy import when possible.