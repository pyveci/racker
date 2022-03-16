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

- A lightweight wrapper around ``systemd-nspawn`` to provide container
  environments with ``systemd``.



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



********
Synopsis
********

A SuT which just uses a dummy probe ``/bin/systemctl is-active systemd-journald``
cycles quite fast, essentially demonstrating that the overhead of environment
setup/teardown is insignificant.

::

    time python3 postroj/container.py

    real    0m0.913s
    user    0m0.707s
    sys     0m0.844s



*******
Details
*******

- The managed environment used by postroj is stored within ``/var/lib/postroj``.
  In this manner, it gets out of the way of other machine images stored at
  ``/var/lib/machines``.




[1] https://www.youtube.com/watch?v=s7LlUs5D9p4
