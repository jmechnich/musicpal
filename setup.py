#!/usr/bin/env python3

from setuptools import setup  # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="musicpal",
    author="Joerg Mechnich",
    author_email="joerg.mechnich@gmail.com",
    license="GNU GPLv3",
    description="Command line interface for remote controlling a Freecom MusicPal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmechnich/musicpal",
    scripts=["musicpal"],
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=["setuptools_scm"],
    install_requires=["beautifulsoup4", "lxml", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
)
