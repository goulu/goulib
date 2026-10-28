# goulib

library of useful Python code for scientific + technical applications.

see the [IPython notebook](https://github.com/goulu/goulib/blob/master/examples/notebook.ipynb) for an overview of features

[![GitHub version](https://badge.fury.io/gh/goulu%2Fgoulib.svg)](https://badge.fury.io/gh/goulu%2Fgoulib)
[![License](http://img.shields.io/badge/license-LGPL-green.svg)](https://github.com/goulu/goulib/blob/master/LICENSE.TXT)
[![PyPI version](https://badge.fury.io/py/goulib.svg)](https://pypi.python.org/pypi/goulib/)
[![Conda](https://anaconda.org/goulu/goulib/badges/version.svg)](https://anaconda.org/channels/goulu/packages/Goulib/overview)
[![Build](https://github.com/goulu/Goulib/actions/workflows/build.yml/badge.svg)](https://github.com/goulu/Goulib/actions/workflows/build.yml)
[![Coverage](https://coveralls.io/repos/github/goulu/Goulib/badge.svg?branch=master)](https://coveralls.io/github/goulu/Goulib?branch=master)
[![Doc](https://readthedocs.org/projects/goulib/badge/?version=latest)](http://goulib.readthedocs.org/en/latest/)

- **author:** Philippe Guglielmetti <goulib@goulu.net>
- **installation:** `pip install goulib`
- **distribution:** <https://pypi.python.org/pypi/goulib>
- **documentation:** <http://goulib.readthedocs.org/en/latest/>
- **examples:** <https://github.com/goulu/goulib/blob/master/examples/notebook.ipynb>
- **source:** <https://github.com/goulu/goulib>

## Modules

- **colors**: very simple RGB color management
- **container**: sorted collection
- **datetime2**: additions to datetime standard library
- **decorators**: useful decorators
- **drawing**: Read/Write and handle vector graphics in .dxf, .svg and .pdf formats
- **expr**: simple symbolic math expressions
- **geom**, **geom3d**: 2D + 3D geometry
- **graph**: efficient Euclidian Graphs for [NetworkX](http://networkx.github.io/) and related algorithms
- **image**: image processing and conversion
- **interval**: operations on [x..y[ intervals
- **itertools2**: additions to itertools standard library
- **markup**: simple HTML/XML generation (forked from [markup](http://pypi.python.org/pypi/markup/))
- **math2**: additions to math standard library
- **motion**: motion simulation (kinematics)
- **optim**: optimization algorithms : knapsack, traveling salesman, simulated annealing
- **periodic**: periodic functions (WIP)
- **piecewise**: piecewise-defined functions
- **plot**: plotable rich object display on IPython notebooks
- **polynomial**: manipulation of polynomials
- **stats**: very basic statistics functions
- **table**: Table class with Excel + CSV I/O, easy access to columns, HTML output, and much more.
- **tests**: utilities for unit tests (using nose)
- **workdays**: WorkCalendar class with datetime operations on working hours, handling holidays; merges and improves [BusinessHours](http://pypi.python.org/pypi/BusinessHours/) and [workdays](http://pypi.python.org/pypi/workdays/) packages

## Requirements

quite a lot of packages are needed for the full functionality of goulib, but most modules need only a small subset with lazy import when possible.
