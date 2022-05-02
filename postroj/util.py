import os
import shlex
import subprocess
import sys
import threading
from pathlib import Path
from typing import Union


def is_dir_empty(path):
    """
    Efficiently check whether a directory is empty.

    https://stackoverflow.com/a/65117802
    """
    with os.scandir(path) as scan:
        return next(scan, None) is None


def cmd(command):
    """
    Spawn a system command in a separate process.
    """
    print(f"Running command on host system: {command}")
    return subprocess.check_output(shlex.split(command)).decode()


def cmd_with_stderr(command):
    process = subprocess.run(shlex.split(command), stderr=subprocess.PIPE)
    return process.stderr.decode()


def ccmd(machine: str, command: str, **kwargs):
    """
    Run command within spawned container.

    STDERR will be displayed, STDOUT will be captured and returned.
    """
    print(f"Running command on container machine {machine}: {command}")
    command = f"systemd-run --machine={machine} --wait --quiet --pipe {command}"
    print(f"Effective command is: {command}")
    try:
        return subprocess.check_output(shlex.split(command), **kwargs).decode()
    except subprocess.CalledProcessError as ex:
        print(f"Process exited with returncode {ex.returncode}. Output:\n{ex.output}")
        raise


def scmd(directory: Union[Path, str], command: str):
    """
    Run command within root filesystem of unspawned container.
    """
    return cmd(f"systemd-nspawn --directory={directory} --pipe {command}")


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
