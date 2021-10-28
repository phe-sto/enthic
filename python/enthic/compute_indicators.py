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


def compute_companies_statistics(host, year, limit, offset):
    """
    Compute indicators for each companies

        :param host: API address IP + port
    """
    indicators_count = 0
    for i in range(offset, 2000000, limit):
        url = "http://" + host + "/compute/company/all/" + str(i) + "/" + str(limit)
        if year:
            url += "/" + str(year)
        response = get(url)
        assert response.status_code == 200, "Request on url %s returned WRONG HTTP CODE %s INSTEAD OF 200" % (url,response.status_code)
        results = loads(response.text)
        assert results is not None, "NOT RETURNING A JSON"
        if len(results) > 0:
            indicators_count += len(results)
            print("For " + str(i + limit) + " companies for year " + str(year) + ", " + str(indicators_count) + " indicators computed")
        else:
            print("No more company to compute for year " + str(year) + ". " + str(indicators_count) + " indicators computed")
            break


def compute_ape_deciles(host, year):
    """
    Compute percentiles indicators values for each APE and year

        :param host: API address IP + port
    """
    errors = []
    for ape in sorted(CON_APE):
        print("percentiles computed for ", ape)
        url = "http://" + host + "/compute/ape/" + ape
        if year:
            url += "/" + str(year)
        response = get(url)
        if response.status_code != 200:
            errors.append({"code": response.status_code,
                           "ape": ape,
                           "url": url,
                           "response": response.text})

    print(errors)

def main():
    """
    Compute indicators for each company then by APE code
    """

    parser = ArgumentParser(description='Trigger indicators computation into database')
    parser.add_argument('host',
                        help='API address IP + port')
    parser.add_argument('batch_size',
                        metavar='batch size',
                        type=int,
                        help='number of companies to compute per API request')
    parser.add_argument('offset',
                        type=int,
                        help='offset to start computing')
    parser.add_argument('computation_type',
                        choices=['APE', 'company'],
                        help='Compute scores company or APE percentiles')
    parser.add_argument('--year',
                        type=int,
                        help='compute data only for the given year')

    args = parser.parse_args()

    if args.computation_type == 'APE':
        compute_ape_deciles(args.host, args.year)
    elif args.computation_type == 'company':
        compute_companies_statistics(args.host, args.year, args.batch_size, args.offset)

if __name__ == '__main__':
    main()  # ONLY IF EXECUTED NOT WHEN IMPORTED
