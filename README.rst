#######
postroj
#######



*****
About
*****

An experimental harness tool based on `systemd-nspawn`_  containers.
At the same time, a tribute to the authors and contributors of GNU, Linux,
systemd, VirtualBox, Vagrant, Docker, Python and more.

``postroj`` is ...

- A runtime harness for testing software packages and similar purposes, in
  different environments, mostly run headless and non-interactive.

- A lightweight wrapper around ``systemd-nspawn`` to provide container
  environments with ``systemd``.

- A lightweight wrapper around ``vagrant`` to provide convenient access to all
  things needing a full VM, like running Windows on Linux or macOS.


**********
Background
**********

Lennart Poettering identifies three pillars of containers [1]:

- Resource bundling
- Sandboxing
- Delivery

See also [2], where Lennart Poettering and Kai Sievers outline their vision
of systemd as a platform for running systems and their focus on containers.

``systemd`` already provides a stack of features in the areas of *resource
bundling* and *sandboxing* [1]. ``postroj`` might fill some gaps on the
*delivery* aspects.

[3] outlines how systemd-nspawn was conceived to aid in testing and debugging
systemd and [4] is the latest overview of systemd in 2018. From a user's
perspective, `Running containers with systemd-nspawn`_ has a concise walkthrough.

| [1] `Containers without a Container Manager, with systemd`_ (2018)
| [2] `Lennart Poettering und Kay Sievers über Systemd`_ (2014)
| [3] `Systemd-Nspawn is Chroot on Steroids`_ (2013)
| [4] `NYLUG Presents - Lennart Poettering on Systemd in 2018`_
| [5] `Running containers with systemd-nspawn`_


*****
Setup
*****

Install prerequisites::

    apt-get update
    apt-get install --yes systemd-container skopeo umoci python3-pip python3-venv


Install postroj::

    python3 -m venv .venv
    source .venv/bin/activate
    pip install git+https://github.com/cicerops/postroj --upgrade

.. note::

    If you are not running Linux on your workstation, the `postroj sandbox
    installation`_ documentation outlines how to run this program within
    a virtual machine using Vagrant.


*****
Usage
*****

Basic commands::

    # List available images.
    postroj list-images

    # Acquire rootfs image.
    postroj pull debian-bullseye

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

    # Run two probes that need installing a 3rd party package beforehand.

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

    real    0m0.610s
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

- | Q: Does the program need root privileges?
  | A: Yes, the program must be invoked with ``root`` or corresponding ``sudo`` privileges.

- | Q: Where does postroj store its data?
  | A: The managed environment used by postroj is stored at ``/var/lib/postroj``.
       In this manner, it completely gets out of the way of any other machine images
       located at ``/var/lib/machines``. Thus, images created by postroj images will
       not be listed by ``machinectl list-images``.
  | A: The download cache is located at ``/var/cache/postroj/downloads``.

- | Q: Where are the filesystem images stored?
  | A: Activated filesystem images are located at ``/var/lib/postroj/images``.

- | Q: How are machine names assigned?
  | A: Machine names for spawned containers are automatically assigned.
       The name will be assembled from the distribution's ``fullname`` attribute,
       prefixed with ``postroj-``.
       Examples: ``postroj-debian-buster``, ``postroj-centos-8``.

- | Q: How large are filesystem images?
  | A: postroj prefers to use "slim" variants of filesystem images, aiming to
       only use artefacts with download sizes < 100 MB.

- | Q: Are container disks ephemeral?
  | A: Yes, by default, all container images will be ephemeral, i.e. all changes to
       them are volatile.


.. _machinectl: https://www.freedesktop.org/software/systemd/man/machinectl.html
.. _systemd-nspawn: https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
.. _systemd-run: https://www.freedesktop.org/software/systemd/man/systemd-run.html

.. _postroj sandbox installation: https://github.com/cicerops/postroj/blob/main/doc/sandbox.rst
.. _Running containers with systemd-nspawn: https://janma.tk/2019-10-13/systemd-nspawn/

.. _Containers without a Container Manager, with systemd: https://invidious.fdn.fr/watch?v=sqhojVPr7xM
.. _Systemd-Nspawn is Chroot on Steroids: https://invidious.fdn.fr/watch?v=s7LlUs5D9p4
.. _Lennart Poettering und Kay Sievers über Systemd: https://invidious.fdn.fr/watch?v=6Q_iTG6_EF4
.. _NYLUG Presents - Lennart Poettering on Systemd in 2018: https://invidious.fdn.fr/watch?v=_obJr3a_2G8
