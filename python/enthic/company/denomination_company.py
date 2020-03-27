# -*- coding: utf-8 -*-
"""
=============================================================
Class representing a company, constructed with a Denomination
=============================================================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from enthic.calculation.calculation import BundleCalculation
from enthic.company.company import Company


class DenominationCompany(Company):
    """
    Class DenominationCompany inherit from Company class.
    """

    def __init__(self, mysql, denomination, calculation):
        """
        Constructor of the DenominationCompany class.

           :param mysql: MySQL database to connect.
           :param denomination: The official denomination of the company.
           :param calculation: Type of data to return, average, a year, all.
              Must be BundleCalculation enum.
        """
        if calculation == BundleCalculation.AVERAGE:
            Company.__init__(self, mysql, denomination, calculation, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, devise, bundle, "average", AVG(amount)
            FROM bundle LEFT JOIN identity
            ON bundle.siren = identity.siren
            WHERE identity.denomination = "%s"
            GROUP BY identity.siren, bundle.bundle;""")
        elif calculation == BundleCalculation.ALL:
            Company.__init__(self, mysql, denomination, calculation, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, devise, bundle, declaration, amount
            FROM bundle LEFT JOIN identity
            ON bundle.siren = identity.siren
            WHERE identity.denomination = "%s"
            GROUP BY identity.siren, bundle.bundle, declaration, amount;""")
        else:
            Company.__init__(self, mysql, denomination, calculation, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, devise, bundle, "%s", amount
            FROM bundle LEFT JOIN identity
            ON bundle.siren = identity.siren
            WHERE identity.denomination = "%s"
            AND declaration = %s;""")
