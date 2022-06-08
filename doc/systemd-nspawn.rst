############################
systemd-nspawn in a nutshell
############################


*******
Preface
*******

This document has been written in the spirit of addressing some details of
`Docker Considered Harmful`_ and `Systemd vs. Docker`_.


*****
About
*****

    ``systemd-nspawn`` may be used to run a command or OS in a light-weight
    namespace container. In many ways it is similar to ``chroot``, but more
    powerful since it fully virtualizes the file system hierarchy, as well as
    the process tree, the various IPC subsystems and the host and domain name.

    It is primarily intended for use in development, experimenting, debugging,
    instrumentation, testing and building of software.

    It can easily be used to start containers capable of booting up a complete
    and unmodified Linux distribution inside as normal system services.


************
Introduction
************

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


*******
Details
*******

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


.. _Changing Roots: http://0pointer.de/blog/projects/changing-roots.html
.. _Creating containers with systemd-nspawn: https://lwn.net/Articles/572957/
.. _Docker Considered Harmful: https://catern.com/docker.html
.. _OS containers: http://0pointer.net/blog/systemd-for-administrators-part-xxi.html
.. _Running containers with systemd-nspawn: https://janma.tk/2019-10-13/systemd-nspawn/
.. _systemd: https://www.freedesktop.org/wiki/Software/systemd/
.. _systemd for administrators: https://www.freedesktop.org/wiki/Software/systemd/#thesystemdforadministratorsblogseries
.. _Systemd vs. Docker: https://lwn.net/Articles/676831/

.. _Containers without a Container Manager, with systemd: https://invidious.fdn.fr/watch?v=sqhojVPr7xM
.. _Lennart Poettering und Kay Sievers über Systemd: https://invidious.fdn.fr/watch?v=6Q_iTG6_EF4
.. _NYLUG Presents - Lennart Poettering on Systemd in 2018: https://invidious.fdn.fr/watch?v=_obJr3a_2G8
.. _Systemd-Nspawn is Chroot on Steroids: https://invidious.fdn.fr/watch?v=s7LlUs5D9p4
