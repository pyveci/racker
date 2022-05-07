# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
"""
A convenience wrapper around Windows Docker Machine.

https://github.com/StefanScherer/windows-docker-machine
"""
import json
import shlex
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import click

from postroj.util import port_is_up


class WinRunner:

    BOX = "2019-box"

    def __init__(self):
        self.workdir = Path.home() / "postroj"
        self.workdir.mkdir(exist_ok=True)

        self.wdmdir = self.workdir / "windows-docker-machine"

    def setup(self):
        if not self.wdmdir.exists():
            click.echo("Installing Windows Docker Machine")
            command = f"""
                cd {self.workdir}
                git clone https://github.com/StefanScherer/windows-docker-machine
                cd windows-docker-machine
                #ls -alF
                sed -i 's/v.memory = 2048/v.memory = 8192/' Vagrantfile
                sed -i 's/v.cpus = 2/v.cpus = 8/' Vagrantfile
            """
            run(command, shell=True)
        else:
            click.echo("Windows Docker Machine already installed")

    def start(self):

        if self.docker_context_online():
            click.echo("Docker context is online")
        else:
            click.echo("Docker context is offline, starting VirtualBox VM with Vagrant")
            run(f"vagrant up --provider=virtualbox {self.BOX}", cwd=self.wdmdir)

        click.echo("Pinging Docker context")
        run("docker --context=2019-box ps")

    def cmd(self, command):
        command = f"cmd /C {command}"
        return self.run(command)

    def powershell(self, command):
        command = f"powershell -Command {command}"
        return self.run(command)

    def run(self, command, strip_armor=True, translate_newlines=True):
        click.echo(f"Running command: {command}")
        command = f"docker --context={self.BOX} run -it --rm openjdk:17-windowsservercore-1809 {command}"
        outcome = run(command)
        if strip_armor:
            """
            b'\x1b[2J\x1b[?25l\x1b[m\x1b[H\r\n\r\n...\r\n\x1b[H\x1b]0;C:\\Windows\\system32\\cmd.exe\x00\x07\x1b[?25h\x1b[?25lhello \r\n\x1b[?25h'
            """
            prefix = "\x1b[?25h\x1b[?25l"
            suffix = "\x1b[?25h"
            cutoff_left = outcome.find(prefix) + len(prefix)
            cutoff_right = outcome.rfind(suffix)
            outcome = outcome[cutoff_left:cutoff_right]
        if translate_newlines:
            outcome = outcome.replace("\r\n", "\n")
        # print(outcome.encode())
        return outcome

    def docker_context_online(self):
        """
        Test if a Docker context is online.
        """
        response = json.loads(run(f"docker context inspect {self.BOX}"))
        address = urlparse(response[0]["Endpoints"]["docker"]["Host"])
        return port_is_up(address.hostname, address.port)


def run(command, shell=False, cwd=None):
    """
    Generic routine to run command within container.

    STDERR will be displayed, STDOUT will be captured.
    """
    # print(f"Running command: {command}")
    # command = f"""
    #    systemd-run --machine={machine} --wait --quiet --pipe {command}
    # """
    if shell:
        output = subprocess.check_output(command, shell=shell, cwd=cwd)
    else:
        output = subprocess.check_output(shlex.split(command), cwd=cwd)
    return output.decode()
