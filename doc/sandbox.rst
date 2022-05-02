############################
postroj sandbox installation
############################


The postroj sandbox installation described in this document is based on
Vagrant. You can also install it on any other Linux system.


Acquire sources
===============

::

    git clone https://github.com/cicerops/postroj
    cd postroj


Launch Linux environment
========================

::

    vagrant up
    vagrant ssh


Install postroj
===============

::

    cd /usr/src/postroj
    python3 -m venv .venv_linux
    source .venv_linux/bin/activate
    pip install --editable=.


Invoke postroj
==============

Run image provider::

    sudo $(command -v python) -m postroj.image

