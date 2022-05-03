# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
import subprocess
import time
from abc import abstractmethod

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.model import OperatingSystem, LinuxDistribution
from postroj.util import host_is_up, print_header, print_section_header


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

    def wait_for_port(self, host: str, port: int):
        # TODO: Improve waiting until port is reachable.
        timeout = 5
        interval = 0.1
        while timeout > 0:
            if host_is_up(host, port):
                break
            time.sleep(interval)
            timeout -= interval
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
            self.run("/usr/bin/apt-get install --yes apache2 curl")
        if self.is_redhat:
            package_and_unit_name = "httpd"
            self.run("/usr/bin/yum install -y httpd curl")

        # Enable service.
        self.run(f"/bin/systemctl enable {package_and_unit_name}")
        self.run(f"/bin/systemctl start {package_and_unit_name}")

        # Run probe.
        self.run(f"/bin/systemctl is-active {package_and_unit_name}")
        self.wait_for_port("localhost", 80)


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
