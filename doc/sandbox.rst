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


Install postroj
===============

::

    vagrant ssh
    sudo su -
    cd /usr/src/postroj
    python3 -m venv .venv_linux
    source .venv_linux/bin/activate
    pip install --editable=.


Invoke postroj
==============

::

    python -m postroj.image
    python -m postroj.container
    python -m postroj.probe

