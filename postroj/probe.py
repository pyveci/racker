# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import logging
import subprocess
from abc import abstractmethod

from furl import furl

from postroj.container import PostrojContainer
from postroj.util import find_rootfs, print_header, wait_for_port

logger = logging.getLogger(__name__)


class ProbeBase:
    def __init__(self, container: PostrojContainer):
        self.container = container
        self.container.rootfs = find_rootfs(self.container.image_path)

    @abstractmethod
    def invoke(self):
        raise NotImplementedError()

    def run(self, command: str, capture: bool = False):
        return self.container.run(command=command, capture=capture)

    @property
    def is_debian(self):
        return (self.container.rootfs / "etc" / "debian_version").exists()

    @property
    def is_redhat(self):
        redhat_release_file = self.container.rootfs / "etc" / "redhat-release"
        os_release_file = self.container.rootfs / "etc" / "os-release"
        return redhat_release_file.exists() or 'ID_LIKE="fedora"' in os_release_file.read_text()

    @property
    def is_suse(self):
        os_release_file = self.container.rootfs / "etc" / "os-release"
        return os_release_file.exists() and "suse" in os_release_file.read_text().lower()

    @property
    def is_archlinux(self):
        return (self.container.rootfs / "etc" / "arch-release").exists()

    def check_unit(self, name):
        """
        Check unit for being `active`.
        """
        print_header(f"Probing unit '{name}'")
        try:
            process = self.run(f"/bin/systemctl is-active {name}", capture=True)
            logger.info(f"Status of unit '{name}': {process.stdout.strip()}")
        except subprocess.CalledProcessError as ex:
            unit_status = ex.stdout.strip()
            logger.info(f"Status of unit '{name}': {unit_status}")
            if unit_status in ["inactive"]:
                logger.error(f"Probe failed, unit '{name}' is not active")
                raise SystemExit(ex.returncode)
            else:
                logger.error(f"Unit '{name}' has unknown status: {unit_status}")
                raise

    def check_address(self, address: str, timeout: float = 5.0, interval: float = 0.05):

        print_header(f"Probing network address {address}")

        uri = furl(address)
        logger.info(f"Waiting for {uri} to become available within {timeout} seconds")

        if uri.scheme in ["tcp", "http", "https"]:
            host, port = uri.host, int(uri.port)
            if not wait_for_port(host, port, timeout=timeout, interval=interval):
                raise TimeoutError(f"{host}:{port} did not become available within {timeout} seconds")
        else:
            raise ValueError(f"Unknown scheme for network address {uri}")

        if uri.scheme in ["http", "https"]:
            host, port = uri.host, int(uri.port)
            self.run(f"/usr/bin/curl {host}:{port} --output /dev/null --dump-header -")
