# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
"""
A convenience wrapper around Windows Docker Machine by Stefan Scherer.

https://github.com/StefanScherer/windows-docker-machine
"""
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import appdirs
import pkg_resources

from postroj.util import port_is_up, cmd, fix_tty

logger = logging.getLogger(__name__)


class WinRunner:

    BOX = "2019-box"
    VCPUS = os.environ.get("RACKER_VM_VCPUS", 6)
    MEMORY = os.environ.get("RACKER_VM_MEMORY", 6144)

    def __init__(self, image: str):
        self.image_base = image
        self.image_real = "racker-runtime/" + self.image_base.replace("/", "-")

        self.workdir = Path(appdirs.user_state_dir(appname="racker"))
        self.workdir.mkdir(exist_ok=True, parents=True)

        self.wdmdir = self.workdir / "windows-docker-machine"

    def setup(self):
        """
        Prepare virtual machine and adjust system resources.
        """
        if not self.wdmdir.exists():
            logger.info(f"Installing Windows Docker Machine into {self.wdmdir}")
            command = f"""
                cd '{self.workdir}'
                git clone https://github.com/StefanScherer/windows-docker-machine
                cd windows-docker-machine
                #ls -alF
                sed -i 's/v.cpus = [0-9]\+/v.cpus = {self.VCPUS}/' Vagrantfile
                sed -i 's/v.memory = [0-9]\+/v.memory = {self.MEMORY}/' Vagrantfile
                sed -i 's/v.maxmemory = [0-9]\+/v.maxmemory = {self.MEMORY}/' Vagrantfile
            """
            hshell(command)
        else:
            logger.info(f"Windows Docker Machine already installed into {self.wdmdir}")

    def start(self):
        """
        Start the "Windows Docker Machine" virtual machine.

        - Launch a virtual machine using Vagrant.
        - Connect to Docker daemon on virtual machine.
        - Provision the operating system image with additional software.
        """

        if self.docker_context_online():
            logger.info("Docker context is online")
        else:
            logger.info("Docker context is offline, starting VirtualBox VM with Vagrant")
            cmd(f"vagrant provision {self.BOX}", cwd=self.wdmdir, use_stderr=True)
            cmd(f"vagrant up --provider=virtualbox {self.BOX}", cwd=self.wdmdir, use_stderr=True)

        logger.info("Pinging Docker context")
        if not self.docker_context_online():
            raise IOError(f"Unable to bring up Docker context {self.BOX}")

        # Attention: This can run into 60 second timeouts.
        # TODO: Use ``with stopit.ThreadingTimeout(timeout) as to_ctx_mgr``.
        # TODO: Make timeout values configurable.
        # https://github.com/moby/moby/blob/0e04b514fb/integration-cli/docker_cli_run_test.go
        cmd(f"docker --context={self.BOX} ps", capture=True)

        if "nanoserver" in self.image_base:
            self.image_real = self.image_base
        else:
            self.provision_image()

    def provision_image(self):
        """
        Provide an operating system image by building a Docker image using `winrunner.Dockerfile`.

        - Provision a Windows operating system image with additional software.
        - Automatically installs the open source version of the Chocolatey package manager.
        - By default, it installs `git`, `curl`, and `wget`.
        """

        logger.info(f"Provisioning Docker image for Windows environment based on {self.image_base}")
        dockerfile = pkg_resources.resource_filename("postroj", "winrunner.Dockerfile")
        tmpdir = tempfile.mkdtemp()
        command = f"docker --context={self.BOX} build --platform=windows/amd64 " \
                  f"--file={dockerfile} --build-arg=BASE_IMAGE={self.image_base} --tag={self.image_real} {tmpdir}"
        logger.debug(f"Running command: {command}")
        try:
            hcmd(command)
        except subprocess.CalledProcessError:
            raise
        finally:
            os.rmdir(tmpdir)

    def cmd(self, command):
        command = f"cmd /C {command}"
        return self.run(command)

    def powershell(self, command):
        command = f"powershell -Command {command}"
        return self.run(command)

    def run(self, command, interactive: bool = False, tty: bool = False):
        logger.info(f"Running guest command: {command}")

        option_interactive = ""
        if interactive or tty:
            option_interactive = "-it"

        command = f"docker --context={self.BOX} run {option_interactive} --rm {self.image_real} {command}"

        # When an interactive prompt is requested, spawn a shell without further ado.
        if interactive or tty:
            ccmd(command, use_pty=True)

        # Otherwise, capture stdout and mangle its output.
        else:
            outcome = cmd(command)
            return outcome

    def docker_context_online(self):
        """
        Test if the Docker context is online.
        """
        logger.info(f"Checking connectivity to Docker daemon in Windows context '{self.BOX}'")
        try:
            response = cmd(f"docker context inspect {self.BOX}", capture=True)
        except:
            logger.warning(f"Docker context {self.BOX} not online or not created yet")
            return False

        data = json.loads(response.stdout)
        address = urlparse(data[0]["Endpoints"]["docker"]["Host"])

        logger.info(f"Checking TCP connectivity to {address.hostname}:{address.port}")
        return port_is_up(address.hostname, address.port)


def hcmd(command, cwd=None, silent=False):
    logger.debug(f"Running command: {command}")
    return cmd(command, cwd=cwd, use_stderr=True)


def hshell(command, cwd=None):
    logger.debug(f"Running command: {command}")
    #return cmd(command, cwd=cwd, passthrough=True).stdout
    return subprocess.check_output(command, shell=True, cwd=cwd).decode()


def ccmd(command, use_pty=False):
    logger.debug(f"Running command: {command}")
    p = cmd(command=command, use_pty=use_pty)
    stdout = p.stdout
    fix_tty()
    return stdout
