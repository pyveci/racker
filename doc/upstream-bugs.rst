#############
Upstream bugs
#############

.. note::

    Just some random notes.

*************************
Filesystem overlay hiccup
*************************

About
=====

We observed a situation where, when accessing the OS root directory of an Arch
Linux system with regular Unix tools (``cat``) on the host system, the file
contents indicate that it is a Debian bullseye system instead.

On the other hand, when spawning the OS root directory as container, the system
correctly reports being Arch Linux, as intended.


Details
=======

Host::

    root@rackerhost-debian11:~# uname -a
    Linux rackerhost-debian11 5.10.0-8-amd64 #1 SMP Debian 5.10.46-4 (2021-08-03) x86_64 GNU/Linux

    root@rackerhost-debian11:~# cat /etc/os-release
    PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
    NAME="Debian GNU/Linux"
    VERSION_ID="11"
    VERSION="11 (bullseye)"
    VERSION_CODENAME=bullseye
    ID=debian
    HOME_URL="https://www.debian.org/"
    SUPPORT_URL="https://www.debian.org/support"
    BUG_REPORT_URL="https://bugs.debian.org/"


Create guest::

    skopeo copy --override-os=linux docker://archlinux:base-20220501.0.54834 oci:/var/lib/postroj/archive/archlinux-base-20220501-0-54834.oci:default
    umoci unpack --rootless --image=/var/lib/postroj/archive/archlinux-base-20220501-0-54834.oci:default /var/lib/postroj/archive/archlinux-base-20220501-0-54834.img
    systemd-nspawn --directory=/var/lib/postroj/archive/archlinux-base-20220501-0-54834.img/rootfs --bind-ro=/etc/resolv.conf:/etc/resolv.conf cat /etc/os-release

Inspect guest::

    root@rackerhost-debian11:~# cat /var/lib/postroj/archive/archlinux-base-20220501-0-54834.img/rootfs/etc/os-release

    PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
    NAME="Debian GNU/Linux"
    VERSION_ID="11"
    VERSION="11 (bullseye)"
    VERSION_CODENAME=bullseye
    ID=debian
    HOME_URL="https://www.debian.org/"
    SUPPORT_URL="https://www.debian.org/support"
    BUG_REPORT_URL="https://bugs.debian.org/"

::

    root@rackerhost-debian11:~# systemd-nspawn --directory=/var/lib/postroj/archive/archlinux-base-20220501-0-54834.img/rootfs --bind-ro=/etc/resolv.conf:/etc/resolv.conf cat /etc/os-release

    Spawning container rootfs on /var/lib/postroj/archive/archlinux-base-20220501-0-54834.img/rootfs.
    Press ^] three times within 1s to kill container.
    NAME="Arch Linux"
    PRETTY_NAME="Arch Linux"
    ID=arch
    BUILD_ID=rolling
    ANSI_COLOR="38;2;23;147;209"
    HOME_URL="https://archlinux.org/"
    DOCUMENTATION_URL="https://wiki.archlinux.org/"
    SUPPORT_URL="https://bbs.archlinux.org/"
    BUG_REPORT_URL="https://bugs.archlinux.org/"
    LOGO=archlinux-logo
    Container rootfs exited successfully.
