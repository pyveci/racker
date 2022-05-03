#######
postroj
#######



*****
About
*****

A universal harness tool. At the same time, a tribute to the developers of
Linux, GNU, systemd, VirtualBox, Vagrant, Docker and all pieces in between.


********
Features
********

``postroj`` is ...

- A managed runtime harness for testing software packages and similar purposes,
  in different environments.

- A lightweight wrapper around ``vagrant`` to provide convenient access to all
  things needing a full VM, like running Windows on Linux or macOS.

- A lightweight wrapper around ``systemd-nspawn`` to provide container
  environments with ``systemd``.


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

Lennart Poettering identifies [1] three pillars of containers:

- Resource bundling
- Sandboxing
- Delivery

``systemd`` already provides a stack of features in the area of *resource
bundling* and *sandboxing*. Parts of ``postroj`` might fill some gaps on the
*delivery* aspects.


***********
Performance
***********

A SuT which just uses a dummy probe ``/bin/systemctl is-active systemd-journald``
on Debian 10 "buster" cycles quite fast, essentially demonstrating that the
overhead of environment setup/teardown is insignificant.

::

    time python -m postroj.container

    real    0m0.768s
    user    0m0.082s
    sys     0m0.043s


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




[1] https://www.youtube.com/watch?v=s7LlUs5D9p4
