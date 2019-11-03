# -*- coding: utf-8 -*-

from re import compile

from enthic.utils.ok_json_response import OKJSONResponse
from enthic.utils.sql_json_response import SQLJSONResponse
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app._static_folder = "./static"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'enthic'
mysql = MySQL(app)
siren_re = compile(r"^\d{9}$")  # REGEX OF A SIREN


@app.route("/company/siren/<siren>", methods=['GET'])
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


@app.route("/company/denomination/<denomination>", methods=['GET'])
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


@app.route("/company/search/<probe>", methods=['GET'])
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




@app.route("/swagger")
def swagger():
    return app.send_static_file('swagger/index.html')


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    app.run(debug=True)
