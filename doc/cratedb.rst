#########################
Using postroj for CrateDB
#########################

.. note::

    This is still a work in progress.


****************
postroj pkgprobe
****************

Purpose: Test distribution packages.

Test package on Debian bullseye::

    postroj pkgprobe \
        --image=debian-bullseye \
        --package=https://cdn.crate.io/downloads/apt/testing/pool/main/c/crate/crate_4.7.2-1~bullseye_amd64.deb \
        --check-unit=crate \
        --check-network=http://localhost:4200 \
        --check-network=tcp://localhost:5432 \
        --network-timeout=30

Test package on Fedora 36::

    postroj pkgprobe \
        --image=fedora-36 \
        --package=https://cdn.crate.io/downloads/yum/testing/7/x86_64/crate-4.7.2-1.x86_64.rpm \
        --check-unit=crate \
        --check-network=http://localhost:4200 \
        --check-network=tcp://localhost:5432 \
        --network-timeout=30

.. todo::

    Probing the HTTP port 4200 of CrateDB currently still responds with::

        HTTP/1.1 503 Service Unavailable

    Improve!


***********
postroj run
***********

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


***************
Troubleshooting
***************

CrateDB on openSUSE fails
=========================

A: Workaround applied by running ``rpm --install --nodeps``.
TODO: Maybe adjust the RPM dependencies?

::

    zypper --non-interactive install crate-4.7.2-1.x86_64.rpm
    Loading repository data...
    Reading installed packages...
    Resolving package dependencies...

    Problem: nothing provides 'systemd-units' needed by the to be installed crate-4.7.2-1.x86_64
     Solution 1: do not install crate-4.7.2-1.x86_64
     Solution 2: break crate-4.7.2-1.x86_64 by ignoring some of its dependencies

    Choose from above solutions by number or cancel [1/2/c/d/?] (c): c

::

    rpm -i crate-4.7.2-1.x86_64.rpm
    warning: crate-4.7.2-1.x86_64.rpm: Header V4 RSA/SHA1 Signature, key ID 06f6eaeb: NOKEY
    error: Failed dependencies:
        shadow-utils is needed by crate-4.7.2-1.x86_64
        systemd-units is needed by crate-4.7.2-1.x86_64
