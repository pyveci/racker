###############
postroj backlog
###############

.. note::

    Those are just random notes about ideas and more.


*************
Release 0.1.0
*************

- [x] Naming things.
- [x] Refactoring.
- [x] Implement ``postroj list-images``.
- [x] Improve robustness and convenience.
- [x] Add more Linux distributions.
- [x] Improve convenience of Vagrant sandbox with autosetup and sudo permissions
- [x] Add logging.
- [x] Implement ``postroj run``.
- [o] Add some basic software tests.
- [o] Format code using ``black`` and ``isort``.
- [o] Rename project and Python package to ``racker``.


*************
Release 0.2.0
*************

- [o] Improve software tests.
- [o] Check if software tests can be invoked on CI/GHA.
- [o] Continue renaming to ``racker``.
- [o] Split functionality between ``racker`` and ``postroj``.

  - ``racker {run,pull,logs}``
  - ``postroj {list-images,pkgprobe,selftest}``
  - ``pronto opensuse/tumbleweed hostnamectl`` (``pronto.hexagon`` (hx), ``pronto.kaxon`` (kx))
- [o] Provide more advanced and generic image (label) resolution, from docker.io, ghcr.io, etc.
- [o] Improve error messages, see "Compatibility" section

  - postroj run -it --rm debian-stretch hostnamectl
  - postroj run -it --rm debian-stretch /bin/hostnamectl
  - postroj run -it --rm debian-stretch /usr/bin/hostnamectl
- [o] Wait for container to properly shut down before moving on.
      Q: When running ``postroj selftest``, why is there more output from
         containers shutting down, while the program is finished already?
- [o] Improve textual/logging output of probe details. Colors?
- [o] Check non-x64 architectures, maybe using Qemu and/or ``binfmt_misc``/``systemd-binfmt``.

  - https://en.wikipedia.org/wiki/Binfmt_misc
  - https://www.freedesktop.org/software/systemd/man/binfmt.d.html
  - https://www.freedesktop.org/software/systemd/man/systemd-binfmt.service.html
  - https://forums.raspberrypi.com/viewtopic.php?t=232417&start=100
  - https://github.com/sakaki-/raspbian-nspawn-64
  - https://cloud.debian.org/images/cloud/bullseye/latest/debian-11-generic-arm64.tar.xz

- [o] Improve README: Point out some specific features and their use cases


*************
Release 0.3.0
*************

- [o] Optionally force downloading and rebuilding rootfs images by using
  ``postroj pull --force``, re-triggering the ``skopeo`` and ``umoci`` steps.
- [o] Implement ``postroj logs``.
- [o] Accept packages from filesystem by using ``copy-to``.
  https://www.freedesktop.org/software/systemd/man/machinectl.html#copy-to%20NAME%20PATH%20%5BPATH%5D
- [o] Generalize package installation (is_debian vs. is_redhat vs. is_suse)
- [o] Implement ``racker compose``.
  - What about network isolation, host name assignment and resolution?
  - What about filesystem mounting?


*************
Release 0.4.0
*************

- [o] Is it possible to run RHEL and SLES?
- [o] Improve HTTP probe request/response handling and verification.
  Q: Would it be possible to implement it completely in Python?


*************
Compatibility
*************

CLI interfaces
==============
- ``docker {run,pull,logs}`` (implemented by ``racker``)
- ``docker compose`` (implemented by ``racker``)
- ``docker-py`` Python package (``import racker as docker; client = docker.from_env()``)
- Xen CLI ``xm``/``xl`` (implemented by ``hx`` or ``kx``)

Behaviour on error conditions
=============================
::

    docker run -it --rm opensuse/leap2 bash
    Unable to find image 'opensuse/leap2:latest' locally

References
==========
- https://pypi.org/project/docker-compose/
- https://pypi.org/project/docker-pycreds/
- https://pypi.org/project/docker-py/
- https://pypi.org/project/docker/
- https://github.com/docker/docker-py/blob/master/tests/unit/client_test.py


*****
Ideas
*****

- [o] Look at Nspawn console
  - https://wiki.archlinux.org/title/getty#Nspawn_console
  - https://wiki.archlinux.org/title/Systemd#Change_default_target_to_boot_into

- [o] Look at systemd-firstboot

  - https://wiki.archlinux.org/title/Systemd-firstboot

- Use/integrate with ``mkosi``.

  - https://github.com/systemd/mkosi
  - http://0pointer.net/blog/mkosi-a-tool-for-generating-os-images.html
  - https://lwn.net/Articles/726655/

- Currently, ``systemd-nspawn`` needs to be invoked as user ``root``.

  - Investigate *systemd-nspawn unprivileged mode* if that can improve the situation.
    https://www.reddit.com/r/archlinux/comments/ug1fwy/systemdnspawn_unprivileged_mode/
  - Check options ``--user`` / ``-U``.

- Make sure ``resolved`` is enabled on both the host and the guest.
  ``systemctl enable systemd-resolved``.
  Maybe this can get rid of bind-mounting the ``resolv.conf``, see
  ``--bind-ro=/etc/resolv.conf:/etc/resolv.conf``.

- Optionally install more software into machine image by default.
  ``apt-get install --yes procps iputils-ping netcat telnet iproute2 openssh-client wget curl``

- Use ``CacheDirectory=`` directive to cache download artefacts
- Build ``RootImage=``-compatible images, with GPT
- Integrate packaging code from Kotori
- Proposal: ``postroj create image`` vs. ``postroj create package``
- Check if "login prompt" unit can be deactivated when running with ``--boot``
- Check ``systemd-dissect``
- Boot ``.iso``
- Boot Xen guest, using Hexagon, with ``hx``.
- Logging to journald
- Run system provisioning with Ansible


********
Research
********

- Check if and how ready-made Vagrant images can be used for providing rootfs.

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

- Look into Kubernetes Image Builder

  - https://github.com/kubernetes-sigs/image-builder


********
Problems
********

No way to disable /etc/issue?
=============================

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



*************
Miscellaneous
*************

- Others also recommend ``systemd-nspawn``.

    "As an aside, we recommend using a more intelligent, modern tool like systemd-nspawn instead."

    -- https://github.com/purpleidea/docker/commit/445197336ebfc341fe1c922410324422b5722328

- If you need to...

    ok if you need nested containers inside an alpine container on github actions, here is how you do it:

    - https://twitter.com/ariadneconill/status/1502406979427446787
    - https://github.com/chainguard-dev/melange/blob/main/.github/workflows/e2e.yaml#L13-L14

    ::

        jobs:
          build:
            name: bootstrap package
            runs-on: ubuntu-latest
            container:
              image: alpine:latest
              options: |
                --cap-add NET_ADMIN --cap-add SYS_ADMIN --security-opt seccomp=unconfined --security-opt apparmor:unconfined

