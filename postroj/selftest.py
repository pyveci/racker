# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
from copy import copy
from typing import Union

import click

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.model import ALL_DISTRIBUTIONS, OperatingSystem
from postroj.probe import ProbeBase
from postroj.util import print_section_header, print_header


@click.group()
def selftest_main():
    """
    Run self tests
    """
    pass


@click.command()
def selftest_pkgprobe():
    """
    Run example probes on all available images/containers.

    - Iterate all available filesystem images.
    - Spawn a container.
    - Wait until container has booted completely.
    - Run two probe actions on the container.
    """

    selected_distributions = get_selftest_distributions()

    # Iterate selected distributions.
    for distribution in selected_distributions:
        print_section_header(f"Checking distribution {distribution.fullname}, release={distribution.release}")

        # Acquire rootfs filesystem image.
        ip = ImageProvider(distribution=distribution)
        rootfs = ip.image

        # Boot container and run probe commands.
        with PostrojContainer(rootfs=rootfs) as pc:
            pc.boot()
            pc.wait()
            pc.info()

            probe = BasicProbe(container=pc)
            probe.invoke()

            probe = ApacheProbe(container=pc)
            probe.invoke()

        print()

    print_section_header("Report")
    print(f"Successfully checked {len(selected_distributions)} distributions:\n"
          f"{json.dumps(list(map(str, selected_distributions)), indent=2)}")


class BasicProbe(ProbeBase):

    def invoke(self):
        self.check_unit(name="systemd-journald")


class ApacheProbe(ProbeBase):

    def invoke(self):

        print_header("Checking Apache web server")

        # Setup service.
        print("Installing Apache web server")
        if self.is_debian:
            package_name = unit_name = "apache2"
            self.run(f"/usr/bin/apt-get update")
            self.run(f"/usr/bin/apt-get install --yes {package_name}")
        elif self.is_redhat:
            package_name = unit_name = "httpd"
            self.run(f"/usr/bin/yum install -y {package_name}")
        elif self.is_archlinux:
            package_name = "apache"
            unit_name = "httpd"
            self.run(f"/usr/sbin/pacman -Syu --noconfirm {package_name}")
        else:
            print(f"WARNING: Unable to invoke ApacheProbe. Reason: Unsupported operating system.")
            return

        # Enable service.
        self.run(f"/bin/systemctl enable {unit_name}")
        self.run(f"/bin/systemctl start {unit_name}")

        # Run probe.
        self.check_unit(unit_name)
        self.check_address("http://localhost:80")


@click.command()
def selftest_hostnamectl():
    """
    Spawn a container and wait until it has booted completely.
    Then, display host information about the container, using `hostnamectl`.
    """
    selected_distributions = get_selftest_distributions()

    # Iterate all suitable operating systems.
    for distribution in selected_distributions:
        print_section_header(f"Spawning {distribution.fullname}")

        # Acquire path to rootfs filesystem image.
        ip = ImageProvider(distribution=distribution)
        rootfs_path = ip.image

        # Invoke `hostnamectl` on each container.
        with PostrojContainer(rootfs=rootfs_path) as pc:
            pc.boot()
            pc.wait()
            pc.info()


def get_selftest_distributions():

    # Select all distributions.
    selected_distributions = copy(ALL_DISTRIBUTIONS)

    # Mask two distributions which show unstable cycling behavior.
    selected_distributions.remove(OperatingSystem.FEDORA_35.value)
    selected_distributions.remove(OperatingSystem.CENTOS_7.value)

    # On demand, select only specific items.
    # selected_distributions = [OperatingSystem.ARCHLINUX_20220501.value]

    return selected_distributions


selftest_main.add_command(cmd=selftest_pkgprobe, name="pkgprobe")
selftest_main.add_command(cmd=selftest_hostnamectl, name="hostnamectl")
