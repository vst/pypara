# Currencies, Monetary Value Objects, Arithmetic and Conversion

![](https://github.com/vst/pypara/workflows/Install%20and%20Test/badge.svg)

> **TODO**: Provide a complete README.

## Development Notes

Create a virtual environment:

```
python3.8 -m venv /opt/venvs/pypara3.8
```

Activate the virtual environment:

```
source /opt/venvs/pypara3.8/bin/activate
```

Upgrade base dependencies:

```
pip install --upgrade pip setuptools
```

Install production and development dependencies:

```
pip install -e . -r dev-requirements.txt
```

Make sure that [tox](https://tox.readthedocs.io/en/latest/) completes successfully:

```
tox
```

## Publishing

To build a package and upload to PyPI:

```
pip install --upgrade twine
python setup.py sdist bdist_wheel
twine check dist/*
twine upload -s dist/*
```