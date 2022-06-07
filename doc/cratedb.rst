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
