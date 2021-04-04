"""
This module provides the setup procedure.
"""

import os
import re

from setuptools import find_packages, setup

setup(
    name="pypara",
    version=re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", open("pypara/__init__.py").read()).group(1),
    description="Currencies, Monetary Value Arithmetic/Conversion and Some Type Convenience",
    long_description=open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    author="Vehbi Sinan Tunalioglu",
    author_email="vst@vsthost.com",
    url="https://github.com/vst/pypara",
    license="BSD",
    package_data={"pypara": ["py.typed"]},
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["python-dateutil<3.0"],
    dependency_links=[],
    scripts=[],
)
