# Copilot instructions for goulib

Be concise. Produce edits that follow the project's style and tests. This file highlights repository-specific facts an AI coding agent should know to be productive immediately.

Key facts

- Project: `goulib` — a small, single-package Python library (package directory: `goulib/`).
- Versioning/build: `pyproject.toml` (PEP 621 fields + setuptools dynamic deps). Runtime requires Python >=3.9.
- Tests live under `tests/` and are run with pytest. CI uses: `pip install .`, `flake8`, then `coverage run -m pytest tests/`.

Where to look first

- `README.rst` — high level overview and module list.
- `pyproject.toml` — packaging, version, and dependency wiring (`requirements.txt` is the canonical dependency list).
- `docs/conf.py` — sphinx configuration; shows how the package is imported for docs and where to find version string (`goulib/__init__.py`).
- `tests/` — many tests contain concrete examples of API usage; copy examples from tests for realistic changes.

Important patterns & conventions

- Single namespace package: `goulib` exports many small modules (e.g. `goulib.drawing`, `goulib.geom`, `goulib.image`). Prefer adding functions/classes to the appropriate module rather than creating new top-level packages.
- Lazy/optional imports: many modules declare optional dependencies in `requirements.txt`. Guard imports in code (tests skip optional features when the dependency is missing). Follow the same pattern when adding code that uses optional libs (wrap import in try/except and skip or provide fallback behavior).
- Tests use pytest and often use `pytest.skip(...)` for optional features. If adding functionality requiring a new dependency, update `requirements.txt` and `requirements-dev.txt` (if needed), and ensure tests reflect optional import behavior.
- Cross-platform testing: some tests use Windows-style paths (backslashes). Prefer using `os.path` utilities when modifying tests or adding file paths.

Build / test / CI commands (copyable)

- Install and test locally (same as CI):
  - python -m pip install --upgrade pip
  - python -m pip install flake8 pytest coveralls
  - pip install .
  - flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
  - coverage run -m pytest tests/

Code-style and linting

- CI runs flake8 with a strict check for syntax/undefined names (select E9,F63,F7,F82). Keep line length <=127 in practice. Avoid large refactors that massively reformat code.

Examples to reference when changing behavior

- Geometry & drawing: `goulib/drawing.py` (renders to matplotlib, handles many optional backends). Look at tests in `tests/test_goulib_drawing.py` for expected behaviors and example inputs/outputs.
- Package version: `goulib/__init__.py` contains `__version__` used by docs/build.
- Tests helpers: `goulib/tests.py` contains utilities used by many tests; update cautiously.

Integration points

- Sphinx docs (docs/): uses `get_version()` reading `goulib/__init__.py` and adds `..` to sys.path. If you change packaging layout, update `docs/conf.py` accordingly.
- CI workflows: `.github/workflows/build.yml` and `release.yml` show matrix python versions and commands — keep changes compatible with these flows.

When you create changes

- Add or update unit tests in `tests/` covering the new behavior. Use existing tests as templates.
- If you add a runtime dependency, list it in `requirements.txt`. If only needed for development/tests, update `requirements-dev.txt`.
- Run flake8 and pytest locally before opening a PR. The repository prefers minimal, targeted changes.

If in doubt

- Prefer small, well-tested changes. Use tests as the source of truth for APIs. Ask for clarification if a change affects many modules or the packaging.

Please review and tell me any missing examples or specific workflows you'd like included.

Concrete edit examples

- Small behavior change: `goulib/math2.py` implements a fallback `isclose` if math.isclose is missing — modify or extend it carefully. Tests referencing `math2.isclose` live under `tests/test_goulib_math2.py` and are good templates.
- Add a utility function: place it inside the appropriate module (e.g. `math2.py` for math helpers). Add a unit test in `tests/` mirroring existing tests (use `pytest` style and functions from `goulib/tests.py` if needed).

PR checklist (run locally before opening PR)

- Run linting (note CI flake8 flags):

```bash
python -m pip install --upgrade pip
python -m pip install flake8 pytest coveralls
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

- Run tests with coverage:

```bash
coverage run -m pytest tests/
```

- If you add a runtime dependency, update `requirements.txt`. If the dependency is only for tests/dev, update `requirements-dev.txt`.
