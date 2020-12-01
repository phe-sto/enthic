# -*- coding: utf-8 -*-
"""
===========================================================================
Flask application, compatible with Sphinx documentation and Gunicorn server
===========================================================================

PROGRAM BY PAPIT SASU, 2019

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""

import concurrent.futures
import re
from json import loads, load
from os.path import dirname, join
from math import isnan
from flask import Flask, request
from flask_cors import CORS

from enthic.company.company import CompanyIdentity
from enthic.company.denomination_company import (
    YearDenominationCompany,
    AverageDenominationCompany,
    AllDenominationCompany
)
from enthic.company.siren_company import (
    YearSirenCompany,
    AverageSirenCompany,
    AllSirenCompany
)
from enthic.compute_stats import compute_company_statistics
from enthic.database.fetch import fetchall
from enthic.decorator.insert_request import insert_request
from enthic.ontology import ONTOLOGY, APE_CODE
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse

################################################################################
# FLASK INITIALISATION
application = Flask(__name__)
CORS(application, expose_headers='Authorization', max_age=600, methods=["POST", "GET"])

################################################################################
# CONFIGURE APPLICATION
with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
    config = load(json_configuration_file)
application._static_folder = "./static/"
application.config['MYSQL_HOST'] = config["mySQL"]["enthic"]["host"]
application.config['MYSQL_USER'] = config["mySQL"]["enthic"]["user"]
application.config['MYSQL_PASSWORD'] = config["mySQL"]["enthic"]["password"]
application.config['CACHE_TYPE'] = 'simple'
application.config['MYSQL_DB'] = 'enthic'


@application.route("/company/siren/<int:siren>/<string:year>", methods=['GET'],
                   strict_slashes=False)
@insert_request
def company_siren_year(siren, year):
    """
    Retrieve company information by SIREN for a given year. Path is
    /company/siren/<int:siren> GET method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.

       :param year: Year of results to return, default is None.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN or YEAR wrongly formatted.
    """
    return YearSirenCompany(siren, year)


@application.route("/company/siren/<int:siren>/average", methods=['GET'], strict_slashes=False)
@insert_request
def company_siren_average(siren):
    """
    Retrieve company information by SIREN, calculation of the years average.
    Path is /company/siren/<int:siren> GET method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    return AverageSirenCompany(siren)


@application.route("/company/siren/<int:siren>", methods=['GET'], strict_slashes=False)
@insert_request
def company_siren(siren):
    """
    Retrieve company information by SIREN, calculation of all years. Path is
    /company/siren/<int:siren> GET method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    return AllSirenCompany(siren)


@application.route("/company/denomination/<string:denomination>/average", methods=['GET'],
                   strict_slashes=False)
@insert_request
def company_denomination_average(denomination):
    """
    Retrieve company information by company denomination of the years average.
    Path is /company/denomination/<string:denomination> GET method only and no strict
    slash.

       :param denomination: String, denomination of the company.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return AverageDenominationCompany(denomination)


@application.route("/company/denomination/<string:denomination>", methods=['GET'],
                   strict_slashes=False)
@insert_request
def company_denomination(denomination):
    """
    Retrieve company information by company denomination, calculation of all
    years. Path is /company/denomination/<string:denomination> GET method only and no strict slash.

       :param denomination: String, denomination of the company.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return AllDenominationCompany(denomination)


@application.route("/company/denomination/<string:denomination>/<string:year>", methods=['GET'],
                   strict_slashes=False)
@insert_request
def company_denomination_year(denomination, year):
    """
    Retrieve company information for a given year by company denomination. Path
    is /company/denomination/<string:denomination> GET method only and no strict slash.

       :param denomination: String, denomination of the company.
       :param year: Year of results to return, default is None.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return YearDenominationCompany(denomination, year)


@application.route("/company/ontology", methods=['GET'], strict_slashes=False)
@insert_request
def ontology():
    """
    Return the ontology used to extract accountability data.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(ONTOLOGY)


@application.route("/company/ape", methods=['GET'], strict_slashes=False)
@insert_request
def ape():
    """
    Return all known APE codes.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(APE_CODE)


def pre_cast_integer(probe):
    """
    A str that cannot be casted as integer is set to 0 in MySQL. This Function
    return None (NULL SQL equivalent) if not castable.

       :param probe: SQL probe to cast or not.
    """
    return str(probe) if probe.__class__ is int else probe if probe.isnumeric() is True else None


def get_corresponding_ape_codes(ape_code):
    """
    APE codes are not saved in the original format.
    This function returns codes that are in the database
    and corresponds to the given APE code or it's sub-categories
    It returns None if the given APE code does not exist

        :param ape_code : the list of APE for the filter, comma separated

        :return: list of corresponding APE_CODE in database
    """
    result = list()
    for one_code in ape_code.split(","):
        for i in APE_CODE:
            if re.match(one_code, APE_CODE[i][0]):
                result.append(i)
    if not result:
        return None
    return result


def result_array(probe, limit, ape_code=[], offset=0):
    """
    List the result of the search in the database.

       :param probe: A string to match.
       :param limit: Integer, the limit of result to return.
       :param ape_code: List of APE codes to match or None
       :param offset: Integer, offset of the select SQL request.
    """
    sql_query_select_part = "SELECT siren, denomination, ape, postal_code, town FROM identity"
    sql_query_count = "SELECT  COUNT(*) FROM identity"

    sql_query_probe_condition = '1'
    if probe:
        sql_query_probe_condition = "denomination LIKE {} OR MATCH(denomination) AGAINST ({} IN NATURAL LANGUAGE MODE)".format(
                                    "'{0}%'".format(probe),
                                    "'{0}%'".format(probe))
        # If probe is an interger, it might be a siren number, so we add this condition to the query
        if pre_cast_integer(probe):
            sql_query_probe_condition = "siren = {} OR ".format(pre_cast_integer(probe)) + sql_query_probe_condition

    sql_query_ape_code_condition = "1"
    if len(ape_code) > 1:
        sql_query_ape_code_condition = "ape IN {}".format(tuple(ape_code))
    elif len(ape_code) == 1:
        sql_query_ape_code_condition = "ape = {}".format(ape_code[0])

    sql_query_condition = " WHERE (" + sql_query_probe_condition + ") AND (" + sql_query_ape_code_condition + ") "
    sql_query_limit_and_offset = " LIMIT {} OFFSET {};".format(limit, offset)

    with application.app_context():
        count = fetchall(sql_query_count + sql_query_condition)
        companies = fetchall(sql_query_select_part + sql_query_condition + sql_query_limit_and_offset)
        return count[0][0], tuple(CompanyIdentity(*company).__dict__ for company in companies)

def get_siren(first_letters):
    """
    Get siren of companies whose denomination starts with the given first letters
    """
    first_letters += '%'
    with application.app_context():
        siren_list = fetchall("""SELECT siren
                        FROM identity
                        WHERE denomination LIKE %s LIMIT 1000000""", (first_letters,))

    return siren_list

@application.route("/company/search", methods=['POST'], strict_slashes=False)
@insert_request
def search():
    """
    Search companies by SIREN or denomination. Limited to 1000 results. Path is
    /company/search POST method only and no strict slash. A JSON Body is to
    be post with the keys probe and limit. Key probe is the string to search,
    limit is an integer, the maximum number of results to return.

       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    json_data = loads(request.data)
    if json_data.__class__ is not dict:
        return ErrorJSONResponse("Request body should be a JSON.")
    try:
        ########################################################################
        # WRONG TYPE
        if json_data["limit"].__class__ is not int and \
                (json_data["probe"].__class__ is not str and json_data[
                    "probe"].__class__ is not int):
            return ErrorJSONResponse(
                "Value limit must be a string or integer and limit an integer."
            )
        elif json_data["limit"].__class__ is not int:
            return ErrorJSONResponse("Value limit must be an integer.")
        elif json_data["probe"].__class__ is not str and json_data["probe"].__class__ is not int:
            return ErrorJSONResponse("Value probe must be a string or integer.")
        ########################################################################
        # WRONG LIMIT
        elif json_data["limit"] > 10000:
            return ErrorJSONResponse("Value limit is 10000 maximum.")
        ########################################################################
        # CORRECT JSON
        else:
            count, results = result_array(json_data["probe"], json_data["limit"])
            return OKJSONResponse({
                "@context": "http://www.w3.org/ns/hydra/context.jsonld",
                "@id": request.url,
                "@type": "Collection",
                "totalItems": count,
                "member":
                    results
            })
    ############################################################################
    # WRONG JSON KEY
    except KeyError as error:
        return ErrorJSONResponse(
            "Unhandled JSON key resulting the following error: {}".format(
                str(error)
            )
        )


@application.route("/company/search/page", methods=['GET'], strict_slashes=False)
@insert_request
def page_search():
    """
    Return a JSON formatted as page. Try to implement the Hydra
    hypermedia-driven Web APIs https://www.markus-lanthaler.com/hydra/.
    """

    page = int(request.args.get('page', '1')) - 1  #  TO COUNT
    if page < 0:
        return ErrorJSONResponse('page parameter should be > 0')
    per_page = int(request.args.get('per_page', '30'))
    if per_page < 1:
        return ErrorJSONResponse('per_page parameter should be > 0')
    probe = request.args.get('probe', "")

    # Check consistency of 'ape' argument, and convert it to corresponding database ape codes
    requested_ape_codes = request.args.get('ape', "")
    ape_code = list()
    ape_arg_for_url = ''
    if requested_ape_codes:
        ape_code = get_corresponding_ape_codes(requested_ape_codes)
        if not ape_code:
            return ErrorJSONResponse("ape parameter's value doesn't correspond to any known APE code")
        ape_arg_for_url = "&ape={}".format(requested_ape_codes)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = executor.submit(result_array, probe, per_page, ape_code,
                                      offset=page * per_page)
        count, results = future_list.result()

    if count < page * per_page:
        return ErrorJSONResponse("Page number {} exceed number of page given result per page is {} and result count is {}".format(page + 1, per_page, count))

    last_page = (count / per_page) + 1
    ############################################################################
    # OBJECT STORING RESPONSE
    obj = {"@context": "http://www.w3.org/ns/hydra/context.jsonld",
           "@id": request.url,
           "@type": "Collection",
           "totalItems": count, "view": {
               "@id": request.full_path,
               "@type": "PartialCollectionView",
               "first": '%s?page=1&per_page=%d&probe=%s%s' % (request.path,
                                                              per_page,
                                                              probe,
                                                              ape_arg_for_url),
               "last": '%s?page=%d&per_page=%d&probe=%s%s' % (request.path,
                                                              last_page,
                                                              per_page,
                                                              probe,
                                                              ape_arg_for_url)},
           "member": results
           }
    ############################################################################
    # OBJECT VIEW
    if page == 0:
        obj["view"]['previous'] = ''
    else:
        obj["view"]['previous'] = '%s?page=%d&per_page=%d&probe=%s%s' % (request.path,
                                                                         page,
                                                                         per_page,
                                                                         probe,
                                                                         ape_arg_for_url)
    # MAKE NEXT URL
    if page * per_page + per_page > count:
        obj["view"]["next"] = ''
    else:
        obj["view"]["next"] = '%s?page=%d&per_page=%d&probe=%s%s' % (request.path,
                                                                     page + 2,
                                                                     per_page,
                                                                     probe,
                                                                     ape_arg_for_url)

    return OKJSONResponse(obj)

@application.route("/compute/<string:first_letters>", methods=['GET'], strict_slashes=False)
@insert_request
def compute(first_letters):
    """
    Computes scores and saves them into the database.

       :return: HTTP Response as application/json
    """
    result_list = []
    result = []
    for siren in get_siren(first_letters):
        company_data = company_siren(siren[0])
        scores = compute_company_statistics(company_data)
        result_list.append({"siren" : siren[0], "scores" : scores})
        for score in scores:
            if not isnan(score["share_score"]):
                result.append((siren[0], score["year"], 1, score["share_score"]))
            if not isnan(score["salary_level"]):
                result.append((siren[0], score["year"], 3, score["salary_level"]))
            if not isnan(score["salary_percent"]):
                result.append((siren[0], score["year"], 2, score["salary_percent"]))

    with application.app_context():
        from enthic.database.mysql import mysql
        cur = mysql.connection.cursor()
        sql_replace_query = "REPLACE INTO `annual_statistics`(`siren`, `declaration`, `stats_type`, `value`) VALUES (%s, %s, %s, %s)"
        values = tuple(result)
        cur.executemany(sql_replace_query, values)
        mysql.connection.commit()
        cur.close()
    return OKJSONResponse(result)

@application.route('/<path:path>', strict_slashes=False)
@insert_request
def static_proxy(path):
    """
    Serve the static files, like the Swagger definition page and the 404.

       :param path: / Base path of the host.
       :return: The resource present at the path.
    """
    return application.send_static_file(path)


@application.route("/", strict_slashes=False)
@insert_request
def index():
    """
    Serve the index.html at the base path.

       :return: The static index.html and a return code 200.
    """
    return application.send_static_file("index.html"), 200


@application.errorhandler(404)
@insert_request
def page_not_found(error):
    """
    Page not found and logging.

       :param error: Error message to be logged.
       :return: The HTML 404 page.
    """
    application.logger.info(error)
    return application.send_static_file('404.html'), 404


@application.errorhandler(500)
@insert_request
def server_error(error):
    """
    Server error page and logging.

       :param error: Error message to be logged.
       :return: The HTML 500 page.
    """
    application.logger.error(error)
    return application.send_static_file('500.html'), 500


def main():
    """
    Start app, after configuration.
    """
    ############################################################################
    # START APPLICATION
    application.run(debug=config["flask"]["debug"],
                    host=config["flask"]["host"],
                    port=config["flask"]["port"])


if __name__ == "__main__":
    """
    Only executed as script not at import.
    """
    main()
