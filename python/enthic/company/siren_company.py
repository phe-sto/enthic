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

from enthic.company.company import Company


class SirenCompany(Company):
    """
    Class SirenCompany inherit from Company class.
    """

    def __init__(self, mysql, siren, year, *args):
        """
        Constructor of the DenominationCompany class.

           :param mysql: MySQL database to connect.
           :param siren: The SIREN of the company.
           :param year: Kwarg, default is None, otherwise an integer of the year
              to retrieve.
           :param *args: Average distribution ratio.
        """
        cur = mysql.connection.cursor()
        if year is None:
            avg_dir = args[0]
            cur.execute("""SELECT identity.siren, denomination, ape,
            postal_code, town, accountability, devise, bundle, SUM(amount)
            FROM identity LEFT OUTER JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.siren = '%s'
            GROUP BY bundle.bundle;""" % (siren))
        else:
            try:
                avg_dir = args[0][int(year)]
            except KeyError:
                avg_dir = None
            cur.execute("""SELECT identity.siren, denomination, ape,
            postal_code, town, accountability, devise, bundle, amount
            FROM identity LEFT OUTER JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.siren = '%s'
            AND declaration = %s;""" % (siren, year))
        sql_results = cur.fetchall()
        cur.close()
        Company.__init__(self, sql_results, avg_dir)
