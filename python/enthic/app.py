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

from inspect import stack
from json import loads, load
from os.path import dirname, join

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
from enthic.database.fetch import fetchall, fetchone
from enthic.decorator.check_sql_injection import check_sql_injection
from enthic.decorator.insert_request import insert_request
from enthic.ontology import ONTOLOGY
from enthic.result.result import result
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.not_found_response import NotFoundJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from flask import Flask, request
from flask_cors import CORS

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

################################################################################
# IN ORDER NOT TO CONNECT DATABASE BELOW IF EXECUTED DURING SPHINX IMPORT
try:
    setup = stack()[6].filename.endswith("autodoc/importer.py")
except IndexError:
    setup = False
################################################################################
# CALCULATE SCORES RELATED DATA ONLY IF NOT BUILDING/INSTALLING

with application.app_context():
    from enthic.database.mysql import mysql

    if setup is False:
        cursor = mysql.connection.cursor()
        cursor.execute("""SELECT declaration, ROUND(AVG(amount))
                    FROM bundle where bundle = 'DIR'
                    GROUP BY declaration;""")
        result.yearly_avg_dir = cursor.fetchall()
        cursor.close()


@application.route("/company/siren/<siren>/<year>", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request
def company_siren_year(siren, year):
    """
    Retrieve company information by SIREN for a given year. Path is
    /company/siren/<siren> GET method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.

       :param year: Year of results to return, default is None.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN or YEAR wrongly formatted.
    """
    return YearSirenCompany(siren, year)


@application.route("/company/siren/<siren>/average", methods=['GET'], strict_slashes=False)
@check_sql_injection
@insert_request
def company_siren_average(siren):
    """
    Retrieve company information by SIREN, calculation of the years average.
    Path is /company/siren/<siren> GET method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    return AverageSirenCompany(siren)


@application.route("/company/siren/<siren>", methods=['GET'], strict_slashes=False)
@check_sql_injection
@insert_request
def company_siren(siren):
    """
    Retrieve company information by SIREN, calculation of all years. Path is
    /company/siren/<siren> GET method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    return AllSirenCompany(siren)


@application.route("/company/denomination/<denomination>/average", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request
def company_denomination_average(denomination):
    """
    Retrieve company information by company denomination of the years average.
    Path is /company/denomination/<denomination> GET method only and no strict
    slash.

       :param denomination: String, denomination of the company.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return AverageDenominationCompany(denomination)


@application.route("/company/denomination/<denomination>", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request
def company_denomination(denomination):
    """
    Retrieve company information by company denomination, calculation of all
    years. Path is /company/denomination/<denomination> GET method only and no strict slash.

       :param denomination: String, denomination of the company.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return AllDenominationCompany(denomination)


@application.route("/company/denomination/<denomination>/<year>", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request
def company_denomination_year(denomination, year):
    """
    Retrieve company information for a given year by company denomination. Path
    is /company/denomination/<denomination> GET method only and no strict slash.

       :param denomination: String, denomination of the company.
       :param year: Year of results to return, default is None.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return YearDenominationCompany(denomination, year)


@application.route("/company/ontology", methods=['GET'], strict_slashes=False)
def ontology():
    """
    Return the ontology used to extract accountability data.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(ONTOLOGY)


def result_array(probe, limit, offset=0):
    """
    List the result of the search in the database.

       :param probe: A string to match.
       :param limit: Integer, the limit of result to return.
       :param offset: Integer, offset of the select SQL request.
    """
    companies = list(fetchall("""SELECT siren, denomination, ape, postal_code, town, 
                    accountability, devise
                    FROM identity WHERE siren LIKE "%s%%"
                    OR denomination LIKE "%s%%"
                    OR MATCH(denomination) AGAINST ("%s%%" IN NATURAL LANGUAGE MODE)
                    LIMIT %d OFFSET %d;""" % (probe, probe, probe, limit, offset)))
    return tuple([CompanyIdentity(*company).__dict__ for company in companies])


@application.route("/company/search", methods=['POST'], strict_slashes=False)
@check_sql_injection
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
                json_data["probe"].__class__ is not str:
            return ErrorJSONResponse(
                "Value limit must be a string and limit an integer."
            )
        elif json_data["limit"].__class__ is not int:
            return ErrorJSONResponse("Value limit must be an integer.")
        elif json_data["probe"].__class__ is not str:
            return ErrorJSONResponse("Value probe must be a string.")
        ########################################################################
        # WRONG LIMIT
        elif json_data["limit"] > 10000:
            return ErrorJSONResponse("Value limit is 1000 maximum.")
        ########################################################################
        # CORRECT JSON
        else:
            results = result_array(json_data["probe"], json_data["limit"])
            return OKJSONResponse({
                "@context": "http://www.w3.org/ns/hydra/context.jsonld",
                "@id": request.url,
                "@type": "Collection",
                "totalItems": results.__len__(),
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
@check_sql_injection
@insert_request
def page_search():
    """
    Return a JSON formatted as page. Try to implement the Hydra
    hypermedia-driven Web APIs https://www.markus-lanthaler.com/hydra/.
    """

    page = int(request.args.get('page', '1')) - 1  #  TO COUNT
    per_page = int(request.args.get('per_page', '30'))
    probe = request.args.get('probe', "")
    results = result_array(probe, per_page, offset=page * per_page)
    count = fetchone("""SELECT COUNT(*)
                        FROM identity WHERE siren LIKE "%s%%"
                        OR denomination LIKE "%s%%"
                        OR MATCH(denomination) AGAINST ("%s%%" IN NATURAL LANGUAGE MODE)""" % (
        probe, probe, probe))
    if count < page * per_page:
        return NotFoundJSONResponse()
    ############################################################################
    # OBJECT STORING RESPONSE
    obj = {"@context": "http://www.w3.org/ns/hydra/context.jsonld",
           "@id": request.url,
           "@type": "Collection",
           "totalItems": count, "view": {
            "@id": request.full_path,
            "@type": "PartialCollectionView",
            "first": '%s?page=1&per_page=%d&probe=%s' % (request.path,
                                                         per_page, probe),
            "last": '%s?page=%d&per_page=%d&probe=%s' % (request.path,
                                                         count / per_page + 1,
                                                         per_page,
                                                         probe)},
           "member": results
           }
    ############################################################################
    # OBJECT VIEW
    if page == 0:
        obj["view"]['previous'] = ''
    else:
        obj["view"]['previous'] = '%s?page=%d&per_page=%d&probe=%s' % (request.path,
                                                                       page,
                                                                       per_page,
                                                                       probe)
    # MAKE NEXT URL
    if page * per_page + per_page > count:
        obj["view"]["next"] = ''
    elif page + 1 < int(count / per_page):
        obj["view"]["next"] = '%s?page=%d&per_page=%d&probe=%s' % (request.path,
                                                                   page + 2,
                                                                   per_page,
                                                                   probe)
    else:
        obj["view"]["next"] = '%s?page=%d&per_page=%d&probe=%s' % (request.path,
                                                                   page + 2,
                                                                   per_page,
                                                                   probe)
    return OKJSONResponse(obj)


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
