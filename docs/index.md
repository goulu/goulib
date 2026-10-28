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

## Requirements

quite a lot of packages are needed for the full functionality of goulib, but most modules need only a small subset with lazy import when possible.

[Sphinx](http://sphinx-doc.org/) is needed to generate this documentation.

## Modules

```{eval-rst}
.. currentmodule:: goulib

.. autosummary::
    :toctree: modules

    colors
    containers
    datetime2
    decorators
    drawing
    expr
    geom
    geom3d
    graph
    image
    interval
    itertools2
    markup
    math2
    motion
    notebook
    optim
    periodic
    piecewise
    plot
    polynomial
    stats
    table
    tests
    units
    workdays
```

## Classes

```{eval-rst}
.. inheritance-diagram::
    colors
    containers
    datetime2
    decorators
    drawing
    expr
    geom
    geom3d
    graph
    image
    interval
    itertools2
    math2
    motion
    notebook
    optim
    periodic
    piecewise
    plot
    polynomial
    stats
    table
    tests
    units
    workdays
    :parts: 2
```

## Indices and tables

```{toctree}
:maxdepth: 1
:hidden:

changes
```

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
* {doc}`changes`
