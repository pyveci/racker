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



*****
Tools
*****

Filesystem snapshots
====================

- http://snapper.io/
- https://documentation.suse.com/sles/15-GA/html/SLES-all/cha-snapper.html
