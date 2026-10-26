cls -C
call pip install sphinx sphinx_rtd_theme
cd docs
del build\html\index.html
call make html
start build\html\index.html
cd ..