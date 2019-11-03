# -*- coding: utf-8 -*-

from re import compile

from enthic.utils.ok_json_response import OKJSONResponse
from enthic.utils.sql_json_response import SQLJSONResponse
from flask import Flask, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)
app._static_folder = "./static/"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'enthic'
mysql = MySQL(app)
siren_re = compile(r"^\d{9}$")  # REGEX OF A SIREN


@app.route("/company/siren/<siren>", methods=['GET'], strict_slashes=False)
def company_siren(siren):
    """
    Retrieve company information by SIREN.
       :param siren: SIREN identification, must be an 9 character long,
          numeric only.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    if siren_re.match(siren):
        return SQLJSONResponse(mysql, """SELECT bundle, amount
                                FROM identity INNER JOIN bundle
                                ON bundle.siren = identity.siren
                                WHERE identity.siren = "{0}";""".format(siren),
                               "bundle", "amount")
    else:
        return OKJSONResponse({"error": "SIREN for is wrong, must match ^\d{9}$."})


@app.route("/company/denomination/<denomination>", methods=['GET'], strict_slashes=False)
def company_denomination(denomination):
    """
    Retrieve company information by company denomination.
       :param denomination: String, denomination of the company.
       :return: HTTP Response as application/json. Contain all known information.
    """
    return SQLJSONResponse(mysql, """SELECT bundle, amount
                            FROM identity INNER JOIN bundle
                            ON bundle.siren = identity.siren
                            WHERE identity.denomination = "{0}";""".format(denomination),
                           "bundle", "amount")


@app.route("/company/search/<probe>", methods=['GET'], strict_slashes=False)
def search(probe):
    """
    Search companies by SIREN or denomination. Limited to 1000 results.
       :param probe: Supposed to be SIREN or a denomination.
       :return: HTTP Response as application/json. Contain all known information
          on that company of an error message if SIREN wrongly formatted.
    """
    return SQLJSONResponse(mysql, """SELECT denomination, bundle.siren
                            FROM identity INNER JOIN bundle
                            ON bundle.siren = identity.siren
                            WHERE identity.siren like "{0}%"
                            OR denomination like "{0}%" LIMIT 1000;""".format(probe),
                           "denomination", "siren")


@app.route('/<path:path>', strict_slashes=False)
def static_proxy(path):
    """
    Serve the static files, like the Swagger definition page and the 404.
       :param path: / Base path of the host.
       :return: The resource present at the path.
    """
    return app.send_static_file(path)


@app.errorhandler(404)
def page_not_found(error):
    """
    Page not found redirection and logging.
       :param error: Error message to be logged.
       :return: The HTML 404 page.
    """
    app.logger.error(error)
    return redirect('404.html', 404)


def main():
    """
    Start app.
    """
    app.run(debug=True)


if __name__ == "__main__":
    """
    Only executed as script not at import.
    """
    main()
