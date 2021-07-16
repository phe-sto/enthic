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
import csv
import io
import codecs
from json import loads, load
from os.path import dirname, join
import numpy
from flask import Flask, request, send_file
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
from enthic.database.fetch import fetchall
from enthic.decorator.insert_request import insert_request
from enthic.ontology import ONTOLOGY, APE_CODE, SCORE_DESCRIPTION, CODE_MOTIF, CODE_CONFIDENTIALITE, INFO_TRAITEMENT
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from enthic.utils.conversion import CON_APE, get_corresponding_ape_codes
from enthic.scoring.main import get_percentiles, compute_score, save_score_in_database

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


@application.route("/ontology/bundles", methods=['GET'], strict_slashes=False)
@application.route("/ontology/bundle", methods=['GET'], strict_slashes=False)
@insert_request
def ontology():
    """
    Return the ontology used to extract accountability data.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(ONTOLOGY)


@application.route("/ontology/ape", methods=['GET'], strict_slashes=False)
@insert_request
def ape():
    """
    Return all known APE codes.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(APE_CODE)


@application.route("/ontology/scores", methods=['GET'], strict_slashes=False)
@application.route("/ontology/score", methods=['GET'], strict_slashes=False)
@insert_request
def scores():
    """
    Return description of all scores computed.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(SCORE_DESCRIPTION)


@application.route("/ontology/metadata", methods=['GET'], strict_slashes=False)
@insert_request
def metadata():
    """
    Return description of INPI's metadata.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse({"CODE_MOTIF" : CODE_MOTIF,
                           "CODE_CONFIDENTIALITE" : CODE_CONFIDENTIALITE,
                           "INFO_TRAITEMENT" : INFO_TRAITEMENT})


def pre_cast_integer(probe):
    """
    A str that cannot be casted as integer is set to 0 in MySQL. This Function
    return None (NULL SQL equivalent) if not castable.

       :param probe: SQL probe to cast or not.
    """
    return str(probe) if probe.__class__ is int else probe if probe.isnumeric() is True else None


def result_array(probe, limit, ape_code=[], offset=0):
    """
    List the result of the search in the database.

       :param probe: A string to match.
       :param limit: Integer, the limit of result to return.
       :param ape_code: List of APE codes to match or None
       :param offset: Integer, offset of the select SQL request.
    """
    sql_query_select_part = "SELECT siren, denomination, ape, postal_code, town FROM identity"

    sql_query_probe_condition = '1'
    sql_arguments = {}
    if probe:
        sql_query_probe_condition = "denomination LIKE %(probe)s OR MATCH(denomination) AGAINST (%(probe)s IN NATURAL LANGUAGE MODE)"
        sql_arguments['probe'] = str(probe) + '%'
        # If probe is an interger, it might be a siren number, so we add this condition to the query
        if pre_cast_integer(probe):
            sql_query_probe_condition = "siren = %(siren)s OR " + sql_query_probe_condition
            sql_arguments['siren'] = int(probe)

    sql_query_ape_code_condition = "1"
    if len(ape_code) > 1:
        sql_query_ape_code_condition = "ape IN {}".format(tuple(ape_code))
    elif len(ape_code) == 1:
        sql_query_ape_code_condition = "ape = {}".format(ape_code[0])

    sql_query_condition = " WHERE (" + sql_query_probe_condition + ") AND (" + sql_query_ape_code_condition + ") "
    sql_query_limit_and_offset = " LIMIT {} OFFSET {};".format(limit, offset)

    with application.app_context():
        companies = fetchall(sql_query_select_part + sql_query_condition + sql_query_limit_and_offset, args=sql_arguments)
        result_count = len(companies)
        if result_count < limit:
            total_count = offset + result_count
        else:
            total_count = fetchall("SELECT COUNT(siren) FROM identity " + sql_query_condition + ";", args=sql_arguments)[0][0]
            # Sometimes, COUNT request doesn't return an exact count and we don't know why (cache or estimation maybe?)
            # This code handle the case where SQL return a count less than the real one, to be able to still request last pages
            if total_count < (result_count + offset):
                print("Error total_count({}) < (result_count({})+offset({})".format(total_count, result_count, offset))
                total_count = result_count + offset + limit
        return total_count, tuple(CompanyIdentity(*company).__dict__ for company in companies)


def get_siren(first_letters):
    """
    Get siren of companies whose denomination starts with the given first letters

        :param first_letters: A string to match companies name.

        :return: list of siren number of companies found
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


@application.route("/statistics/<string:real_ape>/<int:year>/<int:score>", methods=['GET'], strict_slashes=False)
@application.route("/statistics/<string:real_ape>/<int:year>", methods=['GET'], strict_slashes=False)
@application.route("/statistics/<string:real_ape>", methods=['GET'], strict_slashes=False)
@insert_request
def statistics(real_ape, year=None, score=None):
    """
    Return stored statistics about the given APE code as json

        :param real_ape: official APE code asked for
        :param year : year asked for
        :param score : score type asked for
    """

    result = get_percentiles(real_ape, year, score)

    if not result:
        error_msg = "No data for APE {}".format(real_ape)
        if year :
            error_msg += ", year {}".format(year)
        if score:
            error_msg += "and score '{}'({})".format(SCORE_DESCRIPTION[score], score)
        return ErrorJSONResponse(error_msg)

    return OKJSONResponse(result)


@application.route("/compute/company/<string:first_letters>/<int:year>", methods=['GET'], strict_slashes=False)
@application.route("/compute/company/<string:first_letters>/", methods=['GET'], strict_slashes=False)
@insert_request
def compute(first_letters, year=None):
    """
    Computes scores and saves them into the database.

       :param first_letters: A string to match companies name.
       :param year: year on which compute indicators. None for all available years

       :return: HTTP Response as application/json
    """
    result = []
    for siren in get_siren(first_letters):
        result += compute_score(siren[0], year)

    save_score_in_database(result)

    return OKJSONResponse(result)


@application.route("/compute/company/all/<int:offset>/<int:limit>/<int:year>", methods=['GET'], strict_slashes=False)
@application.route("/compute/company/all/<int:offset>/<int:limit>", methods=['GET'], strict_slashes=False)
@insert_request
def compute_all(offset, limit, year=None):
    """
    Computes bundle's scores and saves them into the database.

       :param offset: offset in database to compute.
       :param limit: limit of score to compute
       :param year: year on which compute indicators. None for all available years

       :return: HTTP Response as application/json
    """
    sql_args = {"limit": limit,
                "offset": offset}
    siren_to_compute = fetchall(""" SELECT siren
                                    FROM `identity`
                                    LIMIT %(limit)s
                                    OFFSET %(offset)s""",
                                    sql_args)

    result = []
    for siren in siren_to_compute:
        result += compute_score(siren[0], year)

    save_score_in_database(result)

    return OKJSONResponse(result)

@application.route("/compute/ape/<string:real_ape>/<int:year>/<int:score>", methods=['GET'], strict_slashes=False)
@application.route("/compute/ape/<string:real_ape>/<int:year>", methods=['GET'], strict_slashes=False)
@application.route("/compute/ape/<string:real_ape>", methods=['GET'], strict_slashes=False)
@insert_request
def compute_ape(real_ape, year = None, score = None):
    """
    Computes decile for each score for the given year, score and APE (including APE part of the given one) and saves them into the database.

       :param real_ape: decile will be computed for companies from this APE code.
       :param year: decile will be computed for the given year.
       :param score: decile wil be computed for the given score type (see SCORE_DESCRIPTION in ontology).

       :return: HTTP Response as application/json
    """
    # Fetch all score of a given type, and for specified economic sector (APE)
    ape_stringlist = get_corresponding_ape_codes(real_ape)
    dict_scores = {}
    sql_args = {"ape_list": tuple(ape_stringlist),
                "score": score,
                "year": year}
    sql_request = """SELECT stats_type, declaration, value
                     FROM identity
                     RIGHT JOIN annual_statistics ON annual_statistics.siren = identity.siren
                     WHERE identity.ape IN %(ape_list)s"""

    if score:
        sql_request += " AND annual_statistics.stats_type = %(score)s"
    else:
        for existing_score in SCORE_DESCRIPTION:
            dict_scores[existing_score] = {}

    if year:
        sql_request += " AND annual_statistics.declaration = %(year)s"
        for existing_score in dict_scores:
            dict_scores[existing_score][year] = []
    else:
        for existing_score in dict_scores:
            for possible_year in range(1980,2022):
                dict_scores[existing_score][possible_year] = []
    sql_request += ";"

    sql_result = fetchall(sql_request, sql_args)

    if len(sql_result) == 0:
        error_msg = "No data for APE {}".format(real_ape)
        if year :
            error_msg += ", year {}".format(year)
        if score:
            error_msg += "and score '{}'({})".format(SCORE_DESCRIPTION[score], score)
        return ErrorJSONResponse(error_msg)

    for score_line in sql_result:
        dict_scores[score_line[0]][score_line[1]].append(score_line[2])

    new_data = []
    percentiles_needed = [10, 20, 30, 40, 50, 60, 70, 80, 90]

    for k_score in dict_scores:
        for k_year in dict_scores[k_score]:
            score_values = dict_scores[k_score][k_year]
            score_values.sort()
            count = len(score_values)
            if count > 0:
                percentile_values = numpy.percentile(score_values, percentiles_needed)
                i = 0
                for percentile in percentiles_needed:
                    new_data.append({"ape": CON_APE[real_ape],
                                     "year": k_year,
                                     "score": k_score,
                                     "percentile": percentile,
                                     "value": percentile_values[i],
                                     "count": count})
                    i = i + 1

    with application.app_context():
        from enthic.database.mysql import mysql
        cur = mysql.connection.cursor()
        sql_replace_query = """REPLACE INTO `annual_ape_statistics`
            (`ape`, `declaration`, `stats_type`, `percentile`, `value`, `count`)
            VALUES (%(ape)s, %(year)s, %(score)s, %(percentile)s, %(value)s, %(count)s);"""
        values = tuple(new_data)
        cur.executemany(sql_replace_query, values)
        mysql.connection.commit()
        cur.close()

    return OKJSONResponse(new_data)

@application.route("/csv/<int:siren>", methods=['GET'], strict_slashes=False)
@insert_request
def serve_csv_file(siren):
    """
    Get all data from the given company and returns it as csv file

       :param siren: A company's siren

       :return: HTTP Response as csv file
    """

    # Get data
    sql_arguments = {"siren" : siren}
    sql_query = "SELECT * FROM `bundle` WHERE siren = %(siren)s"
    result = fetchall(sql_query, args=sql_arguments)

    # Open bytes stream
    stream = io.BytesIO()
    stream_writer = codecs.getwriter('utf-8')
    # Convert to String stream
    buffer = stream_writer(stream)
    # Write data
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(["siren", "annee", "type de comptabilite", "code compta", "valeur"])
    writer.writerows(result)

    # Send data to client
    stream.seek(0)
    return send_file(
        stream,
        mimetype="text/csv",
        attachment_filename="export.csv",
    )

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
