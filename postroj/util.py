import os
import shlex
import subprocess


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

def scmd(directory: Union[Path, str], command: str):
    """
    Run command within root filesystem of unspawned container.
    """
    return cmd(f"systemd-nspawn --directory={directory} --pipe {command}")

