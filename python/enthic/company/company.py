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

from enthic.score.classification import DistributionClassification
from enthic.utils.ok_json_response import OKJSONResponse
from enthic.ontology import ONTOLOGY
from enthic.ape import ape_code


class Company(OKJSONResponse):
    """
    Company class inherit from OKJSONResponse.
    """

    def __init__(self, sql_results, avg_dir):
        """
        Constructor of the Company class. Attribute defined based on SQL results.

           :param sql_results: Result from a previously executed request.
           :param avg_dir: Average redistribution.
        """
        try:
            ####################################################################
            # IDENTIFICATION RELATED DATA
            self.siren = {"value": sql_results[0][0], "description": "SIREN"}
            self.denomination = {"value": sql_results[0][1], "description": "Dénomination"}
            try:
                self.ape = {"value": "{}, {}".format(sql_results[0][2], ape_code[sql_results[0][2]]),
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
            for line in sql_results:
                try:
                    _value = round(line[8], 2)
                    for accounting in ONTOLOGY["accounting"].keys():
                        try:
                            _description = ONTOLOGY["accounting"][accounting][
                                "code"][line[7].lower()]
                        except KeyError:
                            pass
                    setattr(self, line[7].lower(), {"value": _value, "description": _description})
                except TypeError:  # IN CASE OF NO BUNDLE
                    continue

            ####################################################################
            # SCORE RELATED CALCULATION
            if hasattr(self, "dir") and avg_dir is not None:
                if self.dir["value"] > avg_dir - avg_dir * 0.1:
                    _distribution = DistributionClassification.TIGHT
                elif avg_dir - avg_dir * 0.1 <= self.dir["value"] <= avg_dir + avg_dir * 0.1:
                    _distribution = DistributionClassification.AVERAGE
                elif avg_dir + avg_dir * 0.1 > self.dir["value"]:
                    _distribution = DistributionClassification.GOOD
            else:
                _distribution = DistributionClassification.UNKNOWN
            self.distribution = {"value": _distribution.value,
                                 "description": ONTOLOGY["scoring"]["distribution"]["description"]}
        except IndexError:
            pass
        OKJSONResponse.__init__(self, self.__dict__)
