###########################
Racker sandbox installation
###########################


*****
About
*****

In order to use Racker, when not working on Linux, it is recommended to use a
sandbox installation based on Vagrant. The ``Vagrantfile`` has all the needed
provisioning recipes to provide a working Racker installation within the
virtual machine without further ado.


***************
Getting started
***************

::

    # Acquire sources.
    git clone https://github.com/cicerops/racker
    cd racker

    # Launch Linux environment.
    vagrant up && vagrant ssh

    # Test drive.
    sudo postroj selftest hostnamectl


*****
Usage
*****

Racker can now be used regularly like outlined in the `Racker usage`_
documentation. In order to satisfy privileges, please invoke it with ``sudo``.


.. _Racker usage: https://github.com/cicerops/racker/blob/main/README.rst#usage
