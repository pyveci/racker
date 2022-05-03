###############
postroj backlog
###############

.. note::

    Those are just random notes about ideas and more.


**********
Actionable
**********

- [o] Naming things.
- [o] Refactoring.
- [o] Implement ``postroj list-images``.
- [o] Add Debian stretch.
- [o] Implement some software tests.
- [o] Release 0.1.0.
- [o] Option to force downloading and rebuilding rootfs images.


*****
Ideas
*****

- Currently, ``systemd-nspawn`` needs to be invoked as user ``root``.
  Investigate *systemd-nspawn unprivileged mode* if that can improve the situation.
  https://www.reddit.com/r/archlinux/comments/ug1fwy/systemdnspawn_unprivileged_mode/
- Make sure ``resolved`` is enabled on both the host and the guest.
  ``systemctl enable systemd-resolved``.
  Maybe this can get rid of bind-mounting the ``resolv.conf``, see
  ``--bind-ro=/etc/resolv.conf:/etc/resolv.conf``.
- Optionally install more software into machine image by default.
  ``apt-get install --yes procps iputils-ping netcat telnet iproute2 openssh-client wget curl``
- Check if and how ready-made Vagrant images can be used for providing rootfs.
- Use ``CacheDirectory=`` directive to cache download artefacts

- Check non-x64 architectures

  - https://forums.raspberrypi.com/viewtopic.php?t=232417&start=100
  - https://github.com/sakaki-/raspbian-nspawn-64

- Use/integrate with ``mkosi``.

  - https://github.com/systemd/mkosi
  - http://0pointer.net/blog/mkosi-a-tool-for-generating-os-images.html
  - https://lwn.net/Articles/726655/

- Check KIWI

  - https://github.com/OSInside/kiwi

- Build ``RootImage=``-compatible images, with GPT
- Integrate packaging code from Kotori
- Proposal: ``postroj create image`` vs. ``postroj create package``
- Check if "login prompt" unit can be deactivated when running with ``--boot``
- Check ``systemd-dissect``
- Check unprivileged mode / ``--user`` / ``-U``

- Fedora 35 does not work

  - https://www.spinics.net/lists/fedora-devel/msg296987.html
  - https://bugzilla.redhat.com/show_bug.cgi?id=2048033
  - https://pagure.io/ContainerSIG/container-sig/issue/55
  - https://pagure.io/cloud-sig/issue/367

- Look into Kata Containers

  - https://github.com/kata-containers/kata-containers
  - https://virtio-fs.gitlab.io/

- Look into UTM

  - https://github.com/utmapp/UTM
  - https://mac.getutm.app/

- Look into Quickemu

  - https://github.com/quickemu-project

- How can postroj be combined with Packer and/or Buildah?



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

