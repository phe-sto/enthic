# -*- coding: utf-8 -*-
"""
============================
Class representing a company
============================

PROGRAM BY PAPIT SASU, 2020

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

from re import compile

from enthic.ape import ape_code
from enthic.calculation.calculation import BundleCalculation
from enthic.ontology import ONTOLOGY
from enthic.result.result import result
from enthic.score.classification import DistributionClassification
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from flask import abort

year_re = compile(r"^\d{4}$")  # REGEX OF A YEAR


class Company(OKJSONResponse):
    """
    Company class inherit from OKJSONResponse.
    """

    def __init__(self, mysql, probe, calculation, sql_request):
        """
        Constructor of the Company class. Attribute defined based on SQL results.

           :param mysql: MySQL database client.
           :param probe: Either a Siren or a denomination to get in base.
           :param calculation: Type of data to return, average, a year, all.
              Must be BundleCalculation enum.
           :param sql_request: Corresponding request to execute.
        """
        ########################################################################
        # EXECUTE SQL REQUEST
        cur = mysql.connection.cursor()
        if calculation == BundleCalculation.AVERAGE or calculation == BundleCalculation.ALL:
            avg_dir = result.avg_dir
            cur.execute(sql_request % (probe))
        else:
            if year_re.match(calculation):  # CHECK YEAR FORMAT

                try:
                    avg_dir = result.yearly_avg_dir[int(calculation)]
                except KeyError:
                    avg_dir = None
                cur.execute(sql_request % (calculation, probe, calculation))
            else:
                abort(ErrorJSONResponse("Year format is not ^\d{4}$"))

        sql_results = cur.fetchall()
        cur.close()
        try:
            ####################################################################
            # IDENTIFICATION RELATED DATA
            self.siren = {"value": sql_results[0][0], "description": "SIREN"}
            self.denomination = {"value": sql_results[0][1], "description": "Dénomination"}
            try:
                self.ape = {
                    "value": "{}, {}".format(sql_results[0][2], ape_code[sql_results[0][2]]),
                    "description": "Code Activité Principale Exercée (NAF)"}
            except KeyError:
                self.ape = {"value": "{}, Code APE inconnu".format(sql_results[0][2]),
                            "description": "Code Activité Principale Exercée (NAF)"}
            self.postal_code = {"value": sql_results[0][3], "description": "Code Postal"}
            self.town = {"value": sql_results[0][4], "description": "Commune"}
            self.accountability = {"value": "{}, {}".format(sql_results[0][5],
                                                            ONTOLOGY["accounting"][
                                                                sql_results[0][5]]["description"]),
                                   "description": "Type de comptabilité"}
            self.devise = {"value": sql_results[0][6], "description": "Devise"}
            ####################################################################
            # BUNDLE RELATED DATA, THEREFORE DYNAMIC
            bundles = {}
            declaration = None
            for line in sql_results:

                bundle = str(line[7]).lower()
                if str(line[8]) not in bundles:
                    if bundles.__len__() != 0:
                        setattr(self, declaration, bundles[declaration])
                    declaration = str(line[8])
                    bundles[declaration] = {}
                try:
                    value = round(line[9], 2)
                    for accounting in ONTOLOGY["accounting"].keys():
                        try:
                            bundles[declaration][bundle] = {
                                "value": value,
                                "description":
                                    ONTOLOGY["accounting"][accounting]["code"][
                                        bundle]
                            }
                        except KeyError:
                            pass
                    ############################################################
                    # SCORE RELATED CALCULATION
                    if bundle == "dir" and avg_dir is not None:
                        if value > avg_dir - avg_dir * 0.1:
                            distribution = DistributionClassification.TIGHT
                        elif avg_dir - avg_dir * 0.1 <= value <= avg_dir + avg_dir * 0.1:
                            distribution = DistributionClassification.AVERAGE
                        elif avg_dir + avg_dir * 0.1 > value:
                            distribution = DistributionClassification.GOOD
                        else:
                            distribution = DistributionClassification.UNKNOWN
                        bundles[declaration][bundle] = {
                            "value": distribution.value,
                            "description":
                                ONTOLOGY["scoring"]["distribution"][
                                    "description"]}

                except TypeError:  # IN CASE OF NO BUNDLE
                    continue
            setattr(self, declaration, bundles[declaration])
        except IndexError:
            pass
        OKJSONResponse.__init__(self, self.__dict__)
