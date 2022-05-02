# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import subprocess
import time
from pathlib import Path

from postroj.container import PostrojContainer
from postroj.image import ImageProvider
from postroj.model import OperatingSystem


class ProbeBase:

    def __init__(self, container: PostrojContainer):
        self.container = container

    def invoke(self):
        raise NotImplementedError()

    def check_unit(self, name):
        """
        Commands to setup and run the probe.
        """
        print(f"INFO: Probing unit {name}")
        try:
            outcome = self.container.run(f"/bin/systemctl is-active {name}")
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


class BasicProbe(ProbeBase):

    def invoke(self):
        self.check_unit(name="systemd-journald")


if __name__ == "__main__":
    """
    Spawn a container and wait until it has booted completely.
    Then, run a probe command on the container.
    
    Probing all listed operating systems takes about four seconds.
    """
    all_distributions = [
        OperatingSystem.DEBIAN_BUSTER.value,
        OperatingSystem.DEBIAN_BULLSEYE.value,
        OperatingSystem.UBUNTU_FOCAL.value,
        OperatingSystem.UBUNTU_JAMMY.value,
        # OperatingSystem.CENTOS_7.value,
        OperatingSystem.CENTOS_8.value,
    ]
    for distribution in all_distributions:
        ip = ImageProvider(distribution=distribution)
        rootfs = ip.image
        with PostrojContainer(rootfs=rootfs) as pc:
            pc.boot()
            pc.wait()
            pc.info()
            probe = BasicProbe(container=pc)
            probe.invoke()
