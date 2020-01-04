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
            self.siren = sql_results[0][0]
            self.denomination = sql_results[0][1]
            self.accountability = sql_results[0][2]
            self.devise = sql_results[0][3]
            ####################################################################
            # BUNDLE RELATED DATA, THEREFORE DYNAMIC
            for line in sql_results:
                setattr(self, line[4], round(line[5], 2))
            ####################################################################
            # SCORE RELATED CALCULATION
            if hasattr(self, "DIR") and avg_dir is not None:
                if self.DIR > avg_dir - avg_dir * 0.1:
                    self.distribution = DistributionClassification.TIGHT.value
                elif avg_dir - avg_dir * 0.1 <= self.DIR <= avg_dir + avg_dir * 0.1:
                    self.distribution = DistributionClassification.AVERAGE.value
                elif avg_dir + avg_dir * 0.1 > self.DIR:
                    self.distribution = DistributionClassification.GOOD.value
            else:
                self.distribution = DistributionClassification.UNKNOWN.value
        except IndexError:
            pass
        OKJSONResponse.__init__(self, self.__dict__)
