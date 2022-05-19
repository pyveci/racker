#########
Distrobox
#########


Running Distrobox within Racker
===============================

This actually means: Invoke Podman within a systemd-nspawn container.

Attempt 1::

    racker run -it --rm debian-sid bash
    apt update && apt install --yes distrobox fuse
    export DBX_CONTAINER_IMAGE="quay.io/centos/centos:stream9"
    distrobox create --root --yes --name foo

Croaks::

    Running /usr/bin/distrobox as sudo is not supported.
    Please check the documentation on:
        man distrobox-compatibility	or consult the documentation page on:
        https://github.com/89luca89/distrobox/blob/main/docs/compatibility.md

Croaks::

    ERRO[0000] [graphdriver] prior storage driver overlay failed: 'overlay' is not supported over
    overlayfs, a mount_program is required: backing file system is unsupported for this graph driver.

Maybe the invocation of ``systemd-nspawn`` needs further adjustments.
