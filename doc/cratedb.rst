#########################
Using Postroj for CrateDB
#########################


************
Introduction
************

About
=====

The purpose of this documentation section is to outline how to test the
successful package installation and service startup of CrateDB distribution
packages on different operating systems.

The ``postroj pkgprobe`` command is the tool of choice here, in the spirit of
`autopkgtest`_. Use ``postroj list-images`` to list all available operating
systems.

Please `report back`_ about any incompatibilities or flaws you may discover,
and also take notice of a few backlog items at the bottom of the page.

Prerequisites
=============

After installing Racker and its dependencies, let's define a convenient
shortcut function to probe the installation of CrateDB packages. It obtains
the operating system image label and the package URL as positional parameters
on the command line.

::

    function probe-cratedb() {
        osimage=$1
        pkgurl=$2
        postroj pkgprobe \
            --image=${osimage} \
            --package=${pkgurl} \
            --check-unit=crate \
            --check-network=http://localhost:4200 \
            --check-network=tcp://localhost:5432 \
            --network-timeout=30
    }


*******
Probing
*******


Debian systems
==============

Test package on Debian buster and bullseye::

    probe-cratedb debian-buster https://cdn.crate.io/downloads/apt/testing/pool/main/c/crate/crate_5.2.2-1~buster_amd64.deb
    probe-cratedb debian-bullseye https://cdn.crate.io/downloads/apt/testing/pool/main/c/crate/crate_5.2.2-1~bullseye_amd64.deb

Alternative OS image labels are: ``debian-{stretch,buster,bullseye,bookworm,sid}``.


Ubuntu systems
==============

Test package on 20.04 LTS (Focal Fossa) and 22.04 LTS (Jammy Jellyfish)::

    probe-cratedb ubuntu-focal https://cdn.crate.io/downloads/deb/testing/pool/main/c/crate/crate_5.2.2-1~focal_amd64.deb
    probe-cratedb ubuntu-jammy https://cdn.crate.io/downloads/deb/testing/pool/main/c/crate/crate_5.2.2-1~jammy_amd64.deb

Alternative OS image labels are: ``ubuntu-{focal,jammy}``.


Red Hat systems
===============

Test package on Fedora 35, 36, 37, CentOS 8 and 9, and RHEL 8::

    probe-cratedb fedora-37 https://cdn.crate.io/downloads/yum/testing/7/x86_64/crate-5.2.2-1.x86_64.rpm

Alternative OS image labels are: ``fedora-{35,36,37}``, ``centos-{8,9}``, ``rhel-{8,9}``.


SUSE systems
============

Test package on OpenSUSE Leap and Tumbleweed, and SLES 15::

    probe-cratedb opensuse-leap https://cdn.crate.io/downloads/yum/testing/7/x86_64/crate-5.2.2-1.x86_64.rpm

Alternative OS image labels are: ``opensuse-{leap,tumbleweed}``, ``sles-{15,bci}``.


*******
Backlog
*******


- Fix OS: Debian bullseye currently says ``dpkg: error processing package systemd``.
  It has worked a while ago already.
- Fix OS: RHEL 9 currently says ``404 Image not found``. Has the image moved?
- Fix OS: Ubuntu jammy interrupts with interactive question.
  ``Daemons using outdated libraries » Which services should be restarted?``
- Probing the HTTP port 4200 of CrateDB instantly after starting currently
  still responds with one of::

      HTTP/1.1 400 Bad Request
      HTTP/1.1 503 Service Unavailable

  Improve!


.. _autopkgtest: https://www.freedesktop.org/wiki/Software/systemd/autopkgtest/
.. _report back: https://github.com/cicerops/racker/issues
