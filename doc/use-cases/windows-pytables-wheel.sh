#!/bin/bash
#
# Build wheels for PyTables on Windows. DIY, without a hosted CI provider.
# https://github.com/cicerops/racker/blob/main/doc/use-cases/python-on-windows.rst
#
# Synopsis::
#
#   racker --verbose run -it --rm --platform=windows/amd64 python:3.9 -- bash
#   /c/racker/doc/use-cases/windows-pytables-wheel.sh
#
set -e

# Install prerequisites.

# Miniconda - A minimal installer for Anaconda.
# https://conda.io/miniconda.html
scoop bucket add extras
scoop install miniconda3
#export PATH="$PATH:/c/Users/ContainerAdministrator/scoop/apps/miniconda3/current/condabin"
#alias conda=conda.bat
#/c/Users/ContainerAdministrator/scoop/apps/miniconda3/current/condabin/conda.bat init bash
source /c/Users/ContainerAdministrator/scoop/apps/miniconda3/current/Scripts/activate
conda --version

# /c/Users/ContainerAdministrator/scoop/apps/miniconda3/4.12.0/Scripts/conda.exe

# TODO: `/AddToPath:1` seems to not work, so adjust `$PATH` manually.
#export PATH="$PATH:/c/Tools/miniconda3/condabin"

# TODO: At least within Bash, just addressing `conda` does not work.
#export conda="conda.bat"


# Check prerequisites.
#echo $PATH
#$conda --version
# cibuildwheel --version

# Pretend to be on a build matrix.
export MATRIX_ARCH=win_amd64      # win32
export MATRIX_ARCH_SUBDIR=win-64  # win-32

# Activate and prepare Anaconda environment for building.
conda create --yes --name=build
conda activate build
conda config --env --set subdir ${MATRIX_ARCH_SUBDIR}

# Install needed libraries.
conda install --yes blosc bzip2 hdf5 lz4 lzo snappy zstd zlib

# Install cibuildwheel.
# Build Python wheels for all the platforms on CI with minimal configuration.
# https://cibuildwheel.readthedocs.io/
pip install --upgrade cibuildwheel

# Configure cibuildwheel.
#export CIBW_BUILD="cp36-${MATRIX_ARCH} cp37-${MATRIX_ARCH} cp38-${MATRIX_ARCH} cp39-${MATRIX_ARCH} cp310-${MATRIX_ARCH}"
export CIBW_BUILD="cp39-${MATRIX_ARCH}"
#export CIBW_BEFORE_ALL_WINDOWS="conda create --yes --name=build && conda activate build && conda config --env --set subdir ${MATRIX_ARCH_SUBDIR} && conda install --yes blosc bzip2 hdf5 lz4 lzo snappy zstd zlib"
#export CIBW_ENVIRONMENT_WINDOWS='CONDA_PREFIX="C:\\Miniconda\\envs\\build" PATH="$PATH;C:\\Miniconda\\envs\\build\\Library\\bin"'
export CIBW_ENVIRONMENT="PYTABLES_NO_EMBEDDED_LIBS=true DISABLE_AVX2=true"
export CIBW_BEFORE_BUILD="echo $PATH; pip install -r requirements.txt cython>=0.29.21 delvewheel"
export CIBW_REPAIR_WHEEL_COMMAND_WINDOWS="delvewheel repair -w {dest_dir} {wheel}"

# Debugging.
# env

# Acquire sources.
mkdir -p /c/src
cd /c/src
test ! -d PyTables && git clone https://github.com/PyTables/PyTables --recursive --depth=1
cd PyTables

# Build wheel.
cibuildwheel --platform=windows --output-dir=wheelhouse
