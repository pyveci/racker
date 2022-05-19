# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import dataclasses
import logging
import sys
import time
from contextlib import redirect_stdout
from copy import copy
from typing import Dict, List, Type, Union

import click

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.model import LinuxDistribution
from postroj.probe import ProbeBase
from postroj.registry import CURATED_OPERATING_SYSTEMS, CuratedOperatingSystem
from postroj.util import to_json

logger = logging.getLogger(__name__)


@click.group()
def selftest_main():
    """
    Run different kinds of self tests
    """
    pass


@click.command()
def selftest_hostnamectl():
    """
    Run example command on all curated containers.

    - Iterate all available filesystem images.
    - Spawn a container.
    - Wait until container has booted completely.
    - Display host information about the container, using `hostnamectl`.
    """
    selected_distributions = get_selftest_distributions()
    success = selftest_multiple(selected_distributions, probes=[HostinfoProbe])
    if not success:
        sys.exit(5)


@click.command()
def selftest_pkgprobe():
    """
    Run example package/service probes on all curated containers.

    - Iterate all available filesystem images.
    - Spawn a container.
    - Wait until container has booted completely.
    - Run two probe actions on the container.
    """

    selected_distributions = get_selftest_distributions()
    success = selftest_multiple(selected_distributions, probes=[JournaldProbe, ApacheProbe])
    if not success:
        sys.exit(5)


class HostinfoProbe(ProbeBase):
    """
    A very basic probe which just invokes `hostnamectl` on a container.
    """

    def invoke(self):
        self.container.info()


class JournaldProbe(ProbeBase):
    """
    Another basic probe which asserts the `systemd-journald` unit is active.
    """

    def invoke(self):
        self.check_unit(name="systemd-journald")


class ApacheProbe(ProbeBase):
    """
    A slightly more advanced probe which installs a distribution package,
    checks the unit state and also tests the server port for availability.

    In this case, the Apache daemon is installed and enabled. Afterwards,
    `localhost:80` is checked for availability.

    The special thing, other than dispatching for different operating systems,
    is that the routine also accounts for different unit names.
    """

    def invoke(self):

        logger.info("Checking Apache web server")

        # Setup service.
        # TODO: Refactor to generic package installer.
        logger.info("Installing Apache web server")
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
        elif self.is_suse:
            package_name = unit_name = "apache2"
            self.run(f"/usr/bin/zypper install -y {package_name}")
        else:
            raise ValueError(f"Unable to invoke ApacheProbe. Reason: Unsupported operating system.")

        # Enable service.
        self.run(f"/bin/systemctl enable {unit_name}")
        self.run(f"/bin/systemctl start {unit_name}")

        # Run probe.
        self.check_unit(unit_name)
        self.check_address("http://localhost:80")


@dataclasses.dataclass
class SelftestResult:
    """
    Capture information about probe outcomes.
    """

    distribution: LinuxDistribution
    probes: Dict[str, bool] = dataclasses.field(default_factory=dict)


def selftest_multiple(distributions: List[Union[LinuxDistribution, CuratedOperatingSystem]], probes: List[Type] = None):
    """
    Run a list of probes on a list of selected operating systems.
    """

    probes = probes or []
    results = []
    success = None

    # Iterate all suitable operating systems.
    for distribution in distributions:
        logger.info(f"Probing distribution {distribution}")
        result = SelftestResult(distribution=distribution)

        # Acquire path to rootfs filesystem image.
        ip = ImageProvider(distribution=distribution)
        rootfs_path = ip.image

        # Invoke `hostnamectl` on each container.
        with PostrojContainer(image_path=rootfs_path) as pc:
            with redirect_stdout(sys.stderr):
                pc.boot()
                pc.wait()
                # pc.info()

            for probe_class in probes:
                probe_name = probe_class.__name__
                try:
                    probe = probe_class(container=pc)
                    probe.invoke()
                    success = True
                    result.probes[probe_name] = True
                except:
                    success = False
                    logger.exception(f"Probe {probe_name} failed on {distribution}")
        results.append(result)

    time.sleep(0.33)
    print_report(results)
    return success


def get_selftest_distributions():
    """
    Select list of curated distributions for self-testing.
    """

    # Select all distributions.
    selected_systems = copy(CURATED_OPERATING_SYSTEMS)

    # Mask two distributions which show unstable cycling behavior.
    selected_systems.remove(CuratedOperatingSystem.FEDORA_35)
    selected_systems.remove(CuratedOperatingSystem.CENTOS_7)

    # Mask RHEL9/UBI9 because it can not install packages.
    selected_systems.remove(CuratedOperatingSystem.RHEL_9)

    # On demand, select only specific items.
    # selected_systems = [CuratedOperatingSystem.ARCHLINUX_20220501]
    # selected_systems = [CuratedOperatingSystem.OPENSUSE_TUMBLEWEED]
    # selected_systems = [CuratedOperatingSystem.RHEL_9]
    # selected_systems = [CuratedOperatingSystem.CENTOS_9]
    # selected_systems = [CuratedOperatingSystem.SLES_BCI]

    selected_distributions = [system.value for system in selected_systems]

    return selected_distributions


def print_report(results):
    """
    Print report about self-test outcome.
    """
    logger.info(f"Checked {len(results)} distributions")
    print(to_json(results))


selftest_main.add_command(cmd=selftest_pkgprobe, name="pkgprobe")
selftest_main.add_command(cmd=selftest_hostnamectl, name="hostnamectl")
