###############
Troubleshooting
###############


Running ``systemd-nspawn --oci-bundle=`` directly did not work well. An easy
workaround is to just use ``--directory=oci-bundle/rootfs`` instead.

::

    cd bullseye-oci-bundle/
    systemd-nspawn --oci-bundle=.
    systemd-nspawn --oci-bundle=. --private-users=pick

    cd bundle
    runc run test

    apt update

    E: setgroups 65534 failed - setgroups (1: Operation not permitted)
    E: setegid 65534 failed - setegid (1: Operation not permitted)

See also:

- https://github.com/opencontainers/runc/issues/1860
- https://github.com/opencontainers/runc/issues/2517#issuecomment-720897616
