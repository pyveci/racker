# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
import subprocess
from copy import copy
from typing import Union

from furl import furl

from postroj.container import PostrojContainer, cache_directory
from postroj.image import ImageProvider
from postroj.model import OperatingSystem, ALL_DISTRIBUTIONS
from postroj.util import print_header, print_section_header, wait_for_port

# TODO: Make this configurable.
download_directory = cache_directory / "downloads"


class ProbeBase:

    def __init__(self, container: PostrojContainer):
        self.container = container

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
        self.run(f"/bin/systemctl is-active {package_and_unit_name}")
        self.check_address("http://localhost:80")


if __name__ == "__main__":
    """
    Spawn a container and wait until it has booted completely.
    Then, run a probe command on the container.
    
    Probing all listed operating systems takes
    - about four seconds for the Basic probe.
    - about one minute for the Apache probe.
    """

    selected_distributions = copy(ALL_DISTRIBUTIONS)
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

    print(f"Successfully checked {len(selected_distributions)} distributions:\n"
          f"{json.dumps(list(map(str, selected_distributions)), indent=2)}")
