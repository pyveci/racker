import os
import shlex
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Union

import subprocess_tee


def is_dir_empty(path):
    """
    Efficiently check whether a directory is empty.

    https://stackoverflow.com/a/65117802
    """
    with os.scandir(path) as scan:
        return next(scan, None) is None


def cmd(command, capture: bool = False, check: bool = True):
    """
    Run command in a separate process.
    """
    try:
        if capture:
            p = subprocess_tee.run(shlex.split(command))
        else:
            p = subprocess.run(shlex.split(command), stdout=sys.stdout, stderr=sys.stderr)
        if check:
            p.check_returncode()
        return p
    except subprocess.CalledProcessError as ex:
        print(f"ERROR: Process exited with returncode {ex.returncode}. Output:\n{ex.output}")
        raise


def hcmd(command, capture: bool = False, check: bool = True):
    """
    Run command on host system.
    """
    print(f"Running command on host system: {command}")
    return cmd(command, capture=capture, check=check)


def scmd(directory: Union[Path, str], command: str):
    """
    Run command within root filesystem.
    """
    print(f"Running command within rootfs at {directory}: {command}")
    return cmd(f"systemd-nspawn --directory={directory} --bind-ro=/etc/resolv.conf:/etc/resolv.conf --pipe {command}")


def ccmd(machine: str, command: str, capture: bool = False):
    """
    Run command on spawned container.
    """
    print(f"Running command on container machine {machine}: {command}")
    command = f"systemd-run --machine={machine} --wait --quiet --pipe {command}"
    # log.debug(f"Effective command is: {command}")
    return cmd(command, capture=capture)


def fix_tty():
    """
    The login prompt messes up the terminal, let's make things sane again.

    - https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    - https://superuser.com/questions/122911/what-commands-can-i-use-to-reset-and-clear-my-terminal

    TODO: Figure out what `stty sane` does and implement it natively.
    """
    os.system("stty sane")

    # Clears the whole screen.
    # os.system("tput reset")

    # Some trial & error.
    # print("\33[3J")
    # print("\033[3J", end='')
    # print("\033[H\033[J", end="")
    # print("\033c\033[3J", end='')


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.

    https://stackoverflow.com/a/325528
    """

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def stderr_forwarder(process: subprocess.Popen):
    """
    https://stackoverflow.com/a/53751896
    """
    while True:
        byte = process.stderr.read(1)
        if byte:
            sys.stderr.buffer.write(byte)
            sys.stderr.flush()
        else:
            break


def port_is_up(host: str, port: int):
    """
    Test if a host is up.

    https://github.com/lovelysystems/lovely.testlayers/blob/0.7.0/src/lovely/testlayers/util.py#L6-L13
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ex = s.connect_ex((host, port))
    if ex == 0:
        s.close()
        return True
    return False


def wait_for_port(host: str, port: int, timeout: float = 5.0, interval: float = 0.05):
    sys.stderr.write("\n")
    status = False
    while timeout > 0:
        if port_is_up(host, port):
            status = True
            break
        time.sleep(interval)
        timeout -= interval
        sys.stderr.write(".")
        sys.stderr.flush()
    sys.stderr.write("\n")
    sys.stderr.flush()
    return status


def print_header(title: str, armor: str = "-"):
    length = len(title)
    print()
    print(armor * length)
    print(title)
    print(armor * length)


def print_section_header(title: str, armor: str = "="):
    print_header(title=title, armor=armor)
