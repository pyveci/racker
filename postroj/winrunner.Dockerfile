# Provision a Windows operating system image with additional software.
# Automatically installs the open source version of the Chocolatey package manager.
# By default, it installs `git`, `curl`, and `wget`.

ARG BASE_IMAGE

FROM ${BASE_IMAGE}

# Install the Chocolatey package manager.
RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install essential and convenience programs.
# TODO: Verify that the right `curl` program has priority within the program search path.
RUN choco install --yes git curl wget

# Make `bash` (from Git Bash, MINGW64) available on the program search path.
RUN powershell ([Environment]::SetEnvironmentVariable('Path', $env:Path + ';' + $($env:SystemDrive) + '\Program Files\Git\bin', 'Machine'))

# Display the program search path.
RUN powershell echo \"(Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path).Path\"
