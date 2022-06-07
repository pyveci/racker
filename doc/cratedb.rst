#######################################
Using Racker and Postroj for CrateDB CI
#######################################


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


*************
Prerequisites
*************

When creating the "Windows Docker Machine" virtual machine, the program will
configure it to use 6 VPUs and 6144 MB system memory.

In order to adjust those values, use these environment variables before
invoking the later commands::

    export RACKER_VM_VCPUS=12
    export RACKER_VM_MEMORY=8192

If you want to adjust the values after the initial deployment, you will have to
reset the "Windows Docker Machine" installation directory. For example, it is:

- On Linux: ``/root/.local/state/racker/windows-docker-machine``
- On macOS: ``/Users/amo/Library/Application Support/racker/windows-docker-machine``



**********
racker run
**********

Purpose: Invoke programs in a Java/OpenJDK environment, within a
virtualized/dockerized Windows installation.

Run the CrateDB test suite on OpenJDK 18 (Eclipse Temurin)::

    time racker run --rm --platform=windows/amd64 eclipse-temurin:18-jdk \
        "sh -c 'mkdir /c/src; cd /c/src; git clone https://github.com/crate/crate --depth=1; cd crate; ./gradlew --no-daemon --parallel -PtestForks=2 :server:test -Dtests.crate.run-windows-incompatible=false --stacktrace'"

Invoke a Java command prompt (JShell) with OpenJDK 18::

    racker run -it --rm --platform=windows/amd64 eclipse-temurin:18-jdk jshell
    System.out.println("OS: " + System.getProperty("os.name") + ", version " + System.getProperty("os.version"))
    System.out.println("Java: " + System.getProperty("java.vendor") + ", version " + System.getProperty("java.version"))


****************
postroj pkgprobe
****************


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
.. _report back: https://github.com/pyveci/racker/issues
