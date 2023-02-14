########
Research
########

.. note::

    Just some random notes.


General
=======

- Sources of ``nspawn``: https://github.com/systemd/systemd/tree/main/src/nspawn

- systemd-nspawn rootless: https://lists.freedesktop.org/archives/systemd-devel/2015-February/028024.html

- bubblewrap & Co.

  - https://github.com/containers/bubblewrap
  - https://github.com/projectatomic/bwrap-oci

- Check Lima. -- https://github.com/lima-vm/lima

- Check if and how ready-made Vagrant images can be used for providing rootfs.

- Check how to extract and run Lambda Layers.
  -- https://github.com/mthenw/awesome-layers

- Check KIWI

  - https://github.com/OSInside/kiwi

- Look into Kata Containers

  - https://github.com/kata-containers/kata-containers
  - https://virtio-fs.gitlab.io/

- Look into UTM

  - https://github.com/utmapp/UTM
  - https://mac.getutm.app/

- Look into Quickemu

  - https://github.com/quickemu-project

- How can postroj be combined with Packer and/or Buildah?

- Running systemd within a Docker Container

  - https://developers.redhat.com/blog/2014/05/05/running-systemd-within-docker-container
  - https://lwn.net/Articles/676831/
  - https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container
  - https://developers.redhat.com/blog/2019/04/24/how-to-run-systemd-in-a-container
  - https://medium.com/swlh/docker-and-systemd-381dfd7e4628

- Look at tini. -- https://github.com/krallin/tini

- Portable, encrypted home directories.

  - https://www.heise.de/newsticker/meldung/Systemd-Lennart-Poettering-moechte-das-Home-Verzeichnis-modernisieren-4536581.html
  - https://www.heise.de/newsticker/meldung/FOSDEM-Systemd-und-die-Neuerfindung-der-Home-Verzeichnisse-4651663.html

- Windows

  - https://github.com/containers/podman/issues/8136
  - https://github.com/geoffreysmith/boring-euclid
  - https://docs.microsoft.com/en-us/virtualization/windowscontainers/

- Look at ``multipass``. -- https://multipass.run/

- Look at BuildStream

  - https://github.com/apache/buildstream/
  - https://docs.buildstream.build/

- Pacstall and Axel

  - https://github.com/pacstall/pacstall
  - https://github.com/axel-download-accelerator/axel

- https://snapcraft.io/install/starship/fedora

- PID 1

  - https://about.gitlab.com/blog/2022/05/17/how-we-removed-all-502-errors-by-caring-about-pid-1-in-kubernetes/


Misc links
==========
- Virtualization made Easy: https://linuxgazette.net/144/howell.html
- Virtualizing without Virtualizing: https://linuxgazette.net/150/kapil.html
- Schroot

  - https://wiki.debian.org/Schroot
  - https://web.archive.org/web/20200927080600/https://debian-administration.org/article/566/schroot_-_chroot_for_any_users
- User-mode Linux: http://user-mode-linux.sourceforge.net/



The LXC container driver
========================

    The libvirt LXC driver has no dependency on the LXC userspace tools hosted on
    sourceforge.net. It directly utilizes the relevant kernel features to build the
    container environment. This allows for sharing of many libvirt technologies
    across both the QEMU/KVM and LXC drivers. In particular sVirt for mandatory
    access control, auditing of operations, integration with control groups and
    many other features.

    -- https://libvirt.org/drvlxc.html

    Containers on Linux usually means either using LXC or libvirt LXC, he said.
    Those two are, he stressed, totally separate projects despite the name
    similarity. Both are quite different from the well-known (and understood)
    chroot command (and underlying system call).

    -- https://lwn.net/Articles/572957/



What about other computing architectures?
=========================================

- https://changelog.com/posts/the-big-idea-around-unikernels
- https://mirage.io/
- https://nanos.org/
- https://www.inovex.de/de/blog/containers-docker-containerd-nabla-kata-firecracker/


How to bring it to macOS and Windows?
=====================================

- https://mirage.io/blog/2022-04-06.vpnkit
- https://www.docker.com/blog/how-docker-desktop-networking-works-under-the-hood/
- https://github.com/moby/vpnkit
- https://github.com/moby/hyperkit
- https://github.com/containers/podman/issues/8452
- https://boot2podman.github.io/

  - https://boot2podman.github.io/2021/01/24/reboot-new-project.html
  - https://floelinux.github.io/
  - https://podman.io/community/meeting/notes/2021-04-06/


Rootless containers
===================

- https://github.com/containers/podman#rootless
- https://github.com/rootless-containers/slirp4netns
- https://github.com/rootless-containers/bypass4netns
- https://medium.com/nttlabs/accelerating-rootless-container-network-29d0e908dda4
- https://github.com/rootless-containers/rootlesskit
- https://github.com/giuseppe/become-root


Other smart testing harnesses
=============================

- https://github.com/coreos/coreos-assembler/blob/main/docs/kola.md


Unikernels
==========

- https://www.inovex.de/de/blog/containers-docker-containerd-nabla-kata-firecracker/
- https://mirage.io/docs/hello-world


Kubernetes
==========

- https://blog.tilt.dev/2021/03/18/kubernetes-is-so-simple.html
- https://github.com/kubernetes-sigs/kind
- https://www.docker.com/blog/welcome-tilt-fixing-the-pains-of-microservice-development-for-kubernetes/


Virtualized macOS
=================

- KVM: https://github.com/kholia/OSX-KVM
- VirtualBox: https://github.com/myspaghetti/macos-virtualbox


Ignite / Firecracker
====================

- https://github.com/weaveworks/ignite


Devbox
======

- https://github.com/jetpack-io/devbox

Bocker
======

- https://github.com/p8952/bocker
