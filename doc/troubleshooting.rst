###############
Troubleshooting
###############

.. note::

    Just some random notes.


*******************
machinectl pull-raw
*******************

Acquiring an image with ``pull-raw`` like::

    machinectl pull-raw --verify=no \
        https://ftp-stud.hs-esslingen.de/pub/fedora/linux/releases/35/Cloud/x86_64/images/Fedora-Cloud-Base-35-1.2.x86_64.raw.xz \
        Fedora-Cloud-Base-35-1.2.x86-64

will yield large artefacts. Is there a way around it?


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


***********************
Fedora 35 does not work
***********************

Q: Maybe it does not terminate appropriately?

- https://www.spinics.net/lists/fedora-devel/msg296987.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2048033
- https://pagure.io/ContainerSIG/container-sig/issue/55
- https://pagure.io/cloud-sig/issue/367


*************************************
STDIN: Inappropriate ioctl for device
*************************************
::

    echo "hello world" | sudo racker run -it --rm fedora-37 cat -

::

    stty: 'standard input': Inappropriate ioctl for device


- https://www.pyinvoke.org/faq.html#i-m-getting-ioerror-inappropriate-ioctl-for-device-when-i-run-commands
- https://stackoverflow.com/questions/66090902/how-to-supress-the-stty-standard-input-inappropriate-ioctl-for-device-erro
- https://stackoverflow.com/questions/19880190/interactive-input-output-using-python
- https://bitbucket.org/gehrmann/pyguibot/src/ea1ceed3029a3460949910e0d4b19ca9a3bf6227/pyguibot/controllers/qt_gui.py#lines-671


********************************
Tracebacks on container teardown
********************************

::

    Sending SIGTERM to remaining processes...
    Sending SIGKILL to remaining processes...
    All filesystems, swaps, loop devices, MD devices and DM devices detached.
    Halting system.
    Exception ignored in: <function BaseEventLoop.__del__ at 0x7f9c363268b0>
    Traceback (most recent call last):
      File "/usr/lib/python3.9/asyncio/base_events.py", line 683, in __del__
        self.close()
      File "/usr/lib/python3.9/asyncio/unix_events.py", line 58, in close
        super().close()
      File "/usr/lib/python3.9/asyncio/selector_events.py", line 92, in close
        self._close_self_pipe()
      File "/usr/lib/python3.9/asyncio/selector_events.py", line 99, in _close_self_pipe
        self._remove_reader(self._ssock.fileno())
      File "/usr/lib/python3.9/asyncio/selector_events.py", line 277, in _remove_reader
        key = self._selector.get_key(fd)
      File "/usr/lib/python3.9/selectors.py", line 191, in get_key
        return mapping[fileobj]
      File "/usr/lib/python3.9/selectors.py", line 72, in __getitem__
        fd = self._selector._fileobj_lookup(fileobj)
      File "/usr/lib/python3.9/selectors.py", line 226, in _fileobj_lookup
        return _fileobj_to_fd(fileobj)
      File "/usr/lib/python3.9/selectors.py", line 42, in _fileobj_to_fd
        raise ValueError("Invalid file descriptor: {}".format(fd))
    ValueError: Invalid file descriptor: -1


::

    Exception ignored in: <function BaseEventLoop.__del__ at 0x7f4730101160>
    Traceback (most recent call last):
      File "/usr/lib/python3.9/asyncio/base_events.py", line 683, in __del__
        self.close()
      File "/usr/lib/python3.9/asyncio/unix_events.py", line 58, in close
        super().close()
      File "/usr/lib/python3.9/asyncio/selector_events.py", line 92, in close
        self._close_self_pipe()
      File "/usr/lib/python3.9/asyncio/selector_events.py", line 99, in _close_self_pipe
        self._remove_reader(self._ssock.fileno())
      File "/usr/lib/python3.9/asyncio/selector_events.py", line 277, in _remove_reader
        key = self._selector.get_key(fd)
      File "/usr/lib/python3.9/selectors.py", line 191, in get_key
        return mapping[fileobj]
      File "/usr/lib/python3.9/selectors.py", line 72, in __getitem__
        fd = self._selector._fileobj_lookup(fileobj)
      File "/usr/lib/python3.9/selectors.py", line 226, in _fileobj_lookup
        return _fileobj_to_fd(fileobj)
      File "/usr/lib/python3.9/selectors.py", line 42, in _fileobj_to_fd
        raise ValueError("Invalid file descriptor: {}".format(fd))
    ValueError: Invalid file descriptor: -1


***********************************
SYSTEMD_COLORS environment variable
***********************************

Turning that off does not seem to work with `systemd-run` and::

    Failed to start transient service unit: Path foo is not absolute.


*******************
systemd exit status
*******************

Assume exit status 203 from `systemd-run` means "file/command not found". True?


*****************************
No way to disable /etc/issue?
*****************************

It looks like the subsystem responsible for reading ``/etc/issue`` and displaying
its content at the beginning of an interactive login session, will add a newline
character even if the file is empty. It also looks like there is no obvious way
to turn off this feature completely.

- https://www.linuxquestions.org/questions/linux-newbie-8/disable-etc-issue-net-775967/
- https://bugzilla.redhat.com/show_bug.cgi?id=1663812
- https://unix.stackexchange.com/questions/107138/i-want-to-print-a-line-when-a-user-login
- https://unix.stackexchange.com/questions/84280/is-etc-issue-common-for-all-linux-distributions
- Use ``agetty``'s ``--noissue`` option?

  - https://sleeplessbeastie.eu/2019/09/18/how-to-modify-system-identification-message/
  - /usr/lib/systemd/system/console-getty.service
  - /usr/lib/systemd/system/container-getty@.service
  - /usr/lib/systemd/system/getty@.service
  - /usr/lib/systemd/system/serial-getty@.service


******************************************
Docker context on Windows VM not reachable
******************************************

- Symptom: Process croaks or stalls while trying to connect to the Docker context on the Windows VM.
- Reference: https://github.com/docker/machine/issues/531

Problems::

    $ docker --context=2019-box ps
    error during connect: Get "https://192.168.59.90:2376/v1.24/containers/json": x509: certificate is valid for 169.254.232.221, 172.30.112.1, 10.0.2.15, 127.0.0.1, not 192.168.59.90

    $ docker --context=2019-box ps
    error during connect: Get "https://192.168.59.90:2376/v1.24/containers/json": x509: certificate signed by unknown authority (possibly because of "crypto/rsa: verification error" while trying to verify candidate authority certificate "Docker TLS Root")

Solution::

    docker context rm 2019-box


***********************************
Problem running Windows Server 2022
***********************************

Problem when running 1709 and 1809 container images on a 2016 host::

    docker: a Windows version 10.0.16299-based image is incompatible with a 10.0.14393 host.
    docker: a Windows version 10.0.17763-based image is incompatible with a 10.0.14393 host.

Problem when running a 2022 container image on a 2019 host::

    docker: a Windows version 10.0.20348-based image is incompatible with a 10.0.17763 host.

Problem when running a 2019 container image on a 2022 host::

    docker: Error response from daemon: hcsshim::CreateComputeSystem bd3b2a3b001dbe632c11170e1cfdf2fd0ec0c26e27739a61961d50f3d01a4548:
    The container operating system does not match the host operating system.


Solution: Use a more recent version of Windows within the Windows Docker Machine VM.
