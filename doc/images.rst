#####################
Racker image building
#####################

.. note::

    This is still a work in progress.


*****
Usage
*****


Docker image via OCI bundle
===========================

The idea is to build upon the images hosted on hub.docker.com. Before the
system can be booted properly as a container with ``systemd-nspawn``, the
``systemd`` package will have to be installed.

Here, we are converting Docker images to `OCI filesystem bundles`_  first.

Debian
------

Install prerequisites::

    # Debian Linux
    apt-get install skopeo umoci

    # macOS
    brew install skopeo go-md2man
    git clone https://github.com/opencontainers/umoci; cd umoci; make -j8 && cp umoci /usr/local/bin/

Acquire image::

    skopeo copy docker://docker.io/debian:bullseye-slim oci:debian:bullseye-slim
    umoci ls --layout debian
    umoci stat --image debian:bullseye-slim
    umoci unpack --image debian:bullseye-slim bullseye-slim

Prepare image::

    systemd-nspawn --directory=bullseye-slim/rootfs sh -c "apt-get update; apt-get install --yes systemd"

Invoke machine::

    # Needs the `--machine` option, otherwise the machine would be called `rootfs`.
    systemd-nspawn --directory bullseye-slim/rootfs --boot --volatile=overlay --machine=debian-bullseye
    machinectl shell debian-bullseye


CentOS
------
::

    skopeo copy docker://docker.io/centos:7 oci:centos:7
    umoci unpack --image centos:7 centos-7
    systemd-nspawn --directory centos-7/rootfs --boot --volatile=overlay --machine=centos-7


.. _OCI filesystem bundles: https://github.com/opencontainers/runtime-spec/blob/main/bundle.md


Docker image (direct)
=====================

Same thing as above, but only needs ``docker`` and ``tar``.

Define converter function::

    function d2d {
        image=$1
        directory=$2
        mkdir -p $directory
        docker export "$(docker create --rm --name d2d $image true)" | tar -x -C $directory
        docker rm d2d >/dev/null
    }

Acquire and prepare image::

    d2d debian:bullseye-slim bullseye-slim
    systemd-nspawn --directory bullseye-slim sh -c "apt-get update; apt-get install --yes systemd"

Invoke machine::

    systemd-nspawn --directory bullseye-slim --boot --volatile=overlay
    machinectl shell debian-bullseye


Cloud image
===========

Ubuntu
------

Acquire image::

    wget https://cloud-images.ubuntu.com/minimal/releases/focal/release/ubuntu-20.04-minimal-cloudimg-amd64-root.tar.xz
    mkdir ubuntu-focal
    tar -xf ubuntu-20.04-minimal-cloudimg-amd64-root.tar.xz --directory ubuntu-focal

Prepare image::

    systemd-nspawn --directory=ubuntu-focal systemctl disable ssh systemd-networkd-wait-online

Invoke machine::

    systemd-nspawn --directory ubuntu-focal --boot --volatile=overlay


Fedora
------

::

    https://download.fedoraproject.org/pub/fedora/linux/releases/34/Cloud/x86_64/images/Fedora-Cloud-Base-34-1.2.x86_64.raw.xz
    xz -d Fedora-Cloud-Base-34-1.2.x86_64.raw.xz
    systemd-nspawn --image Fedora-Cloud-Base-34-1.2.x86_64.raw --boot --volatile=overlay --bind-ro=/etc/resolv.conf:/etc/resolv.conf


CentOS
------
Unfortunately, the size of the images are 352M compressed and >3.4G uncompressed.
::

    wget https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.raw.tar.gz
    tar -xzf CentOS-7-x86_64-GenericCloud.raw.tar.gz



Vagrant box
===========

Acquire image::

    wget https://app.vagrantup.com/debian/boxes/bullseye64/versions/11.20211230.1/providers/virtualbox.box
    mkdir tmp; cd tmp; tar -xzf ../virtualbox.box

Extract root filesystem::

    apt install qemu-utils
    modprobe nbd

    qemu-nbd -r -c /dev/nbd1 box.vmdk
    mkdir rootfs; mount /dev/nbd1p1 rootfs

Invoke machine::

    systemd-nspawn --directory=rootfs --boot --volatile=overlay --machine=debian-bullseye

After stopping::

    umount rootfs


-- http://www.uni-koeln.de/~pbogusze/posts/Extract_files_from_VMDK_images.html
-- https://unix.stackexchange.com/questions/550569/how-can-i-access-the-files-in-a-vmdk-file/550654
