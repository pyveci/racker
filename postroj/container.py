# Manage `systemd-nspawn` containers.
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time


# TODO: Make this configurable.
directory = Path("/var/lib/postroj/images/ubuntu-focal")
machine = "postroj-ubuntu-focal"

# TOOD: Remove global variable.
process = None


def install():
    """
    Install a container image suitable for running with `systemd-nspawn`.

    TODO: Provide implementation for image download and setup.
          It is around the corner, see `doc/images.rst`.
    """
    pass


def boot():
    """
    Boot the container in a child process, using `systemd-nspawn`.
    """
    global process

    if not directory.exists():
        raise Exception(f"Image at {directory} not found")

    command = f"""
        /usr/bin/systemd-nspawn \
            --quiet --boot --link-journal=try-guest \
            --volatile=overlay --bind-ro=/etc/resolv.conf:/etc/resolv.conf \
            --directory={directory} --machine={machine}
    """.strip()
    print(command)
    # Invoke command in background.
    # TODO: Add option to suppress output, unless `--verbose` is selected.
    process = subprocess.Popen(shlex.split(command))


def shutdown():
    """
    Shut down the container.
    """
    subprocess.check_output(["/bin/machinectl", "poweroff", machine])

def wait():
    """
    Wait for the container to have started completely.

    Currently, this uses a quirky poll-based implementation. Maybe we find a
    better, event-based solution. We already played around with `pystemd` [1],
    but that would increase the dependency depth significantly. However, we
    are not completely opposed to bringing it to the code base.

    https://github.com/facebookincubator/pystemd

    [1] Actually, we used `pystemd.run` to
    """
    # TODO: Maybe we can find a better way to wait for the machine to boot completely.
    command = f"""
        /bin/systemctl is-system-running --machine={machine} | egrep -v "(starting|down)"
    """.strip()
    # Possible values: `Failed to connect to bus: Host is down`, `starting`, `started`, `degraded`.
    # TODO: Compensate for "starting" output. Valid "startedness" would be any of "started" or "degraded".
    seconds = 5
    interval = 0.2
    count = int(1 / interval * seconds)
    while True:
        os.system("stty sane")
        print("\33[3J")
        print(command)
        p = subprocess.run(command, shell=True)
        if p.returncode == 0:
            break
        if count == 0:
            raise Exception("Timeout")
        count -= 1
        time.sleep(interval)

    # The login prompt messes up the terminal, let's make things sane again.
    # https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    # https://superuser.com/questions/122911/what-commands-can-i-use-to-reset-and-clear-my-terminal
    # TODO: Figure out what `stty sane` does and implement it natively.
    os.system("stty sane")

    # Clears the whole screen.
    #os.system("tput reset")

    # Some trial & error.
    #print("\033[3J", end='')
    #print("\033[H\033[J", end="")
    #print("\033c\033[3J", end='')


def probe():
    """
    Commands to setup and run the probe.
    """
    run("/bin/systemctl is-active systemd-journald")


def probe_apache():
    """
    Commands to setup and run the probe.
    """

    # Setup service
    run("/usr/bin/apt-get update")
    run("/usr/bin/apt-get install --yes apache2 curl")
    run("/bin/systemctl enable apache2")
    run("/bin/systemctl start apache2")

    # Probe
    run("/bin/systemctl is-active apache2")

    # TODO: Improve waiting until port is reachable.
    time.sleep(1)
    run("/usr/bin/curl localhost:80")


def run(command):
    """
    Generic routine to run command within container.

    STDERR will be displayed, STDOUT will be captured.
    """
    print(f"Running command: {command}")
    command = f"""
        systemd-run --machine={machine} --wait --quiet --pipe {command}
    """
    output = subprocess.check_output(shlex.split(command))
    print(output.decode())


def main():
    """
    Run the whole sequence of:

    - Spawn a container and wait until it has booted completely.
    - Setup and invoke probe commands.
    """

    try:
        boot()
        wait()
        probe()
        shutdown()
    finally:
        if process is not None:
            process.terminate()
            process.wait()


if __name__ == "__main__":
    main()
