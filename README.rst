Currencies, Monetary Value Objects, Arithmetic and Conversion
=============================================================

|BUILD_STATUS|

.. |BUILD_STATUS| image:: https://github.com/vst/pypara/workflows/Install%20and%20Test/badge.svg
    :target: https://github.com/vst/pypara/actions

**TODO**: Provide a complete README.


Development Notes
-----------------

Create a virtual environment::

  python3.8 -m venv /opt/venvs/pypara3.8

Activate the virtual environment::

  source /opt/venvs/pypara3.8/bin/activate

Upgrade base dependencies::

  pip install --upgrade pip setuptools

Install production and development dependencies:

  pip install -e . -r dev-requirements.txt

Make sure that `tox <https://tox.readthedocs.io/en/latest/>`_ completes successfully::

And run ``tox``::

  tox

Publishing
----------

```
pip install --upgrade twine
python setup.py sdist bdist_wheel
twine upload -s dist/*
```
