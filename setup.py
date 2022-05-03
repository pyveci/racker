# -*- coding: utf-8 -*-
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

setup(
    name="postroj",
    version="0.0.0",
    author="Andreas Motl",
    author_email="andreas.motl@cicerops.de",
    url="https://github.com/cicerops/postroj",
    description="An experimental harness tool based on systemd-nspawn",
    long_description=README,
    download_url="https://pypi.org/project/postroj/",
    packages=["postroj"],
    license="AGPL-3.0",
    platforms="All",
    keywords=[
        "virtual",
        "environment",
        "build",
        "test",
        "systemd",
        "virtualbox",
        "vagrant",
        "docker",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Development Status :: 3 - Alpha",
        "Operating System :: Linux",
        "Natural Language :: English",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications",
        "Topic :: Education :: Testing",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Emulators",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "postroj = postroj.cli:cli",
        ],
    },
    install_requires=[
        "click>=7,<9",
        "furl>=2,<3",
    ],
)
