# -*- coding: utf-8 -*-
"""
====================================================================
====================================================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from copy import deepcopy

from enthic.database.fetch import fetchall
from enthic.ontology import APE_CODE, SCORE_DESCRIPTION
from enthic.utils.conversion import CON_APE


def get_percentiles(real_ape, year=None, score=None):
    """
    Return stored statistics about the given APE code as json

        :param real_ape: official APE code asked for
        :param year : year asked for
        :param score : score type asked for
    """
    sql_args = {"ape": CON_APE[real_ape],
                "year" : year,
                "score" : score}
    sql_request = "SELECT declaration, stats_type, percentile, value, count FROM `annual_ape_statistics` WHERE ape = %(ape)s"
    if year :
        sql_request = sql_request + " AND declaration = %(year)s"
    if score :
        sql_request = sql_request + " AND stats_type = %(score)s;"

    sql_result = fetchall(sql_request, sql_args)

    if not sql_result:
        return None

    year_data = {}
    if not score :
        for key in SCORE_DESCRIPTION :
            year_data[key] = {
            "description" : SCORE_DESCRIPTION[key],
            "total_count" : 0,
            "percentiles" : {}
            }
    else :
        year_data[score] = {
        "description" : SCORE_DESCRIPTION[score],
        "total_count" : 0,
        "percentiles" : {}
        }

    statistics = {}
    if year :
        statistics[year] = year_data
    else:
        for fictitious_year in range(1990, 2100):
            statistics[fictitious_year] = deepcopy(year_data)

    for row in sql_result :
        statistics[row[0]][row[1]]["percentiles"][row[2]] = row[3]
        statistics[row[0]][row[1]]["total_count"] = row[4]

    years_to_delete = []
    for k_year in statistics :
        has_data = False
        score_to_delete = []
        for k_score in SCORE_DESCRIPTION :
            if statistics[k_year][k_score]["total_count"] > 0:
                has_data = True
            else:
                score_to_delete.append(k_score)
        if not has_data:
            years_to_delete.append(k_year)
        else:
            for key in score_to_delete:
                del statistics[k_year][key]

    for key in years_to_delete:
        del statistics[key]

    result = {
        "ape" : { "value" : APE_CODE[CON_APE[real_ape]][1],
                  "description": "Code Activité Principale Exercée (NAF)",
                  "code" : real_ape},
        "statistics" : statistics
    }
    return result
