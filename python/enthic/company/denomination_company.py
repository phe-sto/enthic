# -*- coding: utf-8 -*-
"""
=============================================================
Class representing a company, constructed with a denomination
=============================================================

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
    DenominationCompany
)


class AllDenominationCompany(MultipleBundleCompany, DenominationCompany):
    """
    Class AllDenominationCompany inherit from MultipleBundleCompany,
    DenominationCompany class as it has multiple bundles.
    """

    def __init__(self, denomination):
        """
        Constructor of the AllDenominationCompany class.

           :param denomination: The official denomination of the company.
        """
        DenominationCompany.__init__(self, denomination)
        MultipleBundleCompany.__init__(self, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, bundle, declaration, amount
            FROM identity LEFT JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.denomination = %s
            GROUP BY identity.siren, accountability, bundle.bundle, declaration, amount;""", (self.denomination,))


class AverageDenominationCompany(UniqueBundleCompany, DenominationCompany):
    """
    Class AverageDenominationCompany inherit from UniqueBundleCompany,
    DenominationCompany class as it as a unique average bundle.
    """

    def __init__(self, denomination):
        """
        Constructor of the AverageDenominationCompany class.

           :param denomination: The official denomination of the company.
        """
        DenominationCompany.__init__(self, denomination)
        UniqueBundleCompany.__init__(self, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, bundle, "average", AVG(amount)
            FROM identity LEFT JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.denomination = %s
            GROUP BY identity.siren, accountability, bundle.bundle;""", (self.denomination,))


class YearDenominationCompany(YearCompany, UniqueBundleCompany, DenominationCompany):
    """
    Class YearDenominationCompany inherit from YearCompany, UniqueBundleCompany,
    DenominationCompany class as it as a unique average bundle. Inherit also
    YearCompany to check the year.
    """

    def __init__(self, denomination, year):
        """
        Constructor of the YearDenominationCompany class.

           :param denomination: The official denomination of the company.
           :param year: The declaration to return, i.e. a year.
        """
        DenominationCompany.__init__(self, denomination)
        YearCompany.__init__(self, year)
        UniqueBundleCompany.__init__(self, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, bundle, %s, amount
            FROM identity LEFT JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.denomination = %s
            AND declaration = %s;""", (self.year, self.denomination, self.year))
