# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Union

from postroj.util import StoppableThread, ccmd, cmd_with_stderr, stderr_forwarder, print_header


class PostrojContainer:
    """
    A lightweight wrapper to manage `systemd-nspawn` containers.
    """

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

        # TODO: Why does `--ephemeral` not work?
        # TODO: Maybe use `--register=false`?
        # TODO: What about `--notify-ready=true`?
        command = f"""
            /usr/bin/systemd-nspawn \
                --quiet --boot --link-journal=try-guest \
                --volatile=overlay --bind-ro=/etc/resolv.conf:/etc/resolv.conf \
                --directory={self.rootfs} --machine={self.machine}
        """.strip()
        print(f"Spawning container with: {command}")

        # Invoke command in background.
        # TODO: Add option to suppress output, unless `--verbose` is selected.
        self.process = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE)
        self.thread = StoppableThread(target=stderr_forwarder, args=(self.process,))
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
        print(self.run("/usr/bin/hostnamectl"))

    def run(self, command, verbose=False, **kwargs):
        #kwargs["stderr"] = subprocess.PIPE
        output = ccmd(self.machine, command, **kwargs)
        if verbose:
            print(output)
        return output
        
    def terminate(self):
        """
        Shut down the container.
        """

        if self.is_down():
            return

        print(f"Terminating container {self.machine}")
        subprocess.check_output(["/bin/machinectl", "poweroff", self.machine])

        # TODO: Appropriately wait for the container to shut down?
        # subprocess.check_output(["/bin/machinectl", "terminate", self.machine])

    def is_down(self):
        command = f"/bin/systemctl is-system-running --machine={self.machine}"
        stderr = cmd_with_stderr(command)
        if "Host is down" in stderr:
            return True
        return False

    def wait(self):
        """
        Wait for the container to have started completely.

        Currently, this uses a quirky poll-based implementation. Maybe we can
        find a better, event-based solution. We already played around with
        `pystemd.run` [1], but that would increase the dependency depth
        significantly. However, we are not completely opposed to bringing it to
        the code base.

        [1] https://github.com/facebookincubator/pystemd
        """
        # TODO: Maybe we can find a better way to wait for the machine to boot completely.
        command = f"""
            /bin/systemctl is-system-running --machine={self.machine} | egrep -v "(starting|down)"
        """.strip()
        print(f"Waiting for container {self.machine} to boot completely")
        # Possible values: `Failed to connect to bus: Host is down`, `starting`, `started`, `degraded`.
        # TODO: Compensate for "starting" output. Valid "startedness" would be any of "started" or "degraded".
        #       Background: A system can be fully booted and functional but signals "degraded" if one or more
        #       units signalled errors.
        seconds = 5
        interval = 0.1
        count = int(1 / interval * seconds)
        while True:
            os.system("stty sane")
            #print("\33[3J")
            print(command)
            p = subprocess.run(command, shell=True)
            if p.returncode == 0:
                break
            if count == 0:
                self.kill()
                raise Exception("Timeout")
            count -= 1
            time.sleep(interval)

        # The login prompt messes up the terminal, let's make things sane again.
        # https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
        # https://superuser.com/questions/122911/what-commands-can-i-use-to-reset-and-clear-my-terminal
        # TODO: Figure out what `stty sane` does and implement it natively.
        os.system("stty sane")

        # Clears the whole screen.
        # os.system("tput reset")

        # Some trial & error.
        # print("\033[3J", end='')
        # print("\033[H\033[J", end="")
        # print("\033c\033[3J", end='')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill()

    def kill(self):
        self.terminate()
        if self.process is not None:
            self.process.kill()
            time.sleep(0.1)
            self.process.terminate()
            self.process.wait()
            del self.process
            self.process = None
        if self.thread is not None:
            self.thread.stop()
            del self.thread
            self.thread = None


if __name__ == "__main__":
    """
    Spawn a container and wait until it has booted completely.
    Then, display host information about the container.
    """
    # TODO: Make this configurable.
    rootfs_paths = [
        Path("/var/lib/postroj/images/debian-buster"),
    ]
    for rootfs_path in rootfs_paths:
        with PostrojContainer(rootfs=rootfs_path) as pc:
            pc.boot()
            pc.wait()
            pc.info()
