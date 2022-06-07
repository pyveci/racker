# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import asyncio
import dataclasses
import enum
import io
import json
import logging
import os
import shlex
import socket
import subprocess
import sys
import threading
import time
from abc import abstractmethod
from asyncio import AbstractEventLoop
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from types import TracebackType
from typing import Optional, Tuple, Union

import click
import furl
import subprocess_tee

from postroj.exceptions import OsReleaseFileMissing

logger = logging.getLogger(__name__)

USE_LOGGING = True


def is_dir_empty(path: Path, missing_ok=False):
    """
    Efficiently check whether a directory is empty.

    https://stackoverflow.com/a/65117802
    """
    if missing_ok and not path.exists():
        return True
    with os.scandir(path) as scan:
        return next(scan, None) is None


def cmd(command, check: bool = True, passthrough: bool = None, capture: bool = False, use_stderr: bool = False, use_pty: bool = False, cwd: Union[Path, str] = None, **kwargs):
    """
    Run command in a separate process.
    """
    try:
        command_encoded = shlex.split(command)
        kwargs.update({
            "cwd": cwd,
        })
        if use_stderr:
            kwargs["stdout"] = sys.stderr
            kwargs["stderr"] = sys.stderr

        if passthrough in [True, False] or capture and not use_pty:
            logger.debug(f"Running with subprocess_tee: {command}")
            p = subprocess_tee.run(command_encoded, tee=passthrough, **kwargs)
        else:
            logger.debug(f"Running with subprocess:     {command} {kwargs}")
            p = subprocess.run(command_encoded, **kwargs)
        """
        if (not passthrough and not capture) or use_pty:
            p = subprocess.run(command, **kwargs)
        else:
            p = subprocess_tee.run(command, tee=passthrough, **kwargs)
        """
        """
        if capture:
            p = subprocess_tee.run(shlex.split(command), tee=passthrough)
        else:
            if passthrough:
                stdout = sys.stdout
                stderr = sys.stderr
            else:
                stdout = subprocess.DEVNULL
                stderr = subprocess.DEVNULL

            # FIXME: Work around `io.UnsupportedOperation: fileno` under `pytest`.
            if "PYTEST_CURRENT_TEST" in os.environ or "TESTING" in os.environ:
                try:
                    stdout.fileno()
                except io.UnsupportedOperation:
                    stdout = None
                try:
                    stderr.fileno()
                except io.UnsupportedOperation:
                    stderr = None

            p = subprocess.run(shlex.split(command), stdout=stdout, stderr=stderr)
        """
        if check:
            p.check_returncode()
        return p
    except subprocess.CalledProcessError as ex:
        message = subprocess_get_error_message(exception=ex, process=p)
        logger.debug(f"Invoking command failed. {message}")
        raise


def hcmd(command, check: bool = True, passthrough: bool = True, capture: bool = False):
    """
    Run command on host system.
    """
    logger.info(f"Running command on host system: {command}")
    return cmd(command, check=check, passthrough=passthrough, capture=capture)


def fix_tty():
    """
    The login prompt messes up the terminal, let's make things sane again.

    - https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
    - https://superuser.com/questions/122911/what-commands-can-i-use-to-reset-and-clear-my-terminal

    TODO: Figure out what `stty sane` does and implement it natively.
    """

    # Fix `stty: 'standard input': Inappropriate ioctl for device`.
    if not sys.stdin.isatty():
        return

    if sys.stdout.isatty():
        os.system("stty sane")
        os.system("tput cnorm")

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

    def __init__(self, *args, **kwargs):
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
    # TODO: Make connect timeout configurable.
    s.settimeout(5)
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

    if USE_LOGGING:
        logger.info(title)
        return

    length = len(title)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print()
        print(armor * length)
        print(title)
        print(armor * length)
    buffer.seek(0)
    print(buffer.read().rstrip())


def print_section_header(title: str, armor: str = "="):
    print_header(title=title, armor=armor)


# https://github.com/python/mypy/issues/4676
_SysExcInfoType = Union[Tuple[type, BaseException, TracebackType], Tuple[None, None, None]]


class LongRunningProcess:
    """
    Invoke command in separate thread, suitable for running `systemd-nspawn --boot`.

    TODO: Add option to suppress output, unless `--verbose` is selected.
    """

    def __init__(self):

        # A handle to the subprocess running the command.
        self.process: Optional[subprocess.Popen] = None

        # A reference to the thread wrapping the command invocation.
        self.thread: Optional[StoppableThread] = None

        # When an exception occurs within a thread, this will propagate the
        # exception info to the main thread.
        self.thread_exc_info: Optional[_SysExcInfoType] = None

        # An `asyncio` event loop for the wrapper thread.
        self.loop: Optional[AbstractEventLoop] = None

        # When the process invocation croaks, it will get signalled.
        self.abort_signal: threading.Event = threading.Event()

    def start(self, command: str):
        """
        Launch command within dedicated thread.
        """
        self.thread = StoppableThread(target=self._start, args=(command,))
        self.thread.start()

    def stop(self):
        """
        Terminate and clean up process and thread wrapper objects.
        """
        if self.process is not None and not isinstance(self.process, subprocess_tee.CompletedProcess):
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

    def _start(self, command: str):
        """
        Thread which is invoking the command in a subprocess.
        It will block until the command has terminated.
        """

        # Create a dedicated `asyncio` event loop.
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Launch command in subprocess.
        self.process = subprocess_tee.run(shlex.split(command))

        # When the invocation was successful, return early.
        try:
            self.process.check_returncode()
            return self.process

        # When the invocation failed, propagate the exception to the main thread.
        except subprocess.CalledProcessError:
            self.thread_exc_info = sys.exc_info()
            # raise
            # logger.exception()

        # Signal the invocation failed, for whatever reason.
        # That means, don't run any teardown code on the container.
        # Instead, leave it completely untouched.
        self.abort_signal.set()

    def check(self):
        """
        Check the abort signal for a little while after the process was launched.

        When there was an exception, propagate it to the abort handler and the
        error handler, optionally augmenting the exception information by passing
        it through a callback handler.
        """
        if self.abort_signal.wait(0.25):
            self.abort_handler()
            if self.thread_exc_info:
                exc_info = self.thread_exc_info
                exc_info = self.error_handler(exc_info)
                raise exc_info[1].with_traceback(exc_info[2])

    @abstractmethod
    def abort_handler(self):
        """
        Will be called immediately after an exception happened while launching the process.
        """
        pass

    @abstractmethod
    def error_handler(self, exc_info: _SysExcInfoType):
        """
        Will be called when `exc_info` data is being propagated from a secondary thread.
        It can be used to augment the exception information.
        """
        return exc_info


def setup_logging(level=logging.INFO):
    log_format = "%(asctime)-15s [%(name)-18s] %(levelname)-8s: %(message)s"
    logging.basicConfig(format=log_format, stream=sys.stderr, level=level)


@contextmanager
def noop():
    """
    A context manager which does nothing.

    It can be used as a placeholder when the code flow needs to conditionally
    swap another contextmanager in or out.
    """
    yield


@contextmanager
def stdout_to_stderr():
    """
    A context manager which redirects stdout to stderr for the wrapped context.
    Afterwards, it restores the previous assignment.
    """
    previous = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = previous


@contextmanager
def mask_logging(highest_level=logging.CRITICAL):
    """
    A context manager that will prevent any logging messages
    triggered during the body from being processed.

    :param highest_level: the maximum logging level in use.
      This would only need to be changed if a custom level greater than CRITICAL
      is defined.

    Source: https://gist.github.com/simon-weber/7853144
    """
    # two kind-of hacks here:
    #    * can't get the highest logging level in effect => delegate to the user
    #    * can't get the current module-level override => use an undocumented
    #       (but non-private!) interface

    previous_level = logging.root.manager.disable

    logging.disable(highest_level)

    try:
        yield
    finally:
        logging.disable(previous_level)


class JsonEncoderPlus(json.JSONEncoder):
    """
    JSON encoder with support for serializing Enums, Data Classes, and `furl` instances.

    - https://docs.python.org/3/library/json.html#json.JSONEncoder
    - https://docs.python.org/3/library/enum.html
    - https://docs.python.org/3/library/dataclasses.html
    - https://github.com/gruns/furl
    """

    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return obj.value
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        elif isinstance(obj, furl.furl):
            return obj.asdict()
        return json.JSONEncoder.default(self, obj)


def to_json(obj, pretty=True):
    """
    Serialize any object to JSON by using a custom encoder.
    """
    kwargs = {}
    if pretty:
        kwargs["indent"] = 2
    return json.dumps(obj, cls=JsonEncoderPlus, **kwargs)


def boot(ctx: click.Context, verbose: bool, debug: bool):

    # Debugging.
    # click.echo(f"Verbose mode is {'on' if verbose else 'off'}", err=True)
    # click.echo(f"Debug mode is {'on' if debug else 'off'}", err=True)

    # Adjust log level according to subcommand.
    # `racker run` should be more silent by default.
    if ctx.invoked_subcommand == "run":
        log_level = logging.WARNING
    else:
        log_level = logging.INFO

    # Adjust log level according to `verbose` / `debug` flags.
    if verbose:
        log_level = logging.INFO
    if debug:
        log_level = logging.DEBUG

    # Setup logging, according to `verbose` / `debug` flags.
    setup_logging(level=log_level)


def subprocess_get_error_message(exception: subprocess.CalledProcessError, process: Optional[subprocess.Popen] = None):

    # Capture stderr output into error message.
    cmd = " ".join(exception.cmd)
    message = f"Command '{cmd}' returned non-zero exit status {exception.returncode}."

    reason = None
    if exception.stderr:
        reason = exception.stderr.strip()

    if exception.stdout:
        stdout_prefix = exception.stdout[:200]
        if not reason and "execv" in stdout_prefix and "failed" in stdout_prefix:
            reason = exception.stdout.strip()

    # Assume exit status 203 from `systemd-run` means "file/command not found".
    # TODO: Validate this assumption.
    if not reason and exception.returncode == 203:
        try:
            real_command = exception.cmd[-1].split(" ")[0]
        except IndexError:
            real_command = "<unknown>"
        reason = f"{real_command}: No such file or directory"

    if reason:
        message += f" Reason: {reason}"
    return message


def subprocess_forward_stderr_stdout(exception: subprocess.CalledProcessError):
    # Propagate stderr.
    sys.stderr.write(exception.stderr)
    sys.stderr.flush()

    # Propagate stdout.
    sys.stdout.write(exception.stdout)
    sys.stdout.flush()


def find_rootfs(image_path: Union[Path, str]) -> Path:
    """
    Check for existence of `/etc/os-release` file in OS root directory.
    When `systemd-nspawn` would encounter an OS root directory without an
    `/etc/os-release` file, it would croak like::

        Directory /path/to/rootfs doesn't look like an OS root directory (os-release file is missing). Refusing.
    """
    image_path = Path(image_path)
    os_release_file = Path("./etc/os-release")
    os_release_candidates = [
        # Image directory contains rootfs directly.
        image_path / os_release_file,
        # Image directory contains "rootfs" subdirectory, having been converted with `umoci`.
        image_path / "rootfs" / os_release_file,
    ]
    for candidate in os_release_candidates:
        if candidate.exists():
            return candidate.parent.parent

    raise OsReleaseFileMissing(
        f"OS root directory {image_path} lacks an operating system (os-release file is missing)."
    )
