#!/usr/bin/env python

"""The setup script."""

from pathlib import Path

from setuptools import find_packages, setup

README = Path("README.md").read_text(encoding="utf-8")
HISTORY = Path("HISTORY.md").read_text(encoding="utf-8")
REQUIRED = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
DEV_REQUIRED = [
    "black==24.4.0",
    "isort==5.13.2",
    "pip==24.0",
    "bump2version==1.0.1",
    "wheel==0.43.0",
    "flake8==7.0.0",
    "tox==4.14.2",
    "coverage==7.4.4",
    "pytest==8.1.1",
    "build",
    "twine==5.1.1",
]


setup(
    author="Juan Manuel Cristóbal Moreno",
    author_email="juanmcristobal@gmail.com",
    python_requires=">=3.10",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    description="extracts the main content from web pages and returns cleaned HTML, optional markdown, and structured metadata.",
    entry_points={
        "console_scripts": [
            "domdown=domdown.cli:main",
        ],
    },
    extras_require={
        "dev": DEV_REQUIRED,
    },
    install_requires=REQUIRED,
    long_description=f"{README}\n\n{HISTORY}",
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="domdown",
    name="domdown",
    packages=find_packages(include=["domdown", "domdown.*"]),
    url="https://github.com/juanmcristobal/domdown",
    version='0.3.6',
    zip_safe=False,
)
