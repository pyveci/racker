# -*- coding: utf-8 -*-
# (c) 2022 Andreas Motl <andreas.motl@cicerops.de>


class OsReleaseFileMissing(Exception):
    pass


class ProvisioningError(Exception):
    pass


class InvalidImageReference(Exception):
    pass


class InvalidPhysicalImage(Exception):
    pass
