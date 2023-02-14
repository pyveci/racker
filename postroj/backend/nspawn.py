# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from pathlib import Path
from typing import Union

import subprocess_tee

from postroj.container import PostrojContainer
from postroj.util import LongRunningProcess, _SysExcInfoType, cmd, hcmd, logger


class NspawnBackend:
    """
    Postroj backend based on `systemd-nspawn`.
    """

    def __init__(self, container: PostrojContainer):
        self.container = container
        self.launcher = NspawnLauncher(container=self.container)

    def launch(self):
        """
        Launch a container.

        Define the command to spawn the container.
        TODO: Mount directory from host.
              # --bind=/usr/src/racker/tmp:/pkg \
        TODO: Why does `--ephemeral` not work?
        TODO: Maybe use `--register=false`?
        TODO: What about `--notify-ready=true`?
        """
        cache_directory = self.container.settings.cache_directory
        command = f"""
            /usr/bin/systemd-nspawn \
            --quiet --boot --link-journal=try-guest \
            --volatile=overlay \
            --bind-ro=/etc/resolv.conf:/etc/resolv.conf \
            --bind={cache_directory}:{cache_directory} \
            --directory={self.container.rootfs} \
            --machine={self.container.machine}
        """.strip()
        logger.info(f"Launch command is: {command}")
        self.launcher.start(command=command)
        self.launcher.check()

    def terminate(self):
        """
        Terminate a container.
        """
        return hcmd(f"/bin/machinectl terminate {self.container.machine}")

    def run(self, *args, **kwargs):
        """
        Run a command inside a container.
        """
        return ccmd(*args, **kwargs)

    def shutdown(self):
        """
        Shutdown container wrapper.
        """
        self.launcher.stop()


class NspawnLauncher(LongRunningProcess):
    def __init__(self, container):
        super(NspawnLauncher, self).__init__()
        self.container: PostrojContainer = container

    def abort_handler(self):
        """
        Propagate signal when machinery croaked while invoking the
        `systemd-nspawn` process.

        In this case, the teardown procedure will be skipped.
        """
        self.container.destroy_after_use = False

    def error_handler(self, exc_info: _SysExcInfoType):
        """
        When machine already exists, modify exception from `CalledProcessError` to `RuntimeError`.
        """
        exc: subprocess_tee.CompletedProcess = exc_info[1]
        stderr = exc.stderr.strip()
        if "already exists" in stderr:
            machine = self.container.machine
            hint = f"Please run `machinectl terminate {machine}` and try again."
            surrogate_exception = RuntimeError(f"Unable to spawn container {machine}. Reason: {stderr}. {hint}")
            exc_info = (exc_info[0], surrogate_exception, exc_info[2])
        return exc_info


def scmd(directory: Union[Path, str], command: str, passthrough: bool = True, capture: bool = False):
    """
    Run command within root filesystem.
    """
    logger.info(f"Running command within rootfs at {directory}: {command}")
    return cmd(
        f"systemd-nspawn --directory={directory} --bind-ro=/etc/resolv.conf:/etc/resolv.conf --pipe {command}",
        passthrough=passthrough,
        capture=capture,
    )


def ccmd(machine: str, command: str, use_pty: bool = False, capture: bool = False):
    """
    Run command on spawned container.
    """
    logger.info(f"Running command on container machine {machine}: {command}")
    pty = ""
    if use_pty:
        pty = "--pty"
    # TODO: Maybe add `--collect`?
    command = f"systemd-run --machine={machine} --wait --pipe --quiet {pty} {command}"
    logger.debug(f"Effective command is: {command}")
    return cmd(command, capture=capture, use_pty=use_pty)
