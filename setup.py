"""
This module provides the setup procedure.
"""

import os
import re

from setuptools import find_packages
from setuptools import setup

#: Defines the name of our package.
NAME = "pypara"

#: Defines the regular expression of the version.
VERSION_REGEXP = r"__version__\s*=\s*['\"]([^'\"]*)['\"]"

#: Defines the version of our package.
VERSION = re.search(VERSION_REGEXP, open(f"{NAME}/__init__.py", encoding="utf_8_sig").read()).group(1)

#: Defines the package root directory.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

#: Defines the README file contents.
README = open(os.path.join(BASEDIR, "README.rst")).read()

#: Defines the LICENSE file contents.
LICENSE = open(os.path.join(BASEDIR, "LICENSE")).read()

#: Defines a list of required libraries.
REQUIREMENTS = []

#: Defines extra requirements for various other purposes.
REQUIREMENTS_EXTRAS = {
    "dev": [
        "ipython",
        "mypy",
        "flake8",
        "tox",
        "twine",
    ],
}

## Proceed with setup:
setup(
    name=NAME,
    version=VERSION,
    description=NAME,
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    author="Vehbi Sinan Tunalioglu",
    author_email="vst@vsthost.com",
    url="https://github.com/vst/pypara",
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    extras_require=REQUIREMENTS_EXTRAS,
    dependency_links=[],
    scripts=[],
)
