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
from flask import current_app as application
from math import isnan

from enthic.company.company import Bundle
from enthic.database.fetch import fetchall
from enthic.ontology import APE_CODE, SCORE_DESCRIPTION
from enthic.scoring.compute_stats import compute_company_statistics
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

def compute_score(siren, year):
    """
    Compute given company's score for given year and store them into database

        :param siren: siren's company
        :param year : year asked for
    """
    sql_results = fetchall("""
        SELECT accountability, bundle, declaration, amount
        FROM bundle
        WHERE bundle.siren = %s AND declaration = %s;""",
        (siren, year))
    if not sql_results :
        return []
    financial_data = Bundle(*[bundle[:] for bundle in sql_results])
    scores = compute_company_statistics(financial_data.__dict__[str(year)])
    result = []
    for score in scores:
        if not isnan(score["share_score"]):
            result.append((siren, year, 1, score["share_score"]))
        if not isnan(score["salary_level"]):
            result.append((siren, year, 3, score["salary_level"]))
        if not isnan(score["salary_percent"]):
            result.append((siren, year, 2, score["salary_percent"]))

    with application.app_context():
        from enthic.database.mysql import mysql
        cur = mysql.connection.cursor()
        sql_replace_query = "REPLACE INTO `annual_statistics` (`siren`, `declaration`, `stats_type`, `value`) VALUES (%s, %s, %s, %s)"
        values = tuple(result)
        cur.executemany(sql_replace_query, values)
        mysql.connection.commit()
        cur.close()

    return result
