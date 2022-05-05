# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import subprocess

from furl import furl

from postroj.container import PostrojContainer
from postroj.util import print_header, wait_for_port


class ProbeBase:

    def __init__(self, container: PostrojContainer):
        self.container = container

    def run(self, command: str, capture: bool = False):
        return self.container.run(command=command, capture=capture)

    @property
    def is_debian(self):
        return (self.container.rootfs / "etc" / "debian_version").exists()

    @property
    def is_redhat(self):
        return (self.container.rootfs / "etc" / "redhat-release").exists()

    @property
    def is_archlinux(self):
        return (self.container.rootfs / "etc" / "arch-release").exists()

    def check_unit(self, name):
        """
        Check unit for being `active`.
        """
        print_header(f"Probing unit {name}")
        try:
            process = self.run(f"/bin/systemctl is-active {name}", capture=True)
            print(f"INFO: Status of unit '{name}': {process.stdout.strip()}")
        except subprocess.CalledProcessError as ex:
            unit_status = ex.stdout.strip()
            print(f"INFO: Status of unit '{name}': {unit_status}")
            if unit_status in ["inactive"]:
                print(f"ERROR: Probe failed, unit '{name}' is not active")
                raise SystemExit(ex.returncode)
            else:
                print(f"ERROR: Unit '{name}' has unknown status: {unit_status}")
                raise

    def check_address(self, address: str, timeout: float = 5.0, interval: float = 0.05):

        print_header(f"Probing network address {address}")

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
