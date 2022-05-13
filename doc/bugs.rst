####
Bugs
####

.. note::

    Just some random notes.


Command line parsing
====================
``--version`` gets attributed to ``racker`` instead of passing it to ``hostnamectl``. Example::

    racker run -it --rm debian-buster /usr/bin/hostnamectl --version

Collisions
==========
When two machines are getting provisioned at the same time::

    Failed to register machine: Machine 'rootfs' already exists

See::

    2022-05-10 20:14:57,697 [racker.cli        ] CRITICAL: Acquiring filesystem image failed. Command 'systemd-nspawn --directory=/var/lib/postroj/archive/rockylinux-8.img/rootfs --bind-ro=/etc/resolv.conf:/etc/resolv.conf --pipe dnf install -y systemd curl wget' returned non-zero exit status 1. Reason: Failed to register machine: Machine 'rootfs' already exists

stdout/stderr redirection
=========================
Most probably, since c5266940/a721345, the progress bar of ``skopeo`` isn't displayed anymore.
