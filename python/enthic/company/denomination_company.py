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

from enthic.company.company import Company


class DenominationCompany(Company):
    """
    Class DenominationCompany inherit from Company class.
    """

    def __init__(self, mysql, denomination, year, *args):
        """
        Constructor of the DenominationCompany class.

           :param mysql: MySQL database to connect.
           :param denomination: The official denomination of the company.
           :param year: Kwarg, default is None, otherwise an integer of the year
              to retrieve.
           :param *args: Average distribution ratio.
        """
        cur = mysql.connection.cursor()
        if year is None:
            avg_dir = args[0]
            cur.execute("""SELECT identity.siren, denomination, ape,
            postal_code, town, accountability, devise, bundle, SUM(amount)
            FROM identity INNER JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.denomination = '%s'
            GROUP BY identity.siren, bundle.bundle;""" % (denomination))
        else:
            try:
                avg_dir = args[0][int(year)]
            except KeyError:
                avg_dir = None
            cur.execute("""SELECT identity.siren, denomination, 
            ape, postal_code, accountability, town, devise, bundle, amount
            FROM identity INNER JOIN bundle
            ON bundle.siren = identity.siren
            WHERE identity.denomination = '%s'
            AND declaration = %s;""" % (denomination, year))
        sql_results = cur.fetchall()
        cur.close()
        Company.__init__(self, sql_results, avg_dir)
