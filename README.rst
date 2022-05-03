#######
postroj
#######



*****
About
*****

An experimental harness tool based on ``systemd-nspawn``. At the same time, a
tribute to the authors and contributors of GNU, Linux, systemd, VirtualBox,
Vagrant, Docker, and all pieces in between.


********
Features
********

``postroj`` is ...

- A managed runtime harness for testing software packages and similar purposes,
  in different environments.

- A lightweight wrapper around ``systemd-nspawn`` to provide container
  environments with ``systemd``.

- A lightweight wrapper around ``vagrant`` to provide convenient access to all
  things needing a full VM, like running Windows on Linux or macOS.



*****
Setup
*****

::

    apt-get update
    apt-get install --yes systemd-container skopeo umoci python3-pip python3-venv
    python3 -m venv .venv
    source .venv/bin/activate
    pip install postroj --upgrade


********
Synopsis
********

::

    python -m postroj.image
    python -m postroj.container
    python -m postroj.probe


**********
Background
**********

Lennart Poettering identifies three pillars of containers [1]:

- Resource bundling
- Sandboxing
- Delivery

See also [2,3,4], where Lennart Poettering and Kai Sievers outline their vision
of systemd as a platform for running systems and their focus on containers.

``systemd`` already provides a stack of features in the area of *resource
bundling* and *sandboxing*. ``postroj`` might fill some gaps on the *delivery*
aspects.

| [1] https://invidious.fdn.fr/watch?v=sqhojVPr7xM
| [2] https://invidious.fdn.fr/watch?v=s7LlUs5D9p4
| [3] https://invidious.fdn.fr/watch?v=6Q_iTG6_EF4
| [4] https://invidious.fdn.fr/watch?v=_obJr3a_2G8


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


*******
Details
*******

- The managed environment used by postroj is stored at ``/var/lib/postroj``.
  In this manner, it completely gets out of the way of any other machine images
  located at ``/var/lib/machines``. Thus, images created by postroj images will
  not be listed with ``machinectl list-images``.

- Activated filesystem images are located at ``/var/lib/postroj/images``.

- Machine names for spawned containers are assembled from the distribution's
  ``fullname`` attribute, prefixed with ``postroj-``.
  Examples: ``postroj-debian-buster``, ``postroj-centos-8``.
