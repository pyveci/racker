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

    selected_distributions = copy(ALL_DISTRIBUTIONS)
    selected_distributions.remove(OperatingSystem.FEDORA_35.value)
    selected_distributions.remove(OperatingSystem.CENTOS_7.value)

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
        package_and_unit_name: Union[str, None] = None
        if self.is_debian:
            package_and_unit_name = "apache2"
            self.run("/usr/bin/apt-get update")
            self.run("/usr/bin/apt-get install --yes apache2")
        if self.is_redhat:
            package_and_unit_name = "httpd"
            self.run("/usr/bin/yum install -y httpd")

        # Enable service.
        self.run(f"/bin/systemctl enable {package_and_unit_name}")
        self.run(f"/bin/systemctl start {package_and_unit_name}")

        # Run probe.
        self.check_unit(package_and_unit_name)
        self.check_address("http://localhost:80")


selftest_main.add_command(cmd=selftest_pkgprobe, name="pkgprobe")
