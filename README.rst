#######
postroj
#######



*****
About
*****

An experimental harness tool based on `systemd-nspawn`_ and `machinectl`_.
At the same time, a tribute to the authors and contributors of GNU, Linux,
systemd, VirtualBox, Vagrant, Docker, Python and more.

``postroj`` is ...

- A managed runtime harness for testing software packages and similar purposes,
  in different environments.

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
systemd and [4] is the latest overview of systemd in 2018.

| [1] `Containers without a Container Manager, with systemd`_ (2018)
| [2] `Lennart Poettering und Kay Sievers über Systemd`_ (2014)
| [3] `Systemd-Nspawn is Chroot on Steroids`_ (2013)
| [4] `NYLUG Presents - Lennart Poettering on Systemd in 2018`_



*****
Setup
*****

::

    apt-get update
    apt-get install --yes systemd-container skopeo umoci python3-pip python3-venv
    python3 -m venv .venv
    source .venv/bin/activate
    pip install postroj --upgrade


*****
Usage
*****

::

    # List available distribution images
    postroj list-images

    # Acquire specific distribution image
    postroj pull debian-bullseye

Some demo programs::

    # Provide rootfs container filesystem images for all available distributions.
    python -m postroj.image

    # Demo: Invoke `hostnamectl` on a Debian buster container.
    time python -m postroj.container

    # Demo: Invoke two demo probes on all available distributions.
    python -m postroj.probe

Package testing::

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

    time python -m postroj.container

    real    0m0.446s
    user    0m0.060s
    sys     0m0.034s


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


.. _machinectl: https://www.freedesktop.org/software/systemd/man/machinectl.html
.. _systemd-nspawn: https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
.. _systemd-run: https://www.freedesktop.org/software/systemd/man/systemd-run.html

.. _Containers without a Container Manager, with systemd: https://invidious.fdn.fr/watch?v=sqhojVPr7xM
.. _Systemd-Nspawn is Chroot on Steroids: https://invidious.fdn.fr/watch?v=s7LlUs5D9p4
.. _Lennart Poettering und Kay Sievers über Systemd: https://invidious.fdn.fr/watch?v=6Q_iTG6_EF4
.. _NYLUG Presents - Lennart Poettering on Systemd in 2018: https://invidious.fdn.fr/watch?v=_obJr3a_2G8
