# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
import os
import subprocess
import time
from abc import abstractmethod
from pathlib import Path
from typing import List

from furl import furl

from postroj.container import PostrojContainer, cache_directory
from postroj.image import ImageProvider
from postroj.model import OperatingSystem, LinuxDistribution
from postroj.util import port_is_up, print_header, print_section_header, wait_for_port

# TODO: Make this configurable.
download_directory = cache_directory / "downloads"


class ProbeBase:

    def __init__(self, container: PostrojContainer):
        self.container = container

    @abstractmethod
    def invoke(self):
        """
        Setup and run the probe.
        """
        raise NotImplementedError()

    def run(self, command: str):
        return self.container.run(command=command, verbose=True)

    def check_unit(self, name):
        """
        Check unit for being `active`.
        """
        print(f"INFO: Probing unit {name}")
        try:
            outcome = self.run(f"/bin/systemctl is-active {name}")
            print(f"INFO: Status of unit {name}: {outcome}")
        except subprocess.CalledProcessError as ex:
            outcome = ex.output.decode().strip()
            print(f"INFO: Status of unit {name}: {outcome}")
            if outcome == "inactive":
                msg = f"ERROR: Probe failed, unit {name} is not active"
                print(msg)
                raise SystemExit(ex.returncode)
            else:
                print(f"ERROR: Unable to check unit {name}. "
                      f"Process exited with returncode {ex.returncode}. Output:\n{ex.output}")
                raise

    @property
    def is_debian(self):
        return (self.container.rootfs / "etc" / "debian_version").exists()

    @property
    def is_redhat(self):
        return (self.container.rootfs / "etc" / "redhat-release").exists()

    def check_address(self, address: str, timeout: float = 5.0, interval: float = 0.05):

        uri = furl(address)
        print(f"Waiting for {uri} to become available within {timeout} seconds")

        if uri.scheme in ["tcp", "http", "https"]:
            host, port = uri.host, int(uri.port)
            if not wait_for_port(host, port, timeout=timeout, interval=interval):
                raise TimeoutError(f"{host}:{port} did not become available within {timeout} seconds")
        else:
            raise ValueError(f"Unknown scheme for network address {uri}")

        if uri.scheme in ["http", "https"]:
            host, port = uri.host, int(uri.port)
            self.run(f"/usr/bin/curl {host}:{port} --output /dev/null --dump-header -")


class BasicProbe(ProbeBase):

    def invoke(self):
        print_header("Checking unit systemd-journald")
        self.check_unit(name="systemd-journald")


class ApacheProbe(ProbeBase):

    def invoke(self):

        print_header("Checking Apache web server")

        # Setup service.
        print("Installing Apache web server")
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
        self.run(f"/bin/systemctl is-active {package_and_unit_name}")
        self.check_address("http://localhost:80")


class PackageProbe(ProbeBase):

    def invoke(self, package: str, unit_names: List[str], network_addresses: List[str], network_timeout: float = 5.0):

        print_header(f"Checking units {','.join(unit_names)}")

        # Download package.
        if package.startswith("http"):
            print(f"Downloading {package}")
            self.run(f"/usr/bin/wget --no-clobber --directory-prefix={download_directory} {package}")
            package = download_directory / os.path.basename(package)
        else:
            raise ValueError(f"Unable to acquire package at {package}")

        # Install package.
        print(f"Installing package {package}")
        if self.is_debian:
            self.run(f"/usr/bin/apt install --yes {package}")
        if self.is_redhat:
            self.run(f"/usr/bin/yum install -y {package}")

        # Enable units.
        for unit in unit_names:
            self.run(f"/bin/systemctl enable {unit}")
            self.run(f"/bin/systemctl start {unit}")

        # Run probes: The systemd unit has to be "active" and the designated ports should be available.
        for unit in unit_names:
            self.run(f"/bin/systemctl is-active {unit}")
        for address in network_addresses:
            self.check_address(address, timeout=network_timeout)


if __name__ == "__main__":
    """
    Spawn a container and wait until it has booted completely.
    Then, run a probe command on the container.
    
    Probing all listed operating systems takes
    - about four seconds for the Basic probe.
    - about one minute for the Apache probe.
    """

    # Select operating systems.
    all_distributions = [
        OperatingSystem.DEBIAN_BUSTER.value,
        OperatingSystem.DEBIAN_BULLSEYE.value,
        OperatingSystem.UBUNTU_FOCAL.value,
        OperatingSystem.UBUNTU_JAMMY.value,
        # OperatingSystem.CENTOS_7.value,
        OperatingSystem.CENTOS_8.value,
    ]

    # Iterate selected distributions.
    distribution: LinuxDistribution
    for distribution in all_distributions:
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

    print(f"Successfully checked {len(all_distributions)} distributions:\n"
          f"{json.dumps(list(map(str, all_distributions)), indent=2)}")
