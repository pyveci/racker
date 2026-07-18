# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>
import re

import pytest

from postroj.exceptions import OsReleaseFileMissing
from postroj.util import find_rootfs


def test_find_rootfs_unhappy():
    with pytest.raises(OsReleaseFileMissing) as ex:
        find_rootfs("/tmp/foo")
    assert ex.match(re.escape("OS root directory /tmp/foo lacks an operating system (os-release file is missing)."))
