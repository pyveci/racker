##############
Image delivery
##############

.. note::

    Just some random notes.


************************
OS distribution variants
************************


Classic
=======
- .iso, .raw, .qcow2, etc.


Docker image
============
- https://github.com/marciopaiva/molecule-systemd-images


OSTree
======
- https://ostree.readthedocs.io/
- https://ostreedev.github.io/ostree/
- https://github.com/ostreedev/ostree
- https://ostreedev.github.io/ostree/related-projects/
- https://ostreedev.github.io/ostree/buildsystem-and-repos/
- https://ostree.readthedocs.io/en/stable/manual/repository-management/
- https://github.com/ostreedev/ostree-releng-scripts
- https://github.com/advancedtelematic/treehub
- https://coreos.github.io/rpm-ostree/compose-server/

rpm-ostree
==========
- https://github.com/coreos/rpm-ostree
- https://coreos.github.io/rpm-ostree/
- https://dustymabe.com/2017/08/08/how-do-we-create-ostree-repos-and-artifacts-in-fedora/
- https://pagure.io/pungi-fedora/blob/392bc7589ecff19e91e03cef34265a270514745e/f/fedora.conf#_710-728

deb-ostree
==========
- https://github.com/dbnicholson/deb-ostree-builder

- Endless OS

  - https://community.endlessos.com/t/layered-packages-on-ostree/8895
  - https://github.com/cosimoc/deb-ostree-builder
  - https://debconf17.debconf.org/talks/41/
  - https://support.endlessos.org/en/endless-os/tech-intro

casync
======
- https://moinakg.wordpress.com/2013/06/22/high-performance-content-defined-chunking/
- https://github.com/systemd/casync

- Look into ``casync`` and casync Bundles

  - http://0pointer.net/blog/casync-a-tool-for-distributing-file-system-images.html
  - https://github.com/systemd/casync
  - https://moinakg.wordpress.com/2013/06/22/high-performance-content-defined-chunking/
  - https://invidious.fdn.fr/watch?v=JnNkBJ6pr9s
  - https://github.com/folbricht/desync
  - https://github.com/rauc/rauc/issues/511
  - https://rauc.readthedocs.io/en/latest/advanced.html
  - https://archive.fosdem.org/2018/schedule/event/distributing_os_images_with_casync/
  - https://archive.fosdem.org/2018/schedule/event/containers_casync/


Bringing (rpm-)ostree and OCI/Docker together
=============================================
- https://fedoraproject.org/wiki/Changes/OstreeNativeContainer
- https://github.com/coreos/enhancements/blob/main/os/coreos-layering.md
- https://github.com/ostreedev/ostree-rs-ext/blob/main/ostree-and-containers.md

Deltas FTW
==========
- https://blogs.gnome.org/alexl/2020/05/13/putting-container-updates-on-a-diet/
- https://github.com/containers/image/pull/902


********
Builders
********


Operating system images
=======================

- mkosi

  - https://github.com/systemd/mkosi
  - http://0pointer.net/blog/mkosi-a-tool-for-generating-os-images.html
  - https://lwn.net/Articles/726655/

- Distrobox

  - https://github.com/89luca89/distrobox
  - https://www.tecmint.com/distrobox-run-any-linux-distribution/
  - https://cloudyday.tech.blog/2022/05/14/distrobox-is-awesome/
  - https://fedoramagazine.org/run-distrobox-on-fedora-linux/
  - https://www.reddit.com/r/linux/comments/r6svfy/github_89luca89distrobox_use_any_linux/

- https://github.com/containers/toolbox
  https://containertoolbx.org/

- https://github.com/debuerreotype/debuerreotype
- https://wiki.debian.org/SystemBuildTools
- https://www.osbuild.org/

  - https://github.com/osbuild
  - https://github.com/osbuild/osbuild
  - https://github.com/osbuild/osbuild-composer
  - https://www.osbuild.org/news/2020-06-01-how-to-ostree-anaconda.html

- https://github.com/coreos/coreos-assembler
- https://pagure.io/pungi
- https://github.com/weldr/lorax

- Check Flatpak

  - https://www.flatpak.org/
  - https://docs.flatpak.org/en/latest/flatpak-command-reference.html

- Look into Kubernetes Image Builder

  - https://github.com/kubernetes-sigs/image-builder


Buildah
=======

- https://www.redhat.com/sysadmin/building-buildah
- https://opensource.com/article/19/3/tips-tricks-rootless-buildah
- https://developers.redhat.com/blog/2019/02/21/podman-and-buildah-for-docker-users
- https://github.com/containers/buildah/blob/main/docs/tutorials/01-intro.md




*****
Tools
*****

Filesystem snapshots
====================

- http://snapper.io/
- https://documentation.suse.com/sles/15-GA/html/SLES-all/cha-snapper.html



*******************
Linux distributions
*******************


General
=======

- https://distrowatch.com/
- Slackware
- Gentoo
- Alpine: n/a
- NixOS
- openSUSE Kubic. -- https://kubic.opensuse.org/
- RHEL UBI minimum. -- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9-beta/html-single/building_running_and_managing_containers/index#con_understanding-the-ubi-minimal-images_assembly_types-of-container-images
- https://developers.redhat.com/blog/2020/03/24/red-hat-universal-base-images-for-docker-users


Fedora CoreOS (FCOS)
====================

- https://getfedora.org/coreos/
- https://getfedora.org/en/coreos/download
- https://docs.fedoraproject.org/en-US/fedora-coreos/faq/
- https://discussion.fedoraproject.org/t/launch-faq-how-are-fedora-coreos-nodes-provisioned-can-i-re-use-existing-cloud-init-configurations/49/1
- https://www.portainer.io/blog/from-zero-to-production-with-fedora-coreos-portainer-and-wordpress-in-7-easy-steps
- https://theforeman.org/2015/06/coreos-cluster-deployments-with-foreman.html
- https://discussion.fedoraproject.org/t/launch-faq-which-container-runtimes-are-available-on-fedora-coreos/52


Fedora Others
=============

- Fedora SilverBlue, IoT, Kinoite; Liri

  - https://silverblue.fedoraproject.org/
  - https://docs.fedoraproject.org/en-US/fedora-silverblue/
  - https://kinoite.fedoraproject.org/
  - https://getfedora.org/iot/
  - https://liri.io/download/silverblue/
  - quay.io/fedora/coreos:stable
  - quay.io/fedora/silverblue:36
  - quay.io/coreos-assembler/fcos:stable

- Fedora Cloud

  - https://alt.fedoraproject.org/cloud/

- Fedora Rawhide (currently probably Fedora 37, no?)

  - https://docs.fedoraproject.org/en-US/releases/rawhide/
  - https://lwn.net/1998/0820/rawhide.html


Alpine Linux
============

| Q: Can Alpine Linux be used?
| A: Not out of the box, because Alpine Linux uses the OpenRC init system. Maybe ``alpine-systemd`` helps?

- https://www.cyberciti.biz/faq/how-to-enable-and-start-services-on-alpine-linux/
- https://news.ycombinator.com/item?id=19375234
- https://github.com/bryanlatten/alpine-systemd
- https://www.client9.com/article/docker-and-alpine-linux-and-systemd/
- https://wiki.alpinelinux.org/wiki/Installing_ArchLinux_inside_an_Alpine_chroot
- https://wiki.alpinelinux.org/wiki/Comparison_with_other_distros
- https://docs.alpinelinux.org/user-handbook/0.1a/Working/apk.html


KISS Linux
==========

- https://web.archive.org/web/20200528200318/https://k1ss.org/
- https://kisslinux.org/
- https://github.com/kiss-community
- https://kisscommunity.org/
- https://news.ycombinator.com/item?id=31307846
- https://jedahan.com/kiss-find/

The distribution explicitly excludes logind, udev, dbus, systemd, polkit,
pulseaudio, electron and all desktop environments. This software is either
with lock-in, too complex or otherwise out of scope.
