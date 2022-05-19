######
Racker
######

.. container::

    *Operating system containers for humans and machines.*

    - **Documentation**: https://github.com/cicerops/racker
    - **Source code**: https://github.com/cicerops/racker
    - **PyPI**: https://pypi.org/project/racker/

|

.. image:: https://img.shields.io/badge/systemd-239%20and%20newer-blue.svg
    :target: https://github.com/systemd/systemd
    :alt: systemd System and Service Manager

.. image:: https://img.shields.io/pypi/pyversions/racker.svg
    :target: https://pypi.org/project/racker/
    :alt: Python version

.. image:: https://img.shields.io/pypi/v/racker.svg
    :target: https://pypi.org/project/racker/
    :alt: Version

.. image:: https://img.shields.io/pypi/status/racker.svg
    :target: https://pypi.org/project/racker/
    :alt: Maturity status

.. image:: https://github.com/cicerops/racker/workflows/Tests/badge.svg
    :target: https://github.com/cicerops/racker/actions?workflow=Tests
    :alt: Test suite status

.. image:: https://codecov.io/gh/cicerops/racker/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/cicerops/racker
    :alt: Test suite code coverage

.. image:: https://img.shields.io/pypi/l/racker.svg
    :target: https://pypi.org/project/racker/
    :alt: License

.. image:: https://img.shields.io/pypi/dm/racker.svg?label=PyPI%20downloads
    :target: https://pypi.org/project/racker/
    :alt: PyPI downloads


----


*****
About
*****

An experimental harness tool based on `systemd`_ and `systemd-nspawn`_, to run
`operating system containers <OS containers_>`_, in the spirit of addressing some details of
`Docker Considered Harmful`_ and `Systemd vs. Docker`_.

At the same time, it is a tribute to the authors and contributors of GNU, Linux,
systemd, Python, VirtualBox, Vagrant, Docker, and more.

Most people running Linux probably want to use `Podman`_ these days. For more
background, enjoy reading `Container wars`_ and `Container Tools Guide`_.

Racker is ...
=============

- A runtime harness for testing software packages and similar purposes, in
  different environments, mostly run headless and non-interactively.

- A lightweight wrapper around ``systemd-nspawn`` to provide and launch
  container environments for/with ``systemd``.

- A lightweight wrapper around ``vagrant`` to provide convenient access to all
  things needing a full VM, like running Windows on Linux or macOS.


Comparison with similar tools
=============================

The aims of Racker are very similar to `Distrobox`_ and `Toolbox`_. However,
there are also some differences.

- Racker is currently based on `systemd-nspawn`_ instead of `Docker`_ or
  `Podman`_.
- Racker can invoke any kind of container payload, but strongly focuses on
  running `OS containers`_ aka. `OS-level virtualization`_, using `systemd`_
  as init process.
- Racker aims to provide concise usability by folding its usage into a single
  command.
- The acquisition and provisioning of operating system images does not need any
  special preparation steps, those are handled by Racker on the fly.

See also `Comparison with similar tools - more details`_.


About ``systemd-nspawn``
========================

As a general introduction, we recommend to read an introductory article on LWN
as well as two installments of the `systemd for administrators`_ blog series:

- `Creating containers with systemd-nspawn`_

    - Lennart Poettering spoke about a mostly unknown utility that ships with it:
      systemd-nspawn. The tool started as a debugging aid for systemd development,
      but has many more uses than just that, he said. [...]
    - The idea was to write a tool that does much of what LXC and libvirt LXC do,
      but is easier to use. It is targeted at "building, testing, debugging, and
      profiling", not at deployment. systemd-nspawn uses the same kernel APIs that
      the other two tools use, but is not a competitor to them because it is not
      targeted at running in a production environment. [...]

- `Changing Roots`_

    - As administrator or developer sooner or later you'll encounter
      ``chroot()`` environments. [...]
    - File system namespaces are in fact a better replacement for ``chroot()``
      in many many ways. [...]
    - More importantly however systemd comes out-of-the-box with the
      ``systemd-nspawn`` tool which acts as ``chroot`` on steroids: it makes
      use of file system and PID namespaces to boot a simple lightweight
      container on a file system tree. [...]

- `OS containers`_

    - We'll focus on OS containers here, i.e. the case where an init system
      runs inside the container, and the container hence in most ways appears
      like an independent system of its own. [...]
    - We use systemd-nspawn extensively when developing systemd. [...]


Lennart Poettering, the author of `systemd`_, identifies three main pillars of
containers [1]:

- Resource bundling
- Sandboxing
- Delivery

At [2] Lennart Poettering and Kai Sievers outline their vision of systemd as a
*platform for running systems* and their focus on containers in 2014. Fast
forward to 2022, and everything is pretty much there. ``systemd`` now provides
a plethora of features for containerization, specifically for *resource
bundling* and *sandboxing* [1].

[3] outlines how systemd-nspawn was originally conceived to aid in testing and
debugging systemd, [4] is the latest overview of systemd in 2018.
For approaching ``systemd-nspawn`` from a user's perspective, a concise
introductory walkthrough can be found at [5].

The most important bits being covered by the systemd software family already,
Racker tries to fill some gaps on the *delivery* aspects.

|
| [1] `Containers without a Container Manager, with systemd`_ (2018)
| [2] `Lennart Poettering und Kay Sievers über Systemd`_ (2014)
| [3] `Systemd-Nspawn is Chroot on Steroids`_ (2013)
| [4] `NYLUG Presents - Lennart Poettering on Systemd in 2018`_
| [5] `Running containers with systemd-nspawn`_ (2019)


*****
Setup
*****

Install prerequisites::

    apt-get update
    apt-get install --yes systemd-container skopeo umoci python3-pip python3-venv


Install Racker::

    python3 -m venv .venv
    source .venv/bin/activate
    pip install racker --upgrade

To install the latest development version, use this command instead::

    pip install git+https://github.com/cicerops/racker --upgrade

.. note::

    If you are not running Linux on your workstation, the `Racker sandbox
    installation`_ documentation outlines how to run this program within
    a virtual machine using Vagrant.



*****
Usage
*****


Racker
======

The ``racker`` program aims to resemble the semantics of Docker by providing a
command line interface compatible with the ``docker`` command.

::

    # Invoke the vanilla Docker `hello-world` image.
    # FIXME: Does not work yet.
    # racker run -it --rm hello-world /hello
    # racker run -it --rm quay.io/podman/hello

    # Acquire rootfs images.
    racker pull debian:bullseye-slim
    racker pull fedora:37

    # Launch an interactive shell.
    racker run -it --rm debian:bullseye-slim bash
    racker run -it --rm fedora:37 bash
    racker run -it --rm docker://registry.access.redhat.com/ubi8/ubi-minimal /bin/bash
    racker run -it --rm docker://quay.io/centos/centos:stream9 bash

    # Launch a single command.
    racker run -it --rm debian:11-slim hostnamectl
    racker run -it --rm opensuse/tumbleweed hostnamectl
    racker run -it --rm ubuntu:jammy /bin/cat /etc/os-release
    racker run -it --rm registry.suse.com/suse/sle15 /bin/cat /etc/os-release
    racker run -it --rm registry.suse.com/bci/bci-base:15.4 /bin/cat /etc/os-release
    racker run -it --rm docker://ghcr.io/jpmens/mqttwarn-standard /usr/bin/hostnamectl

    # Verbose mode.
    racker --verbose run -it --rm fedora:37 hostnamectl

    # Use stdin and stdout, with timing.
    time echo "hello world" | racker run -it --rm fedora:37 cat /dev/stdin > hello
    cat hello


Postroj
=======

The idea behind ``postroj`` is to provide an entrypoint to a command line
interface implementing actions that don't fit into ``racker``, mostly having a
more high-level character.

Currently, ``postroj pkgprobe`` implements a flavor of *full system
integration/acceptance testing* in order to test the soundness of actual
installed binary distribution packages, in the spirit of `autopkgtest`_.

To do so, it implements the concept of *curated* operating system images,
whose labels have a different layout than labels of Docker filesystem images.

Getting started::

    # List available images.
    postroj list-images

    # Acquire images for curated operating systems.
    postroj pull debian-bullseye
    postroj pull fedora-37

    # Acquire rootfs images for all available distributions.
    postroj pull --all

    # Run a self test procedure, invoking `hostnamectl` on all containers.
    postroj selftest hostnamectl

Package testing::

    # Run a self test procedure, invoking example probes on all containers.
    postroj selftest pkgprobe

    # Run two basic probes on different operating systems.
    postroj pkgprobe --image=debian-bullseye --check-unit=systemd-journald
    postroj pkgprobe --image=fedora-37 --check-unit=systemd-journald
    postroj pkgprobe --image=archlinux-20220501 --check-unit=systemd-journald

    # Run probes that need to install a 3rd party package beforehand.

    postroj pkgprobe \
        --image=debian-stretch \
        --package=http://ftp.debian.org/debian/pool/main/w/webfs/webfs_1.21+ds1-12_amd64.deb \
        --check-unit=webfs \
        --check-network=http://localhost:8000

    postroj pkgprobe \
        --image=debian-bullseye \
        --package=https://dl.grafana.com/oss/release/grafana_8.5.1_amd64.deb \
        --check-unit=grafana-server \
        --check-network=http://localhost:3000

    postroj pkgprobe \
        --image=centos-8 \
        --package=https://dl.grafana.com/oss/release/grafana-8.5.1-1.x86_64.rpm \
        --check-unit=grafana-server \
        --check-network=http://localhost:3000


***********
Performance
***********

A SuT which just uses a dummy probe ``/bin/systemctl is-active systemd-journald``
on Debian 10 "buster" cycles quite fast, essentially demonstrating that the
overhead of environment setup/teardown is insignificant.

::

    time postroj pkgprobe --image=debian-buster --check-unit=systemd-journald

    real    0m0.589s
    user    0m0.161s
    sys     0m0.065s

On a cold system, where the filesystem image would need to be acquired before
spawning the container, it's still fast enough::

    time postroj pkgprobe --image=debian-bookworm --check-unit=systemd-journald

    real    0m22.582s
    user    0m8.572s
    sys     0m3.136s


*********************
Questions and answers
*********************

- | Q: How does it work?
  | A: Directly quoting the `machinectl`_ documentation here:

    Note that `systemd-run`_ with its ``--machine=`` switch may be used in place of the
    ``machinectl shell`` command, and allows non-interactive operation, more detailed and
    low-level configuration of the invoked unit, as well as access to runtime and exit
    code/status information of the invoked shell process.

    In particular, use ``systemd-run``'s ``--wait`` switch to propagate exit status information
    of the invoked process. Use ``systemd-run``'s ``--pty`` switch for acquiring an interactive
    shell, similar to ``machinectl shell``. In general, ``systemd-run`` is preferable for
    scripting purposes.

- | Q: How does it work, really?
  | A: Roughly speaking...

  - `skopeo`_ and `umoci`_ are used to acquire root filesystem images from Docker image registries.
  - `systemd-nspawn`_ is used to run commands on root filesystems for provisioning them.
  - Containers are started with ``systemd-nspawn --boot``.
  - `systemd-run`_ is used to interact with running containers.
  - `machinectl`_ is used to terminate containers.

- | Q: How is this project related with Docker?
  | A: The runtime is completely independent of Docker, it is solely based on
       ``systemd-nspawn`` containers instead. However, root filesystem images can be
       pulled from Docker image registries in the spirit of `machinectl pull-dkr`_.
       Other than this, the ``racker`` command aims to be a drop-in replacement for
       its corresponding ``docker`` counterpart.

- | Q: Do I need to have Docker installed on my machine?
  | A: No, Racker works without Docker.

- | Q: How are machine names assigned?
  | A: Machine names for spawned containers are automatically assigned.
       The name will be assembled from the distribution's ``fullname`` attribute,
       prefixed with ``postroj-``.
       Examples: ``postroj-debian-buster``, ``postroj-centos-8``.

- | Q: Does the program need root privileges?
  | A: Yes, the program currently must be invoked with ``root`` or corresponding
       ``sudo`` privileges. However, it would be sweet to enable unprivileged
       operations soon. ``systemd-nspawn`` should be able to do it, using
       ``--private-users`` or ``--user``?

- | Q: Where does the program store its data?
  | A: Data is stored at ``/var/lib/postroj``.
       In this manner, it completely gets out of the way of any other images, for
       example located at ``/var/lib/machines``. Thus, any images created or managed
       by Racker will not be listed by ``machinectl list-images``.
  | A: The download cache is located at ``/var/cache/postroj/downloads``.

- | Q: Where are the filesystem images stored?
  | A: Activated filesystem images are located at ``/var/lib/postroj/images``.

- | Q: How large are curated filesystem images?
  | A: The preference for curated filesystem images is to use their corresponding
       "slim" variants where possible, aiming to only use artefacts with download
       sizes < 100 MB.

- | Q: Are container disks ephemeral?
  | A: Yes, by default, all container images will be ephemeral, i.e. all changes to
       them are volatile.


***************
Troubleshooting
***************

*It's always the cable. ;]*

1. If you see that your container might not have network access, make sure to
   provide a valid DNS configuration in your host's ``/etc/resolv.conf``.
   When in doubt, please add ``nameserver 9.9.9.9`` as the first entry.


.. _autopkgtest: https://www.freedesktop.org/wiki/Software/systemd/autopkgtest/
.. _Changing Roots: http://0pointer.de/blog/projects/changing-roots.html
.. _Comparison with similar tools - more details: https://github.com/cicerops/racker/blob/main/doc/comparison.rst
.. _Container Tools Guide: https://github.com/containers/buildah/tree/main/docs/containertools
.. _Container wars: https://github.com/cicerops/racker/blob/main/doc/research/container-wars.rst
.. _Creating containers with systemd-nspawn: https://lwn.net/Articles/572957/
.. _Distrobox: https://github.com/89luca89/distrobox
.. _Docker: https://github.com/docker/
.. _Docker Considered Harmful: https://catern.com/docker.html
.. _machinectl: https://www.freedesktop.org/software/systemd/man/machinectl.html
.. _machinectl pull-dkr: https://github.com/cicerops/racker/blob/main/doc/research/machinectl-pull-dkr.rst
.. _nerdctl: https://github.com/containerd/nerdctl
.. _OS containers: http://0pointer.net/blog/systemd-for-administrators-part-xxi.html
.. _OS-level virtualization: https://wiki.debian.org/SystemVirtualization#OS-level_virtualization
.. _Podman: https://podman.io/
.. _Racker sandbox installation: https://github.com/cicerops/racker/blob/main/doc/sandbox.rst
.. _Running containers with systemd-nspawn: https://janma.tk/2019-10-13/systemd-nspawn/
.. _skopeo: https://github.com/containers/skopeo
.. _systemd: https://www.freedesktop.org/wiki/Software/systemd/
.. _systemd-nspawn: https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
.. _systemd-run: https://www.freedesktop.org/software/systemd/man/systemd-run.html
.. _systemd for administrators: https://www.freedesktop.org/wiki/Software/systemd/#thesystemdforadministratorsblogseries
.. _Systemd vs. Docker: https://lwn.net/Articles/676831/
.. _Toolbox: https://containertoolbx.org/
.. _umoci: https://github.com/opencontainers/umoci

.. _Containers without a Container Manager, with systemd: https://invidious.fdn.fr/watch?v=sqhojVPr7xM
.. _Lennart Poettering und Kay Sievers über Systemd: https://invidious.fdn.fr/watch?v=6Q_iTG6_EF4
.. _NYLUG Presents - Lennart Poettering on Systemd in 2018: https://invidious.fdn.fr/watch?v=_obJr3a_2G8
.. _Systemd-Nspawn is Chroot on Steroids: https://invidious.fdn.fr/watch?v=s7LlUs5D9p4
