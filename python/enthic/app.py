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

from json import loads, load
from os.path import dirname, join
from re import compile

from enthic.company.denomination_company import DenominationCompany
from enthic.company.siren_company import SirenCompany
from enthic.decorator.check_sql_injection import check_sql_injection
from enthic.decorator.insert_request import insert_request
from enthic.ontology import ONTOLOGY
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from enthic.utils.sql_json_response import SQLJSONResponse
from flask import Flask, request
from flask_cors import CORS
from flask_mysqldb import MySQL

siren_re = compile(r"^\d{9}$")  # REGEX OF A SIREN
year_re = compile(r"^\d{4}$")  # REGEX OF A YEAR

application = Flask(__name__)
CORS(application, expose_headers='Authorization')
mysql = MySQL(application)

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
# CALCULATE SCORES RELATED DATA
with application.app_context():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT declaration, ROUND(AVG(amount))
                FROM bundle where bundle = 'DIR'
                GROUP BY declaration;""")
    sql_results_dir_year = cur.fetchall()
    cur.execute("""SELECT ROUND(AVG(amount), 2)
                FROM bundle where bundle = 'DIR';""")
    avg_dir, = cur.fetchone()
    cur.close()


@application.route("/company/siren/<siren>/<year>", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request(mysql, request)
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
    if siren_re.match(siren):
        if year_re.match(year):

            return SirenCompany(mysql, siren, year, dict(sql_results_dir_year))
        else:
            return ErrorJSONResponse("YEAR for is wrong, must match ^\d{4}$.")
    else:
        return ErrorJSONResponse("SIREN for is wrong, must match ^\d{9}$.")


@application.route("/company/siren/<siren>", methods=['GET'], strict_slashes=False)
@check_sql_injection
@insert_request(mysql, request)
def company_siren(siren):
    """
    Retrieve company information by SIREN. Path is /company/siren/<siren> GET
    method only and no strict slash.

       :param siren: SIREN identification, must be an 9 character long,
          numeric only.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    if siren_re.match(siren):
        return SirenCompany(mysql, siren, None, avg_dir)
    else:
        return ErrorJSONResponse("SIREN for is wrong, must match ^\d{9}$.")


@application.route("/company/denomination/<denomination>", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request(mysql, request)
def company_denomination(denomination):
    """
    Retrieve company information by company denomination. Path is
    /company/denomination/<denomination> GET method only and no strict slash.

       :param denomination: String, denomination of the company.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return DenominationCompany(mysql, denomination, None, avg_dir)


@application.route("/company/denomination/<denomination>/<year>", methods=['GET'],
                   strict_slashes=False)
@check_sql_injection
@insert_request(mysql, request)
def company_denomination_year(denomination, year):
    """
    Retrieve company information for a given year by company denomination. Path
    is /company/denomination/<denomination> GET method only and no strict slash.

       :param denomination: String, denomination of the company.
       :param year: Year of results to return, default is None.
       :return: HTTP Response as application/json. Contain all known information.
    """
    if year_re.match(year):
        return DenominationCompany(mysql, denomination, year, dict(sql_results_dir_year))
    else:
        return ErrorJSONResponse("YEAR for is wrong, must match ^\d{4}$.")


@application.route("/company/ontology", methods=['GET'], strict_slashes=False)
def ontology():
    """
    Return the ontology used to extract accountability data.

       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse(ONTOLOGY)


@application.route("/company/search", methods=['POST'], strict_slashes=False)
@check_sql_injection
@insert_request(mysql, request)
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
        elif int(json_data["limit"]) > 1000:
            return ErrorJSONResponse("Value limit is 1000 maximum.")
        ########################################################################
        # CORRECT JSON
        else:
            return SQLJSONResponse(mysql, """SELECT siren, denomination
                                    FROM identity WHERE siren like '%s'
                                    OR denomination like '%s' LIMIT %s;""",
                                   json_data["probe"] + "%",
                                   json_data["probe"] + "%",
                                   json_data["limit"])
    ############################################################################
    # WRONG JSON KEY
    except KeyError as error:
        return ErrorJSONResponse(
            "Unhandled JSON key resulting the following error: {}".format(
                str(error)
            )
        )


@application.route('/<path:path>', strict_slashes=False)
@insert_request(mysql, request)
def static_proxy(path):
    """
    Serve the static files, like the Swagger definition page and the 404.

       :param path: / Base path of the host.
       :return: The resource present at the path.
    """
    return application.send_static_file(path)


@application.route("/", strict_slashes=False)
@insert_request(mysql, request)
def index():
    """
    Serve the index.html at the base path.

       :return: The static index.html and a return code 200.
    """
    return application.send_static_file("index.html"), 200


@application.errorhandler(404)
@insert_request(mysql, request)
def page_not_found(error):
    """
    Page not found and logging.

       :param error: Error message to be logged.
       :return: The HTML 404 page.
    """
    application.logger.info(error)
    return application.send_static_file('404.html'), 404


@application.errorhandler(500)
@insert_request(mysql, request)
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
