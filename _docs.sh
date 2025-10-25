#!/usr/bin/env bash
# Generate Sphinx documentation for goulib

clear
pip install sphinx sphinx_rtd_theme
cd docs || exit 1
sphinx-apidoc ../goulib -eo modules 
rm -f modules/goulib.rst
rm -f build/html/index.html
make html
xdg-open build/html/index.html 
cd ..
