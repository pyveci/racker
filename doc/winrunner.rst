##############
Windows runner
##############

.. note::

    This is still a work in progress.


*****
About
*****

Launch an interactive command prompt (cmd, PowerShell or Bash) within a Windows
environment or invoke programs non-interactively.

References
==========

- https://github.com/PyTables/PyTables/pull/872#issuecomment-773535041


*****
Setup
*****
::

    # Install VirtualBox, Vagrant, and Docker.
    brew install virtualbox vagrant docker

    # Install Windows VM with Docker environment.
    git clone https://github.com/StefanScherer/windows-docker-machine
    cd windows-docker-machine

    # Adjust resources.
    sed -i 's/v.memory = 2048/v.memory = 8192/' Vagrantfile
    sed -i 's/v.cpus = 2/v.cpus = 8/' Vagrantfile

    # Run the box.
    vagrant up --provider virtualbox 2019-box


*****
Usage
*****

Basic usage::

    racker run --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019-amd64 \
        cmd /C echo "Hello, world."

Install software packages using `Chocolatey`_::

    racker run -it --rm --platform=windows/amd64 mcr.microsoft.com/windows/servercore:ltsc2019-amd64 \
        powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    choco install --yes git
    Install-ChocolateyPath -PathToInstall "$($env:SystemDrive)\Program Files\Git\bin"


*************
Miscellaneous
*************

Manipulating ``PATH``
=====================

Display the content of the ``PATH`` environment variable::

    echo %PATH%
    (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path).Path

Set the content of the ``PATH`` environment variable::

    setx PATH "$env:path;$($env:SystemDrive)\Program Files\Git\bin" -m
    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$($env:SystemDrive)\Program Files\Git\bin", "Machine")


Which shell spawns faster?
==========================
::

    time docker --context=2019-box run -it --rm openjdk:17-windowsservercore-1809 cmd /C "echo Hello, world."

::

    time docker --context=2019-box run -it --rm openjdk:17-windowsservercore-1809 powershell -Command "echo 'Hello, world.'"



***********
Admin guide
***********

::

    docker --context=2019-box run -it --rm openjdk:17-windowsservercore-1809 cmd
    wmic cpu get NumberOfCores
    wmic computersystem get TotalPhysicalMemory

::

    docker --context=2019-box run -it --rm openjdk:17-windowsservercore-1809 powershell
    Get-ComputerInfo

Terminate an environment::

    docker --context=2019-box ps
    docker --context=2019-box stop 5e2fe406ccbc


.. _Chocolatey: https://chocolatey.org/
