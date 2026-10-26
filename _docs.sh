#!/usr/bin/env bash
# Generate Sphinx documentation for goulib

clear
source .venv/bin/activate
pip install sphinx sphinx_rtd_theme
cd docs || exit 1
rm -f build/html/index.html
make html
xdg-open build/html/index.html 
cd ..
