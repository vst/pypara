# Currencies, Monetary Value Objects, Arithmetic and Conversion

![](https://img.shields.io/pypi/v/pypara?style=flat-square)
![](https://img.shields.io/pypi/pyversions/pypara?style=flat-square)
![](https://img.shields.io/github/license/vst/pypara?style=flat-square)
![](https://img.shields.io/github/actions/workflow/status/vst/pypara/test.yml?style=flat-square)
![](https://img.shields.io/github/issues/vst/pypara?style=flat-square)
![](https://img.shields.io/github/last-commit/vst/pypara?style=flat-square)

> **TODO**: Provide a complete README.

## Development Notes

Enter the Nix shell:

```sh
nix-shell
```

Run the test suite:

```sh
tox
```

Alternatively:

```sh
nix-shell --argstr python python310 --run tox
nix-shell --argstr python python311 --run tox
```

## Publishing

To build a package and upload to PyPI:

```sh
rm -Rf dist/
python -m build
twine check dist/*
twine upload -s dist/*
```
