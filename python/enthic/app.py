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

from enthic.decorator.check_sql_injection import check_sql_injection
from enthic.decorator.insert_request import insert_request
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from enthic.utils.sql_json_response import SQLJSONResponse
from flask import Flask, request
from flask_mysqldb import MySQL

siren_re = compile(r"^\d{9}$")  # REGEX OF A SIREN
year_re = compile(r"^\d{4}$")  # REGEX OF A YEAR

application = Flask(__name__)
mysql = MySQL(application)

############################################################################
# CONFIGURE applicationLICATION
with open(join(dirname(__file__), "configuration.json")) as json_configuration_file:
    config = load(json_configuration_file)
application._static_folder = "./static/"
application.config['MYSQL_HOST'] = config["mySQL"]["enthic"]["host"]
application.config['MYSQL_USER'] = config["mySQL"]["enthic"]["user"]
application.config['MYSQL_PASSWORD'] = config["mySQL"]["enthic"]["password"]
application.config['MYSQL_DB'] = 'enthic'


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
            return SQLJSONResponse(mysql, """SELECT bundle, amount
                                    FROM identity INNER JOIN bundle
                                    ON bundle.siren = identity.siren
                                    WHERE identity.siren = '%s' 
                                    AND declaration = %s;""", siren, year)
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
        return SQLJSONResponse(mysql, """SELECT bundle, CONVERT(AVG(amount), UNSIGNED INTEGER)
                                FROM identity INNER JOIN bundle
                                ON bundle.siren = identity.siren
                                WHERE identity.siren = '%s'
                                GROUP BY bundle.bundle;""", siren)
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
    return SQLJSONResponse(mysql, """SELECT bundle, CONVERT(AVG(amount), UNSIGNED INTEGER)
                                FROM identity INNER JOIN bundle
                                ON bundle.siren = identity.siren
                                WHERE identity.denomination = '%s'
                                GROUP BY bundle.bundle;""", denomination)


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
        return SQLJSONResponse(mysql, """SELECT bundle, amount
                                FROM identity INNER JOIN bundle
                                ON bundle.siren = identity.siren
                                WHERE identity.denomination = '%s'
                                AND declaration = %s;""",
                               denomination, year)
    else:
        return ErrorJSONResponse("YEAR for is wrong, must match ^\d{4}$.")


@application.route("/company/ontology", methods=['GET'], strict_slashes=False)
def ontology():
    """
    Return the ontology used to extract accountability data.
       :return: HTTP Response as application/json. the ontology as JSON.
    """
    return OKJSONResponse({"accounting": [{"C":
        {
            "description": "Comptes individuels clients et fournisseurs. A tout moment, vous pouvez ainsi connaître les soldes des comptes souhaités, vos créances client par client et/ou vos dettes fournisseur par fournisseur. En terme de gestion de l’entreprise, la comptabilité complète donne des informations importantes.",
            "code": [
                {"FY": "Salaires et traitements"},
                {"DI": "Résultat de l’exercice (bénéfice ou perte)"},
                {"HI": "Résultat exceptionnel"},
                {
                    "HJ": "Participation des salariés aux résultats de l’entreprise"},
                {"HK": "Impôts sur les bénéfices"},
                {"HM": "Total des charges"},
                {"FJ": "Chiffre d’affaires nets"}

            ]}},
        {"S":
            {
                "description": "Pour permettre aux petites entreprises de se développer, un régime de comptabilité simplifiée a été mis en place afin d'alléger leurs obligations comptables et le coût qu'elles impliquent",
                "code": [
                    {"FY": "Salaires et traitements"},
                    {"HI": "Résultat exceptionnel"},
                    {"290": "Produits exceptionnels"},
                    {
                        "HJ": "Participation des salariés aux résultats de l’entreprise"},
                    {"HK": "Impôts sur les bénéfices"},
                    {"310": "Bénéfice ou perte"},
                    {"FJ": "Chiffre d’affaires nets"}
                ]}}]})


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
            return ErrorJSONResponse("Value limit must 1000 maximum.")
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