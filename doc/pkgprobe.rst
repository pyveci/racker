#########################
postroj pkgprobe proposal
#########################

.. note::

    This is still a work in progress.


********
Synopsis
********
::

    postroj pkgprobe \
        --image=<image-label> \
        --package=<package-path-or-url> \
        --check-unit=<systemd-unit-name> \
        --check-network=tcp://<host>:<port>


********
Examples
********
::

    postroj pkgprobe \
        --image=debian-bullseye \
        --package=https://dl.grafana.com/oss/release/grafana_8.5.1_amd64.deb \
        --check-unit=grafana-server \
        --check-network=http://localhost:3000

    postroj pkgprobe \
        --image=centos-8 \
        --package=https://dl.grafana.com/oss/release/grafana-8.5.1-1.x86_64.rpm \
        --check-unit=grafana-server \
        --check-network=http://localhost:3000


*****
Notes
*****


Install package
===============
::

    machinectl shell foobar
    wget https://dl.grafana.com/oss/release/grafana_8.5.1_amd64.deb
    dpkg -i grafana_8.5.1_amd64.deb
    systemctl enable grafana-server
    systemctl start grafana-server


Probe service
=============
::

    machinectl shell foobar /bin/systemctl is-active grafana-server | grep -v inactive
    machinectl shell foobar /usr/bin/curl localhost:3000

Alternatively, use ``systemd-run``, like::

    systemd-run --machine=focal-server-cloudimg-amd64-root --pty --wait /bin/systemctl is-active grafana-server
    systemd-run --machine=focal-server-cloudimg-amd64-root --pty --wait /usr/bin/curl localhost:3000

    systemd-run --machine=focal-server-cloudimg-amd64-root --quiet --wait --pipe /bin/systemctl is-active grafana-server

Alternatively, run it on the host, like::

    systemctl --machine foobar is-active grafana-server


Code sketch
===========
::

    def probe_setup():
        """
        Commands to setup the probe.
        """
        run("/usr/bin/wget https://dl.grafana.com/oss/release/grafana_8.5.1_amd64.deb")
        run("/usr/bin/dpkg -i grafana_8.5.1_amd64.deb")
        run("/bin/systemctl enable grafana-server")
        run("/bin/systemctl start grafana-server")


    def probe_run():
        """
        Commands to run the probe.
        """
        run("/bin/systemctl is-active grafana-server")
        # TODO: Improve waiting until port is reachable.
        time.sleep(3)
        run("/usr/bin/curl localhost:3000")

