Currencies, Monetary Value Objects, Arithmetic and Conversion
=============================================================

+-----------------------+------------------------+
| MASTER                | DEVELOP                |
+=======================+========================+
| |BUILD_STATUS_MASTER| | |BUILD_STATUS_DEVELOP| |
+-----------------------+------------------------+

.. |BUILD_STATUS_MASTER| image:: https://travis-ci.org/vst/pypara.svg?branch=master
    :target: https://travis-ci.org/vst/pypara

.. |BUILD_STATUS_DEVELOP| image:: https://travis-ci.org/vst/pypara.svg?branch=develop
    :target: https://travis-ci.org/vst/pypara

**TODO**: Provide a complete README.


Development Notes
-----------------

Make sure that `tox <https://tox.readthedocs.io/en/latest/>`_ completes successfully.

Create a virtual environment::

  mkvirtualenv --python=python3.6 <VIRTUAL-ENVIRONMENT-NAME>

Install ``tox``::

  pip install tox

And run ``tox``::

  tox
