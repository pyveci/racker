######################
Racker vs. other tools
######################


*****
About
*****

This section outlines similarities and differences between Racker and other,
very similar tools, which are also more mature. Mostly, it is about
`Distrobox`_ and `Toolbox`_.


*******
General
*******

See also the `Comparison with similar tools`_ section within the main README.



**************************
Linux distribution support
**************************

The distributions supported on the container side.

- Distrobox: `Distrobox - Containers distribution support`_
- Toolbox: `Toolbox - Linux distribution support`_.


******************
Image provisioning
******************

Distrobox
=========

    `distrobox-init`_ will take care of installing missing dependencies
    (eg. ``sudo``), set up the user and groups, mount directories from
    the host to ensure the tight integration. Note that this HAS to run
    from inside a distrobox, will not work if you run it from your host.

Toolbox
=======

Currently, Toolbox will need prepared images.

- `Toolbox - Use any Linux distro inside`_
- `Toolbox - Consider building and shipping toolbx images using Quay.io`_


Racker
======

Racker will provision operating system images by sourcing them from
OCI-compliant image registries and install missing dependencies on the fly by
invoking `systemd-nspawn`_ without using the ``--boot`` option.


*****
Notes
*****

There is also `Boombox`_, `CoreOS toolbox`_, `docker-coreos-toolbox-ubuntu`_,
`microos-toolbox`_ and `tlbx`_.


.. _Boombox: https://github.com/anthr76/boombox
.. _CoreOS toolbox: https://github.com/coreos/toolbox
.. _Comparison with similar tools: https://github.com/cicerops/racker#comparison-with-similar-tools
.. _Distrobox: https://github.com/89luca89/distrobox
.. _Distrobox - Containers distribution support: https://distrobox.privatedns.org/compatibility.html#containers-distros
.. _distrobox-init: https://distrobox.privatedns.org/usage/distrobox-init.html
.. _docker-coreos-toolbox-ubuntu: https://github.com/wallneradam/docker-coreos-toolbox-ubuntu
.. _microos-toolbox: https://github.com/openSUSE/microos-toolbox
.. _systemd-nspawn: https://www.freedesktop.org/software/systemd/man/systemd-nspawn.html
.. _tlbx: https://gitlab.com/uppercat/tlbx
.. _Toolbox: https://containertoolbx.org/
.. _Toolbox - Consider building and shipping toolbx images using Quay.io: https://github.com/containers/toolbox/issues/1019
.. _Toolbox - Linux distribution support: https://containertoolbx.org/distros/
.. _Toolbox - Use any Linux distro inside: https://github.com/containers/toolbox/issues/789
