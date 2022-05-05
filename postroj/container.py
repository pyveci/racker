# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Union

from postroj.settings import cache_directory
from postroj.util import StoppableThread, ccmd, print_header, hcmd, fix_tty


class PostrojContainer:
    """
    A lightweight wrapper to manage `systemd-nspawn` containers.
    """

    WAIT_TIMEOUT_SECONDS = 15.0

    def __init__(self, rootfs: Union[Path, str], machine: str = None):
        self.rootfs = Path(rootfs)
        if machine is None:
            machine = f"postroj-{os.path.basename(self.rootfs)}"
        self.machine = machine
        self.process: subprocess.Popen = None
        self.thread: StoppableThread = None

    def boot(self):
        """
        Boot the container in a child process, using `systemd-nspawn`.
        All operations on the container image will be ephemeral/volatile
        to ensure reproducible actions.
        """

        if not self.rootfs.exists():
            raise Exception(f"Image at {self.rootfs} not found")

        cache_directory.mkdir(parents=True, exist_ok=True)
        print(f"INFO: Cache directory is {cache_directory}")

        print_header(f"Spawning container {self.machine}")

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
        print(f"Spawning container with: {command}")

        # Invoke command in background.
        # TODO: Add option to suppress output, unless `--verbose` is selected.
        def spawn():
            self.process = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE)
        self.thread = StoppableThread(target=spawn)
        self.thread.start()

    def check_process_returncode(self):
        if self.process.returncode != 0:
            stderr = self.process.stderr.read().decode().strip()
            print("self.process.stderr:", stderr)
            hint = ""
            if "already exists" in stderr:
                hint = f"Hint: Please run `machinectl terminate {self.machine}` and try again."
            raise RuntimeError(f"Unable to spawn container {self.machine}. Reason: {stderr}. {hint}")

    def info(self):
        print_header("Host information")
        self.run("/usr/bin/hostnamectl")

    def run(self, command, capture: bool = False):
        return ccmd(self.machine, command, capture=capture)

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
            print(f"Container {self.machine} not running, skipping termination")
            return

        hcmd(f"/bin/machinectl terminate {self.machine}")

    def is_down(self):
        process = hcmd(f"/bin/systemctl is-system-running --machine={self.machine}", capture=True, check=False)
        status = process.stdout.strip()
        print(f"INFO: Container status is: {status}")
        if "Host is down" in process.stderr:
            return True
        return False

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

        print(f"Waiting for container {self.machine} to become available within {timeout} seconds")

        # Define the probe command to check whether the container has booted.
        # Possible values: Failed to connect to bus: Host is down`, `starting`, `started`, `degraded`.
        """
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
        # TODO: Compensate for "starting" output. Valid "startedness" would be any of "started" or "degraded".
        #       Background: A system can be fully booted and functional but signals "degraded" if one or more
        #       units signalled errors.
        command = f"""
            /bin/systemctl is-system-running --machine={self.machine} | egrep "(started|running|degraded)" > /dev/null
        """.strip()

        sys.stderr.write("\n")
        interval = 0.1
        while timeout > 0:

            fix_tty()
            p = subprocess.run(command, shell=True)
            if p.returncode == 0:
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
            self.kill()
            raise TimeoutError(f"Timeout while spawning container {self.machine}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill()
        fix_tty()

    def kill(self):
        self.terminate()
        if self.process is not None:
            self.process.kill()
            # time.sleep(0.1)
            self.process.terminate()
            self.process.wait()
            del self.process
            self.process = None
        if self.thread is not None:
            self.thread.stop()
            del self.thread
            self.thread = None
