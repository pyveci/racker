# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
from postroj.registry import CuratedOperatingSystem
from postroj.selftest import HostinfoProbe, get_selftest_distributions, selftest_multiple


def test_get_selftest_distributions(delay):
    result = get_selftest_distributions()
    assert len(result) > 10


def test_selftest_multiple(delay):
    success = selftest_multiple(distributions=[CuratedOperatingSystem.DEBIAN_STRETCH], probes=[HostinfoProbe])
    assert success is True
