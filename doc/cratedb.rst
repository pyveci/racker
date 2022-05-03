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

Test package on CentOS 8::

    postroj pkgprobe \
        --image=centos-8 \
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
