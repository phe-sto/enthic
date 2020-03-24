# -*- coding: utf-8 -*-
"""
======================================================
Class representing a company, constructed with a SIREN
======================================================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from enthic.company.company import (
    YearCompany,
    UniqueBundleCompany,
    MultipleBundleCompany,
    SirenCompany
)


class AllSirenCompany(MultipleBundleCompany, SirenCompany):
    """
    Class SirenCompany and MultipleBundleCompany inherit from Company class as
    it has potentially multiple declarations.
    """

    def __init__(self, siren):
        """
        Constructor of the SirenCompany class.

           :param siren: The official siren of the company.
        """
        SirenCompany.__init__(self, siren)
        MultipleBundleCompany.__init__(self, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, bundle, declaration, amount
            FROM identity LEFT JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.siren = %s
            GROUP BY identity.siren, accountability, bundle.bundle, declaration, amount;""", (self.siren,))


class AverageSirenCompany(UniqueBundleCompany, SirenCompany):
    """
    Class AverageSirenCompany inherit from UniqueBundleCompany class as
    it as a unique average bundle. Inherit also YearCompany to check the year.
    """

    def __init__(self, siren):
        """
        Constructor of the AverageSirenCompany class.

           :param siren: The official siren of the company.
        """
        SirenCompany.__init__(self, siren)
        UniqueBundleCompany.__init__(self, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, bundle, "average", AVG(amount)
            FROM identity LEFT JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.siren = %s
            GROUP BY bundle.bundle, accountability;""", (self.siren,))


class YearSirenCompany(YearCompany, UniqueBundleCompany, SirenCompany):
    """
    Class YearDenominationCompany inherit from UniqueBundleCompany class as
    it as a unique average bundle. Inherit also YearCompany to check the year.
    """

    def __init__(self, siren, year):
        """
        Constructor of the YearDenominationCompany class.

           :param siren: The official siren of the company.
           :param year: The declaration to return, i.e. a year.
        """
        SirenCompany.__init__(self, siren)
        YearCompany.__init__(self, year)
        UniqueBundleCompany.__init__(self, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, bundle, %s, amount
            FROM identity LEFT JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.siren = %s
            AND declaration = %s;""", (self.year, self.siren, self.year))
