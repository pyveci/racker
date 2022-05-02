#########################
Using postroj for CrateDB
#########################

.. note::

    This is still a work in progress.


****************
postroj pkgprobe
****************

Purpose: Test distribution packages.

::

    postroj pkgprobe --image=debian:bullseye-slim --package=<package-path-or-url> --unit-is-active=crate
    postroj pkgprobe --image=centos:7 --package=<package-path-or-url> --unit-is-active=crate



****************************
postroj run --system=windows
****************************

Purpose: Invoke programs within a Windows/Java/OpenJDK environment.

::

    # Basic usage.
    postroj run \
      --system=windows-1809 --cpus=8 --memory=8192M \
      --mount type=git,src=https://github.com/crate/crate,dst=C:/src \
      -- \
      cmd /C "cd src && gradlew :server:test -Dtests.crate.run-windows-incompatible=false"

    # Advanced usage.
    postroj run \
        --environment=windows-1809 --cpus=8 --memory=8192M \
        --repository=https://github.com/crate/crate \
        --command="gradlew :server:test -Dtests.crate.run-windows-incompatible=false"

