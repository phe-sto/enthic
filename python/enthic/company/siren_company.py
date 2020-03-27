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

from re import compile

from enthic.calculation.calculation import BundleCalculation
from enthic.company.company import Company
from enthic.utils.error_json_response import ErrorJSONResponse
from flask import abort

siren_re = compile(r"^\d{9}$")  # REGEX OF A SIREN


class SirenCompany(Company):
    """
    Class SirenCompany inherit from Company class.
    """

    def __init__(self, mysql, siren, calculation):
        """
        Constructor of the DenominationCompany class.

           :param mysql: MySQL database to connect.
           :param siren: The SIREN of the company.
           :param calculation: Type of data to return, average, a year, all.
              Must be BundleCalculation enum.
        """

        if siren_re.match(siren) is None:  # CHECK SIREN FORMAT
            abort(ErrorJSONResponse("SIREN for is wrong, must match ^\d{9}$."))

        if calculation == BundleCalculation.AVERAGE:
            Company.__init__(self, mysql, siren, calculation, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, devise, bundle, "average", AVG(amount)
            FROM bundle LEFT OUTER JOIN identity
            ON bundle.siren = identity.siren
            WHERE identity.siren = '%s'
            GROUP BY bundle.bundle;""")
        elif calculation == BundleCalculation.ALL:
            Company.__init__(self, mysql, siren, calculation, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, devise, bundle, declaration, amount
            FROM bundle LEFT OUTER JOIN identity
            ON bundle.siren = identity.siren
            WHERE identity.siren = '%s'
            GROUP BY bundle.bundle, declaration, amount;""")
        else:
            Company.__init__(self, mysql, siren, calculation, """
            SELECT identity.siren, denomination, ape, postal_code, town,
                accountability, devise, bundle, "%s", amount
            FROM bundle LEFT OUTER JOIN identity
            ON bundle.siren = identity.siren
            WHERE identity.siren = '%s'
            AND declaration = %s;""")
