# Windows runner Dockerfile for Racker
# https://github.com/cicerops/racker
#
# Provision a Windows operating system image.
#
# - Install the Scoop package manager.
# - Install additional software using Scoop.
# - https://scoop.sh/
#

ARG BASE_IMAGE

FROM ${BASE_IMAGE}

# Restore the default Windows shell for correct batch processing.
SHELL ["cmd", "/S", "/C"]

# Install the Scoop package manager.
# https://github.com/ScoopInstaller/Install#for-admin
RUN powershell -Command irm get.scoop.sh -outfile 'scoop-install.ps1'; .\scoop-install.ps1 -RunAsAdmin

# Install/update Aria2 and Git first, to speed up downloads and have it up-to-date.
RUN scoop install aria2 git

# Install essential and convenience programs.
RUN scoop install msys2 zip unzip

# Make MSYS2 programs available on the program search path.
# Note: It is not fully installed. In order to complete it, run `msys2` once.
RUN powershell $msys_path = $(scoop prefix msys2); [Environment]::SetEnvironmentVariable('Path', $env:Path + ';' + $msys_path + '\usr\bin', 'Machine')

# Display the program search path.
#RUN powershell echo (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment' -Name Path).Path

# Rename Windows-native programs in favor of Scoop-installed/FOSS/GNU ones.
# An alternative would be to manipulate `$PATH`, but that is more tedious.
RUN sh -c 'test -f /c/Windows/system32/curl && mv /c/Windows/system32/curl /c/Windows/system32/curl-win'
RUN sh -c 'test -f /c/Windows/system32/convert && mv /c/Windows/system32/convert /c/Windows/system32/convert-ntfs'

# TODO: With PowerShell 7, it is possible to remove the corresponding aliases.
#Remove-Alias -Name ls
#Remove-Alias -Name cat
#Remove-Alias -Name mv
#Remove-Alias -Name ps
#Remove-Alias -Name pwd
#Remove-Alias -Name rm
