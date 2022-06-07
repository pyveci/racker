# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import json
import logging
import re
import sys
from pathlib import Path, PosixPath
from unittest import mock
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from re_assert import Matches

from postroj.cli import cli
from postroj.exceptions import InvalidImageReference, InvalidPhysicalImage, OsReleaseFileMissing, ProvisioningError
from postroj.image import ImageProvider
from postroj.registry import CuratedOperatingSystem
from racker.babelfish import DynamicDistribution
from testing.util import AnyStringWith


if sys.platform != "linux":
    pytest.skip("Skipping Linux-only tests", allow_module_level=True)


def test_list_images():
    runner = CliRunner()

    result = runner.invoke(cli, "list-images", catch_exceptions=False)
    assert result.exit_code == 0

    reference = [
        "debian-stretch",
        "debian-buster",
        "debian-bullseye",
        "debian-bookworm",
        "debian-sid",
        "ubuntu-focal",
        "ubuntu-jammy",
        "fedora-35",
        "fedora-36",
        "fedora-37",
        "rhel-8",
        "rhel-9",
        "opensuse-leap",
        "opensuse-tumbleweed",
        "sles-15",
        "sles-bci",
        "centos-7",
        "centos-8",
        "centos-9",
        "rockylinux-8",
        "amazonlinux-2022",
        "oraclelinux-8",
        "archlinux-20220501",
    ]

    assert json.loads(result.stdout) == reference


def test_image_path():
    ip = ImageProvider(distribution=CuratedOperatingSystem.DEBIAN_SID, autosetup=False)
    assert ip.image == PosixPath("/var/lib/testdrive/postroj/images/debian-sid")


def test_acquire_docker(fakeimage, hcmd_mock):
    fakeimage.acquire_from_docker()
    Matches("skopeo copy .+").assert_matches(hcmd_mock.mock_calls[0].args[0])
    Matches("umoci unpack .+").assert_matches(hcmd_mock.mock_calls[1].args[0])


def test_acquire_invalid_image():
    distribution = DynamicDistribution.empty()
    distribution.image = "foobar"
    ip = ImageProvider(distribution=distribution, autosetup=False)
    with pytest.raises(InvalidImageReference) as ex:
        ip.acquire()
    assert ex.match("Unsupported scheme for image: foobar")


def test_acquire_provisioning_error():
    """
    Simulate a provisioning error.
    """
    distribution = DynamicDistribution.empty()
    distribution.image = "docker://docker.io/debian:stretch-slim"
    ip = ImageProvider(distribution=distribution, autosetup=False)

    def raise_exception(*args, **kwargs):
        raise ProvisioningError("foo")

    with patch("postroj.image.ImageProvider.provision_systemd", raise_exception):
        with pytest.raises(ProvisioningError) as ex:
            ip.acquire()
        assert ex.match("Provisioning filesystem image failed: foo")


@pytest.mark.xfail(reason="Not implemented yet")
def test_acquire_no_operating_system():
    distribution = DynamicDistribution.empty()
    distribution.image = "docker://docker.io/hello-world"
    ip = ImageProvider(distribution=distribution, autosetup=False)
    ip.acquire()


def test_acquire_http_not_found():
    distribution = DynamicDistribution.empty()
    distribution.image = "https://cloud-images.example.org/foobar-minimal-cloudimg-amd64-root.tar.xz"
    ip = ImageProvider(distribution=distribution, autosetup=False)
    with pytest.raises(InvalidImageReference) as ex:
        ip.acquire()
    assert ex.match(f"Unable to download image: {re.escape(distribution.image)}")


def test_discover_not_needed(caplog):
    distribution = CuratedOperatingSystem.FEDORA_37
    ip = ImageProvider(distribution=distribution, autosetup=False)
    caplog.set_level(logging.INFO)
    ip.discover()
    assert "Skipping operating system discovery" in caplog.text


def test_discover_os_release_file_missing():
    ip = ImageProvider(distribution=DynamicDistribution.from_image("foo"), autosetup=False)
    with pytest.raises(OsReleaseFileMissing) as ex:
        ip.discover()
    assert ex.match(
        re.escape(
            "OS root directory /var/lib/testdrive/postroj/archive/docker-foo.img "
            "lacks an operating system (os-release file is missing)."
        )
    )


def test_discover_os_release_file_no_os_root(tmpdir):

    # Create fake OS root directory.x
    fakeroot = Path(tmpdir)
    (fakeroot / "etc").mkdir()
    (fakeroot / "etc" / "os-release").touch()

    ip = ImageProvider(distribution=DynamicDistribution.from_image("foo"), autosetup=False)
    ip.image_staging = fakeroot

    with pytest.raises(OsReleaseFileMissing) as ex:
        ip.discover()

    message_reference = (
        f"Container docker-foo at directory {tmpdir} lacks an operating system (os-release file is missing or "
        f"inaccessible). Error: CalledProcessError. Reason: Command 'systemd-nspawn --directory={tmpdir} "
        f"--bind-ro=/etc/resolv.conf:/etc/resolv.conf --pipe /bin/cat /etc/os-release' returned non-zero "
        f"exit status 1. Reason: Directory {tmpdir} doesn't look like it has an OS tree. Refusing."
    )

    assert ex.match(re.escape(message_reference))


def test_discover_os_release_file_unknown_exception(tmpdir):

    # Create fake OS root directory.x
    fakeroot = Path(tmpdir)
    (fakeroot / "etc").mkdir()
    (fakeroot / "etc" / "os-release").touch()

    ip = ImageProvider(distribution=DynamicDistribution.from_image("foo"), autosetup=False)
    ip.image_staging = fakeroot

    with patch("postroj.image.scmd") as scmd:
        scmd.side_effect = AssertionError("unknown")
        with pytest.raises(OsReleaseFileMissing) as ex:
            ip.discover()

    message_reference = (
        f"Container docker-foo at directory {tmpdir} lacks an operating system (os-release file is missing or "
        f"inaccessible). Error: AssertionError. Reason: unknown"
    )

    assert ex.match(re.escape(message_reference))


def test_provision_systemd_unsupported_operating_system():
    ip = ImageProvider(distribution=DynamicDistribution.from_image("foo"), autosetup=False)
    with pytest.raises(ProvisioningError) as ex:
        ip.provision_systemd()
    assert ex.match(
        re.escape(
            "Unsupported operating system: "
            "DynamicDistribution(family=None, name=None, release=None, version=None, image='docker://foo')"
        )
    )


def test_discover_os_release_file_invalid_command():
    ip = ImageProvider(distribution=DynamicDistribution.from_image("debian:stretch-slim"), autosetup=False)
    with patch("postroj.image.ImageProvider.CAT_COMMAND", "/bin/foo"):
        with pytest.raises(OsReleaseFileMissing) as ex:
            ip.discover()
        message = str(ex.value)
        assert "os-release file is missing or inaccessible" in message
        assert "CalledProcessError" in message
        assert "execv(/bin/foo) failed: No such file or directory" in message


def test_discover_os_release_file_invalid_file():
    ip = ImageProvider(distribution=DynamicDistribution.from_image("debian:stretch-slim"), autosetup=False)
    with patch("postroj.image.ImageProvider.OS_RELEASE_FILE", "/etc/bar"):
        with pytest.raises(OsReleaseFileMissing) as ex:
            ip.discover()
        message = str(ex.value)
        assert "os-release file is missing or inaccessible" in message
        assert "CalledProcessError" in message
        assert "/bin/cat: /etc/bar: No such file or directory" in message


def test_activate_image_not_found_fails():
    ip = ImageProvider(distribution=DynamicDistribution.from_image("foo"), autosetup=False)
    with pytest.raises(FileNotFoundError) as ex:
        ip.activate_image()
    assert ex.match(
        re.escape("[Errno 2] No such file or directory: '/var/lib/testdrive/postroj/archive/docker-foo.img'")
    )


def test_activate_empty_directory_fails(tmpdir):

    # Create fake OS root directory.x
    fakeroot = Path(tmpdir)
    # (fakeroot / "etc").mkdir()
    # (fakeroot / "etc" / "os-release").touch()

    ip = ImageProvider(distribution=DynamicDistribution.from_image("foo"), autosetup=False)
    ip.image_staging = fakeroot

    with pytest.raises(InvalidPhysicalImage) as ex:
        ip.activate_image()

    message_reference = f"Unable to activate image at {tmpdir}"

    assert ex.match(re.escape(message_reference))


def test_setup():
    distribution = DynamicDistribution.from_image("debian:stretch-slim")
    ip = ImageProvider(distribution=distribution, autosetup=False)
    ip.setup()
    assert ip.image.is_symlink()


def test_setup_debian(fakeimage, scmd_first_command):
    fakeimage.setup_debian()
    Matches(".*apt.+install.+systemd.*").assert_matches(scmd_first_command())


def test_setup_ubuntu(fakeimage, scmd_mock, hcmd_mock):
    fakeimage.setup_ubuntu()
    assert scmd_mock.mock_calls == [
        mock.call(directory=mock.ANY, command=AnyStringWith("apt-get install")),
        mock.call(directory=mock.ANY, command=AnyStringWith("systemctl disable")),
        mock.call(directory=mock.ANY, command=AnyStringWith("systemctl mask")),
    ]


def test_setup_redhat(fakeimage, scmd_mock):
    fakeimage.setup_redhat()
    assert scmd_mock.mock_calls == [
        mock.call(directory=mock.ANY, command="command -v dnf"),
        mock.call(directory=mock.ANY, command="dnf install -y --skip-broken systemd curl wget"),
    ]


def test_setup_centos(fakeimage, scmd_first_command, hcmd_mock):
    fakeimage.setup_centos()
    Matches(".*yum.*install.*").assert_matches(scmd_first_command())


def test_setup_suse(fakeimage, scmd_first_command):
    fakeimage.setup_suse()
    Matches(".*zypper.+install.+systemd.*").assert_matches(scmd_first_command())


def test_setup_archlinux(fakeimage, scmd_first_command):
    fakeimage.setup_archlinux()
    Matches(r".*pacman.+\-S.+systemd.*").assert_matches(scmd_first_command())


def test_upgrade_systemd(fakeimage, scmd_mock, hcmd_mock):
    ImageProvider.upgrade_systemd(fakeimage.image_staging)
    Matches("systemd-nspawn --directory=.* --pipe systemctl --version").assert_matches(hcmd_mock.call_args[0][0])
