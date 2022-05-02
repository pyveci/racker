###############
Troubleshooting
###############

.. note::

    Just some random notes.


******************************
systemd-nspawn and OCI bundles
******************************

Running ``systemd-nspawn --oci-bundle=`` directly did not work well. An easy
workaround is to just use ``--directory=oci-bundle/rootfs`` instead.

::

    cd bullseye-oci-bundle/
    systemd-nspawn --oci-bundle=.
    systemd-nspawn --oci-bundle=. --private-users=pick

    cd bundle
    runc run test

    apt update

    E: setgroups 65534 failed - setgroups (1: Operation not permitted)
    E: setegid 65534 failed - setegid (1: Operation not permitted)

See also:

- https://github.com/opencontainers/runc/issues/1860
- https://github.com/opencontainers/runc/issues/2517#issuecomment-720897616


******
CentOS
******

Problem
=======
::

    machinectl shell foobar
    Failed to get shell PTY: Cannot set property StandardInputFileDescriptor, or unknown property.
    Failed to get shell PTY: Protocol error

Reason
======

CentOS 7 has 219 but systemd >= 225 is needed.
https://github.com/systemd/systemd/issues/2277

::

    systemctl --version


Solution
========

Upgrade systemd.

::

    yum install -y wget gcc make libtool intltool gperf glib2-devel libcap-devel xz-devel libgcrypt-devel libmount-devel
    wget https://www.freedesktop.org/software/systemd/systemd-225.tar.xz
    wget https://github.com/systemd/systemd/archive/refs/tags/v225.tar.gz -O systemd-225.tar.gz
    wget https://github.com/systemd/systemd/archive/refs/tags/v247.tar.gz -O systemd-247.tar.gz
    tar -xzf; cd

    ./autogen.sh
    # Run ./configure, as advertised. Add `--disable-manpages`.
    ./configure CFLAGS='-g -O0 -ftrapv' --enable-compat-libs --enable-kdbus --sysconfdir=/etc --localstatedir=/var --libdir=/usr/lib64 --disable-manpages
    make -j8 && make install
    systemctl --version

    systemd 219
    +PAM +AUDIT +SELINUX +IMA -APPARMOR +SMACK +SYSVINIT +UTMP +LIBCRYPTSETUP +GCRYPT +GNUTLS +ACL +XZ +LZ4 -SECCOMP +BLKID +ELFUTILS +KMOD +IDN

    systemd 225
    -PAM -AUDIT -SELINUX +IMA -APPARMOR +SMACK +SYSVINIT +UTMP -LIBCRYPTSETUP +GCRYPT -GNUTLS -ACL +XZ -LZ4 -SECCOMP -BLKID -ELFUTILS -KMOD -IDN
