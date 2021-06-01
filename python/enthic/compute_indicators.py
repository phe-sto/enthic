# -*- coding: utf-8 -*-
"""
===================================
Python script to compute indicators
===================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from argparse import ArgumentParser
from json import loads
from requests import get

from enthic.utils.conversion import CON_APE
from enthic.ontology import SCORE_DESCRIPTION


def compute_companies_statistics(host, year, limit):
    """
    Compute indicators for each companies

        :param host: API address IP + port
    """
    indicators_count = 0
    for i in range(1600000):
        offset = i * limit
        response = get("http://" + host + "/compute_all/" + str(year) + "/" + str(offset) + "/" + str(limit))
        assert response.status_code == 200, "WRONG HTTP RETURN CODE %s INSTEAD OF 200" % response.status_code
        results = loads(response.text)
        assert results is not None, "NOT RETURNING A JSON"
        indicators_count += len(results)
        print("For " + str(offset + limit) + " companies for year " + str(year) + ", " + str(indicators_count) + " indicators computed")


def compute_ape_deciles(host, year):
    """
    Compute percentiles indicators values for each APE and year

        :param host: API address IP + port
    """
    for ape in CON_APE:
        print("percentiles computed for ", ape)
        for score in SCORE_DESCRIPTION:
            url = "http://" + host + "/compute_ape/" + ape + "/" + str(year) + "/" + str(score)
            response = get(url)
            assert response.status_code == 200 or response.status_code == 400 , "WRONG HTTP RETURN CODE %s INSTEAD OF 200 or 400 on url %s" % (response.status_code, url)
            results = loads(response.text)
            assert results is not None, "NOT RETURNING A JSON"


def main():
    """
    Compute indicators for each company then by APE code
    """

    parser = ArgumentParser(description='Trigger indicators computation into database')
    parser.add_argument('host',
                        metavar='Host',
                        type=ascii,
                        help='API address IP + port')
    parser.add_argument('batch_size',
                        metavar='batch size',
                        type=int,
                        help='API address IP + port')


    args = parser.parse_args()
    host = args.host.replace("'","")
    for year in range(2017, 2022):
        compute_companies_statistics(host, year, args.batch_size)
        compute_ape_deciles(host, year)

if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
