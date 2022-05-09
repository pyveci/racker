# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple, Union

import subprocess_tee

from postroj.settings import appsettings
from postroj.util import LongRunningProcess, _SysExcInfoType, ccmd, fix_tty, hcmd, mask_logging, noop, print_header

logger = logging.getLogger(__name__)


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


class PostrojContainer:
    """
    A lightweight wrapper to manage `systemd-nspawn` containers.
    """

    WAIT_TIMEOUT_SECONDS = 15.0

    def __init__(self, rootfs: Union[Path, str], machine: str = None):
        """
        Initialize container wrapper infrastructure and machine name.
        """

        # The path to the rootfs filesystem image.
        self.rootfs: Path = Path(rootfs)

        # Augment the machine name.
        if machine is None:
            machine = f"postroj-{os.path.basename(self.rootfs)}"
        self.machine: str = machine

        # Flag to suppress destroying the container on teardown.
        # Needed when detecting the container is already running.
        self.destroy_after_use: bool = True

        # Process wrapper for invoking `systemd-nspawn --boot`.
        self.launcher: Optional[NspawnLauncher] = None

    def boot(self):
        """
        Boot the container in a child process, using `systemd-nspawn`.
        All operations on the container image will be ephemeral/volatile
        to ensure reproducible actions.
        """

        cache_directory = appsettings.cache_directory

        if not self.rootfs.exists():
            raise Exception(f"Image at {self.rootfs} not found")

        cache_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache directory is {cache_directory}")

        print_header(f"Spawning container {self.machine} with filesystem at {self.rootfs}")

        """
        if not self.is_down():
            self.destroy_after_use = False
            hint = f"Hint: Please run `machinectl terminate {self.machine}` and try again."
            raise RuntimeError(f"Container {self.machine} already running. {hint}")
        """

        # Define the command to spawn the container.
        # TODO: Why does `--ephemeral` not work?
        # TODO: Maybe use `--register=false`?
        # TODO: What about `--notify-ready=true`?
        command = f"""
            /usr/bin/systemd-nspawn \
                --quiet --boot --link-journal=try-guest \
                --volatile=overlay \
                --bind-ro=/etc/resolv.conf:/etc/resolv.conf \
                --bind={cache_directory}:{cache_directory} \
                --directory={self.rootfs} \
                --machine={self.machine}
        """.strip()
        logger.info(f"Launch command is: {command}")

        self.launcher = NspawnLauncher(container=self)
        self.launcher.start(command=command)
        self.launcher.check()

    def info(self):
        """
        Display host information about spawned container.
        """
        print_header("Host information")
        self.run("/usr/bin/hostnamectl")

    def run(self, command, use_pty: bool = False, capture: bool = False):
        """
        Run command on spawned container.
        """
        return ccmd(self.machine, command, use_pty=use_pty, capture=capture)

    def terminate(self):
        """
        Terminate the container.

        Immediately terminates a virtual machine or container, without cleanly shutting it down.
        This kills all processes of the virtual machine or container and deallocates all resources
        attached to that instance. Use `poweroff` to issue a clean shutdown request.

        -- https://www.freedesktop.org/software/systemd/man/machinectl.html#terminate%20NAME%E2%80%A6
        """

        print_header(f"Shutting down container {self.machine}")

        if self.is_down():
            logger.info(f"Container {self.machine} not running, skipping termination")
            return

        hcmd(f"/bin/machinectl terminate {self.machine}")

    def is_down(self) -> bool:
        """
        Determine if the container is down.

        This is, when::

            systemctl is-system-running --machine=<machine>

        prints this message to stderr::

            Failed to connect to bus: Host is down
        """
        status, errors = self.get_status()
        if "Host is down" in errors:
            return True
        return False

    def is_running(self, silent: bool = False) -> bool:
        """
        Determine if the container is running.

        This is, when::

            systemctl is-system-running --machine=<machine>

        prints one of those messages to stdout::

            started
            running
            degraded

        Background: A system can be fully booted and functional but signals "degraded"
                    if one or more units signalled errors.

        # Define the probe command to check whether the container has booted completely.

        # Possible values: Single words on stdout, other messages on stderr.
        - Failed to connect to bus: Host is down
        - Failed to connect to bus: Protocol error
        - starting
        - started, running, degraded
        - stopping
        - Failed to query system state: Connection reset by peer
        - unknown
        - Failed to connect to bus: Protocol error
        - Failed to connect to bus: No such file or directory
        - Failed to connect to bus: Host is down
        """

        # When `silent` mode is requested, suppress any logging completely.
        logging_context = silent and mask_logging or noop
        with logging_context():
            status, errors = self.get_status()
            if status in ["started", "running", "degraded"]:
                return True
            return False

    def get_status(self) -> Tuple[str, str]:
        """
        Get status of system.
        """
        process = hcmd(
            f"/bin/systemctl is-system-running --machine={self.machine}", check=False, passthrough=False, capture=True
        )
        status = process.stdout.strip()
        errors = process.stderr
        logger.info(f"Container status is: {status or '<unknown>'}")
        if errors.strip():
            logger.info(f"Container status messages:\n{errors}")
        return status, errors

    def wait(self, timeout=WAIT_TIMEOUT_SECONDS):
        """
        Wait for the container to have started completely.
        Currently, this uses a quirky poll-based implementation.

        TODO: Maybe we can find a better, event-based solution.

        We already played around with `pystemd.run` [1], but that would
        increase the dependency depth significantly. However, we are not
        completely opposed to bringing it to the code base.

        [1] https://github.com/facebookincubator/pystemd
        """

        logger.info(f"Waiting for container {self.machine} to become available within {timeout} seconds")

        sys.stderr.write("\n")
        interval = 0.1
        while timeout > 0:

            fix_tty()
            if self.is_running(silent=True):
                break

            time.sleep(interval)
            timeout -= interval
            sys.stderr.write(".")
            sys.stderr.flush()

        sys.stderr.write("\n")
        sys.stderr.flush()

        fix_tty()

        # When the container was not able to boot completely and in time, kill
        # it and raise an exception.
        if timeout <= 0:
            self.destroy()
            raise TimeoutError(f"Timeout while spawning container {self.machine}")

    def __enter__(self):
        """
        When entering the context manager, nothing special has to be initialized.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Destroy the container when exiting the context manager.
        """
        self.destroy()
        fix_tty()

    def destroy(self):
        """
        Destroy container and its management/launcher machinery.
        """
        if self.destroy_after_use:
            self.terminate()
        else:
            logger.info("Skipping container destruction")

        if self.launcher:
            self.launcher.stop()
