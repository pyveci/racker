#################
postroj winrunner
#################

.. note::

    This is still a work in progress.


*****
About
*****

- https://github.com/PyTables/PyTables/pull/872#issuecomment-773535041


********
Synopsis
********
::

    # Basic usage.
    postroj invoke --system=windows-1809 -- cmd /C echo hello


*****
Setup
*****
::

    # Install VirtualBox, Vagrant and Docker.
    brew install virtualbox docker vagrant

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

