############################
postroj sandbox installation
############################


*****
About
*****

In order to use ``postroj``, when not working on Linux, it is recommended
to use a sandbox installation based on Vagrant. The ``Vagrantfile`` has all the
needed provisioning recipes to provide ``postroj`` installed within the virtual
machine.


***************
Getting started
***************

::

    # Acquire sources.
    git clone https://github.com/cicerops/postroj
    cd postroj

    # Launch Linux environment.
    vagrant up && vagrant ssh

    # Test drive postroj.
    sudo postroj selftest hostnamectl


*****
Usage
*****

``postroj`` can now be used regularly like outlined in the `postroj usage`_
documentation. In order to satisfy privileges, please invoke it with ``sudo``.


.. _postroj usage: https://github.com/cicerops/postroj/blob/main/README.rst#usage
