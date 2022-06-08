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


VirtualBox on macOS with nested virtualization
==============================================
::

    ==> 2019-box: Booting VM...
    There was an error while executing `VBoxManage`, a CLI used by Vagrant
    for controlling VirtualBox. The command and stderr is shown below.

    Command: ["startvm", "5f422042-d72f-46c5-9bcf-ec27eeee2e06", "--type", "headless"]

    Stderr: VBoxManage: error: Cannot enable nested VT-x/AMD-V without nested-paging and unrestricted guest execution!
    VBoxManage: error:  (VERR_CPUM_INVALID_HWVIRT_CONFIG)
    VBoxManage: error: Details: code NS_ERROR_FAILURE (0x80004005), component ConsoleWrap, interface IConsole
    2022-06-07 15:58:59,573 [racker.cli        ] CRITICAL: Launching container failed. Command 'vagrant up --provider=virtualbox 2019-box' returned non-zero exit status 1.



Using the CrateDB RPM package on openSUSE
=========================================

| A: Workaround applied by running ``rpm --install --nodeps``.
| TODO: Maybe adjust the RPM dependencies?

::

    zypper --non-interactive install crate-4.7.2-1.x86_64.rpm
    Loading repository data...
    Reading installed packages...
    Resolving package dependencies...

    Problem: nothing provides 'systemd-units' needed by the to be installed crate-4.7.2-1.x86_64
     Solution 1: do not install crate-4.7.2-1.x86_64
     Solution 2: break crate-4.7.2-1.x86_64 by ignoring some of its dependencies

    Choose from above solutions by number or cancel [1/2/c/d/?] (c): c

::

    rpm -i crate-4.7.2-1.x86_64.rpm
    warning: crate-4.7.2-1.x86_64.rpm: Header V4 RSA/SHA1 Signature, key ID 06f6eaeb: NOKEY
    error: Failed dependencies:
        shadow-utils is needed by crate-4.7.2-1.x86_64
        systemd-units is needed by crate-4.7.2-1.x86_64


Spawning a container from the CrateDB Docker image
==================================================

Currently, as of 2022-06, the CrateDB Docker image is based on CentOS 7, which
has a systemd installation that is too old for being able to invoke nested
systemd environments.

::

    racker run -it --rm crate/crate:nightly bash

::

    Failed to start transient service unit: Cannot set property AddRef, or unknown property.

=> systemd too old.
