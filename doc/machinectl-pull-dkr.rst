###################
machinectl pull-dkr
###################


*******
History
*******

`machinectl`_ already had a ``pull-dkr`` subcommand in the past.

    Unlike Docker, ``systemd-nspawn`` does not have a special image repository,
    but images can be created and uploaded using any third-party program. tar,
    raw, qcow2, and dkr (the Docker image format; this isn’t written anywhere
    in the ``systemd-nspawn`` documentation and its author made quite an effort
    to avoid using the word Docker) image formats are supported. Images are
    managed based on the btrfs file system.

    -- `Systemd and Containers\: An Introduction to systemd-nspawn`_

However, corresponding support has been removed in 2015 already.

    **importd: drop dkr support**

    The current code is not compatible with current dkr protocols anyway,
    and dkr has a different focus ("microservices") than nspawn anyway
    ("whole machine containers"), hence drop support for it, we cannot
    reasonably keep this up to date, and it creates the impression we'd
    actually care for the microservices usecase.

    -- `importd\: drop dkr support #2133`_

See also `machinectl pull-dkr doesn't work with un-namespaced images #47`_.

The corresponding command syntax to pull an image from a Docker image registry was::

    machinectl pull-dkr --verify=no --dkr-index-url=https://index.docker.io library/redis
    machinectl pull-dkr --verify=no --dkr-index-url=https://registry.hub.docker.com lkundrak/network-manager


.. _importd\: drop dkr support #2133: https://github.com/systemd/systemd/pull/2133
.. _machinectl: https://www.freedesktop.org/software/systemd/man/machinectl.html
.. _machinectl pull-dkr doesn't work with un-namespaced images #47: https://github.com/systemd/systemd/issues/47
.. _Systemd and Containers\: An Introduction to systemd-nspawn: https://blog.selectel.com/systemd-containers-introduction-systemd-nspawn/
