##############
Container wars
##############

.. note::

    Just some random notes.


************
Introduction
************

Before getting into the details, we can warmly recommend to refresh common
container knowledge by reading `A Practical Introduction to Container
Terminology`_. While technically not equally deep, `Welcome To The Container
Jungle`_ provides other interesting insights.

However, both articles, written in 2018 resp. 2020, don't ever mention Podman_.


******
Docker
******

    Let’s start with Docker, as it’s the container runtime most people know. In
    fact, I think Docker profited somewhat from the Kleenex effect, where a
    brand name is genericized—in this case, some people tend to think that Docker
    equals container. This is not the case, it was just one of the earlier famous
    solutions for containerization. When it initially came out in 2013, Docker
    was a monolithic software that had all the qualities of a high-level container
    runtime.

    -- https://www.inovex.de/de/blog/containers-docker-containerd-nabla-kata-firecracker/


************
Rocket (rkt)
************


References
==========
- https://www.ctl.io/developers/blog/post/what-is-rocket-and-how-its-different-than-docker/
- https://www.redhat.com/en/topics/containers/what-is-rkt
- https://github.com/rkt/rkt/issues/1585
- https://github.com/rkt/rkt/issues/2065
- https://github.com/rkt/rkt/issues/3368
- https://web.archive.org/web/20190716105325/https://coreos.com/blog/qa-with-lennart-systemd.html
- https://twitter.com/lucabruno/status/1232250467989807104
- https://github.com/rkt/rkt/issues/3912
- https://github.com/rkt/rkt/issues/3946
- https://github.com/rkt/rkt/issues/4024
- https://www.cncf.io/announcements/2017/03/29/cloud-native-computing-foundation-becomes-home-pod-native-container-engine-project-rkt/
- https://entwickler.de/docker/projekt-rkt-offiziell-eingestellt-eine-reminiszenz-an-eine-container-engine
- https://www.golem.de/news/nach-core-os-uebernahme-entwicklung-von-container-engine-rkt-beendet-2003-146968.html
- https://github.com/kinvolk
- https://news.ycombinator.com/item?id=22249403


Quotes
======

    Die Nische, die ``rkt`` bediente, wurde ohnehin immer kleiner: Das eigene Format
    für Container-Abbilder ``AppC`` setzte sich nie durch, motivierte aber
    indirekt Docker Inc., gemeinsame Standards ins Leben zu rufen. Als Daemon-freie
    Alternative zu Docker konnte sich ``rkt`` ebenfalls nicht positionieren.
    Die meisten Anwender, die Container ohne Daemon ausführen wollen, setzen auf
    Podman – vor allem solche aus der Red-Hat- und Fedora-Szene.

    Die Entwickler von Podman haben unterdessen eine neue Funktion im Alpha-Status
    vorgestellt: ein HTTP-API, das weitgehend mit dem des Docker-Daemons kompatibel
    ist. Zuvor hatte sich Podman ein eigenes API-Format auf Basis des
    Varlink-Standards ausgedacht.

    -- https://www.heise.de/select/ct/2020/8/2006310084759623163 (8/2020)


******
Podman
******

Introduction
============

    Podman is a daemonless, open source, Linux native tool designed to make it
    easy to find, run, build, share and deploy applications using Open
    Containers Initiative (OCI) Containers and Container Images. Podman provides
    a command line interface (CLI) familiar to anyone who has used the Docker
    Container Engine.

    Most users can simply alias Docker to Podman (``alias docker=podman``)
    without any problems. Similar to other common Container Engines (Docker,
    CRI-O, containerd), Podman relies on an OCI compliant Container Runtime
    (runc, crun, runv, etc) to interface with the operating system and create
    the running containers. This makes the running containers created by
    Podman nearly indistinguishable from those created by any other common
    container engine.

    Containers under the control of Podman can either be run by root or by a
    non-privileged user.

    - https://podman.io/
    - https://docs.podman.io/


Rootless mode
=============

    Podman can be easily run as a normal user, without requiring a setuid binary.
    When run without root, Podman containers use user namespaces to set root in
    the container to the user running Podman. Rootless Podman runs locked-down
    containers with no privileges that the user running the container does not have.

    Any recent Podman release should be able to run rootless without any additional
    configuration, though your operating system may require some additional
    configuration.

    - https://github.com/containers/podman#rootless

    Rootless networking is handled via `slirp4netns`_.


systemd mode
============

    Podman has some sane defaults to run containers, that use systemd internally.
    Docker for example needs some special privileges and mount options to use
    systemd in containers. This is not needed in Podman. The man page (``man
    podman-run``) states:

        ``--systemd=true|false|always``
        Run container in systemd mode. The default is true.

    The value true indicates, that Podman detects if systemd is running in the
    container and will do the heavy lifting for you. This means, Podman will
    set up tmpfs mount points for some directories and set the stop signal to
    SIGRTMIN+3.

    - https://blog.while-true-do.io/podman-systemd-in-containers/

Podman containers as systemd services
=====================================
- https://www.redhat.com/sysadmin/podman-shareable-systemd-services
- https://mohitgoyal.co/2021/06/01/running-containers-as-systemd-services-with-podman/


Podman and Compose
==================
- https://compose-spec.io/
- https://github.com/compose-spec/compose-spec/blob/master/spec.md
- https://github.com/containers/podman-compose
- https://www.redhat.com/sysadmin/podman-docker-compose
- https://www.redhat.com/sysadmin/compose-podman-pods
- https://fedoramagazine.org/manage-containers-with-podman-compose/
- https://fedoramagazine.org/use-docker-compose-with-podman-to-orchestrate-containers-on-fedora/
- https://balagetech.com/convert-docker-compose-services-to-pods/
- https://github.com/containers/podman/issues/9169


Rootless
========
- https://www.redhat.com/sysadmin/rootless-podman-makes-sense
- https://www.redhat.com/sysadmin/rootless-podman
- https://www.redhat.com/sysadmin/behind-scenes-podman
- https://www.redhat.com/sysadmin/user-flag-rootless-containers
- https://www.redhat.com/sysadmin/user-namespaces-selinux-rootless-containers


References
==========

- https://developers.redhat.com/articles/podman-next-generation-linux-container-tools
- https://www.ionos.de/digitalguide/server/knowhow/podman-vs-docker/
- https://mkdev.me/posts/dockerless-part-3-moving-development-environment-to-containers-with-podman
- https://serverfault.com/questions/989509/how-can-i-change-the-oci-runtime-in-podman
- https://www.inovex.de/de/blog/containers-docker-containerd-nabla-kata-firecracker/
- https://wiki.debian.org/Podman
- https://github.com/containers/podman/issues/8452
- https://documentation.suse.com/sle-micro/5.1/html/SLE-Micro-all/article-podman.html
- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html-single/building_running_and_managing_containers/index
- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9-beta/html-single/building_running_and_managing_containers/index
- https://www.redhat.com/sysadmin/improved-systemd-podman
- https://docs.podman.io/en/latest/markdown/podman-auto-update.1.html
- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/building_running_and_managing_containers/assembly_porting-containers-to-systemd-using-podman_building-running-and-managing-containers
- https://developers.redhat.com/blog/2019/01/15/podman-managing-containers-pods
- https://developers.redhat.com/blog/2019/02/21/podman-and-buildah-for-docker-users


*******
nerdctl
*******

nerdctl: Docker-compatible CLI for containerd

    nerdctl is a Docker-compatible CLI for containerd.

    - Same UI/UX as docker
    - Supports Docker Compose (nerdctl compose up)
    - Supports rootless mode, without slirp overhead (`slirp4netns`_ vs. `bypass4netns`_)
    - Supports lazy-pulling (Stargz)
    - Supports encrypted images (ocicrypt)
    - Supports P2P image distribution (IPFS) (*1)
    - Supports container image signing and verifying (cosign)

References
==========
- https://github.com/containerd/nerdctl



**************
systemd-nspawn
**************

- https://unix.stackexchange.com/questions/180161/why-is-systemd-nspawn-not-appropriate-for-production-deployments


********************************
OCI-compatible container engines
********************************


runc
====
- https://github.com/opencontainers/runc


crun
====
- https://github.com/containers/crun
- https://www.redhat.com/sysadmin/introduction-crun


RHEL
====

    The default container runtime in RHEL 8 is ``runc``.
    The default container runtime in RHEL 9 is ``crun``.

    -- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9-beta/html/considerations_in_adopting_rhel_9/assembly_containers_considerations-in-adopting-rhel-9

Misc
====

- https://github.com/eth-cscs/sarus



.. _A Practical Introduction to Container Terminology: https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction
.. _bypass4netns: https://github.com/rootless-containers/bypass4netns
.. _Podman: https://podman.io/
.. _slirp4netns: https://github.com/rootless-containers/slirp4netns
.. _Welcome To The Container Jungle: https://www.inovex.de/de/blog/containers-docker-containerd-nabla-kata-firecracker/
