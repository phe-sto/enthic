# -*- coding: utf-8 -*-
"""
==================================
Test the flask server and it's API
==================================

Coding Rules:

- Snake case for variables.
- Only argument is configuration file.
- No output or print, just log and files.
"""
from json import loads, dumps

import pytest
from enthic.app import mysql
from enthic.utils.error_json_response import ErrorJSONResponse
from enthic.utils.json_response import JSONResponse
from enthic.utils.ok_json_response import OKJSONResponse
from enthic.utils.sql_json_response import SQLJSONResponse, \
    SQLJSONResponseException
from requests import get, post


def test_ok_json_response():
    """
    Test OKJSONResponse with wrong object.
    """
    with pytest.raises(TypeError):
        OKJSONResponse({2})


def test_error_json_response():
    """
    Test ErrorJSONResponse with wrong object.
    """
    with pytest.raises(TypeError):
        ErrorJSONResponse({2})


def test_json_response():
    """
    Test JSONResponse with wrong object.
    """
    with pytest.raises(TypeError):
        JSONResponse({2})


@pytest.mark.parametrize("sql_request", ("INSERT (1, 2, 3) INTO bundle;",
                                         "UPDATE bundle SET siren = '' WHERE siren = '999';",
                                         "DROP bundle;"))
def test_sql_json_response_wrong_statement(sql_request):
    """
    Test SQLJSONResponse with wrong INSERT and UPDATE.
       :param sql_request: SQL requests to test.
    """
    with pytest.raises(SQLJSONResponseException):
        SQLJSONResponse(mysql, sql_request)


@pytest.fixture()
def host():
    """
    Fixture of the API host.
       :return: String representing the host address.
    """
    return "127.0.0.1:5000"


@pytest.mark.parametrize("siren", ("389718115",
                                   "410660492",
                                   "999999999"))  # DOES NOT EXIST
def test_siren(host, siren):
    """
    Test the /company/siren endpoint. Should return a JSON.
       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + siren)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren,year", (("389718115", 2019),
                                        ("410660492", 2019),
                                        ("999999999", 2019)))  # DOES NOT EXIST
def test_siren_year(host, siren, year):
    """
    Test the /company/siren/year endpoint. Should return a JSON with
       information for a given year.
       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + siren + "/" + str(year))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren,year", (("389718115", 20199),
                                        ("410660492", "2019f"),
                                        ("999999999", 201)))  # DOES NOT EXIST
def test_siren_wrong_year(host, siren, year):
    """
    Test the /company/siren/year endpoint. Should return a JSON with
       information a wrong year.
       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + siren + "/" + str(year))
    assert response.status_code == 400, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("siren", ("38971811555",  # 11 CHARACTERS
                                   "41066 492",  # 9 CHARACTERS WITH WHITESPACE
                                   "41066d492",  # NON NUMERIC CHARACTER
                                   "9999999"))  # 7 CHARACTERS
def test_wrong_siren(host, siren):
    """
    Test the /company/siren endpoint with wrong SIREN. Should return a JSON.
       :param host: Fixture of the API host.
       :param siren: Parametrise fixture of a SIREN.
    """
    response = get("http://" + host + "/company/siren/" + siren)
    assert response.status_code == 400
    assert loads(response.text)["error"] != "", "NO ERROR MESSAGE OR EMPTY"


@pytest.mark.parametrize("denomination", ("RCV PEINTURE",
                                          "RESEAUX ELECTRIQUE & INFORMATIQUE",
                                          "TOTO SASU"))  # DOES NOT EXIST
def test_denomination(host, denomination):
    """
    Test the /company/denomination endpoint. Should return a
       JSON.
       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
    """
    response = get("http://" + host + "/company/denomination/" + denomination)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("denomination,year", (("RCV PEINTURE", 2019),
                                               ("RESEAUX ELECTRIQUE & INFORMATIQUE", 2019),
                                               ("TOTO SASU", 2019)))  # DOES NOT EXIST
def test_denomination_year(host, denomination, year):
    """
    Test the /company/denomination/year endpoint. Should return a
       JSON.
       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
       :param year: Parametrise fixture of the year to return.
    """
    response = get("http://" + host + "/company/denomination/" + denomination + "/" + str(year))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("denomination,year", (("RCV PEINTURE", 209),
                                               ("RESEAUX ELECTRIQUE & INFORMATIQUE", '201s9'),
                                               ("TOTO SASU", 20189)))  # DOES NOT EXIST
def test_denomination_wrong_year(host, denomination, year):
    """
    Test the /company/denomination/year endpoint. Should return a
       JSON. Tested with a wrong year.
       :param host: Fixture of the API host.
       :param denomination: Parametrise fixture of a company official name.
       :param year: Parametrise fixture of the year to return.
    """
    response = get("http://" + host + "/company/denomination/" + denomination + "/" + str(year))
    assert response.status_code == 400, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


def test_ontology(host):
    """
    Test the GET of the ontology on the URL /company/ontology.
       :param host: Fixture of the API host.
    """
    response = get("http://" + host + "/company/ontology")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("probe,limit", (("toto", 100),
                                         ("toto", 1),
                                         ("toto et Michel", 100),
                                         )
                         )
def test_search(host, probe, limit):
    """
    Test the /company/search endpoint. Should return a JSON.
       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
    """
    response = post("http://" + host + "/company/search/", dumps({"probe": probe, "limit": limit}))
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text) is not None, "NOT RETURNING A JSON"


@pytest.mark.parametrize("sql_request_1,sql_request_2", (("drop database toto;", 100),
                                                         ("drop table enthic;", 1),
                                                         ("toto et Michel", "select * from enthic;"),
                                                         ("toto et Michel", "update toto set siren = '000000';"),
                                                         ("toto et Michel", "insert ('toto') into pouet"),
                                                         ("select * from enthic;", 100),
                                                         # SAME UPPER CASE
                                                         ("DROP DATABASE TOTO;", 100),
                                                         ("DROP TABLE ENTHIC;", 1),
                                                         ("TOTO ET MICHEL", "SELECT * FROM ENTHIC;"),
                                                         ("TOTO ET MICHEL", "UPDATE TOTO SET SIREN = '000000';"),
                                                         ("TOTO ET MICHEL", "INSERT ('TOTO') INTO POUET"),
                                                         ("SELECT * FROM ENTHIC;", 100)
                                                         )
                         )
def test_check_sql_injection_body(host, sql_request_1, sql_request_2):
    """
    Test the check_sql_injection decorator, avoiding SQL injection from request
       body.
       :param host: Fixture of the API host.
       :param sql_request_1: Parametrize fixture of a possible SQL request.
       :param sql_request_2: Parametrize fixture of a possible SQL request.
    """
    response = post("http://" + host + "/company/search/", dumps({"probe": sql_request_1, "limit": sql_request_2}))
    assert response.status_code == 500, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("sql_request", (("drop database toto;"),
                                         ("drop table enthic;"),
                                         ("select * from enthic;"),
                                         ("update toto set siren = '000000';"),
                                         ("insert ('toto') into pouet"),
                                         ("select * from enthic;"),
                                         # SAME UPPER CASE
                                         ("DROP DATABASE TOTO;"),
                                         ("DROP TABLE ENTHIC;"),
                                         ("SELECT * FROM ENTHIC;"),
                                         ("UPDATE TOTO SET SIREN = '000000';"),
                                         ("INSERT ('TOTO') INTO POUET"),
                                         ("SELECT * FROM ENTHIC;"),
                                         )
                         )
def test_check_sql_injection_path(host, sql_request):
    """
    Test the check_sql_injection decorator, avoiding SQL injection from request
       path.
       :param host: Fixture of the API host.
       :param sql_request_1: Parametrize fixture of a possible SQL request.
    """
    response = get("http://" + host + "/company/denomination/" + sql_request)
    assert response.status_code == 500, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("probe,limit", (("toto", "pouet"),
                                         (2, 1),
                                         (2, "toto"),
                                         ("toto", 10000),
                                         )
                         )
def test_wrong_value_search(host, probe, limit):
    """
    Test the /company/search endpoint posting a wrong JSON values. Should return
       a JSON.
       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
    """
    response = post("http://" + host + "/company/search/", dumps({"probe": probe, "limit": limit}))
    assert response.status_code == 400
    assert loads(response.text)["error"] != "", "NO ERROR MESSAGE OR EMPTY"


def test_wrong_key_search(host):
    """
    Test the /company/search endpoint posting a wrong JSON keys. Should return a
       JSON.
       :param host: Fixture of the API host.
       :param probe: Parametrize fixture of the string to search.
       :param limit: Parametrize fixture of limit of result to return.
    """
    response = post("http://" + host + "/company/search/", dumps({"toto": "pouet", "limit": 2}))
    assert response.status_code == 400
    assert loads(response.text)["error"] != "", "NO ERROR MESSAGE OR EMPTY"


@pytest.mark.parametrize("page", ("/404.html",
                                  "/index.html",
                                  "/500.html",))
def test_html_pages(host, page):
    """
    Test static html page, such as swagger description page 500 and 404.
       :param host: Fixture of the API host.
       :param page: Parametrise fixture of a page to get.
    """
    response = get("http://" + host + page)
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"


@pytest.mark.parametrize("page", ("/4040.html",
                                  "/indexx.html",
                                  "/5005.html",))
def test_404(host, page):
    """
    Test unknown URL.
       :param host: Fixture of the API host.
       :param page: Parametrise fixture of a page to get.
    """
    response = get("http://" + host + page)
    assert response.status_code == 404, "WRONG HTTP RETURN CODE"


def test_swagger_json(host):
    """
    Test static swagger.json.
       :param host: Fixture of the API host.
    """
    response = get("http://" + host + "/swagger.json")
    assert response.status_code == 200, "WRONG HTTP RETURN CODE"
    assert loads(response.text)["swagger"] == "2.0", \
        "NOT A SWAGGER 2.0 JSON DESCRIPTION"
